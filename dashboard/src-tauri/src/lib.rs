use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      let astrbot_root = app
        .path()
        .app_data_dir()
        .ok()
        .unwrap_or(std::env::temp_dir())
        .join(".astrbot");
      let astrbot_root_string = astrbot_root.to_string_lossy().to_string();

      let sidecar_command = app
        .shell()
        .sidecar("twopixel-backend")
        .map_err(|e| format!("create backend sidecar failed: {e}"))?
        .env("ASTRBOT_DESKTOP_CLIENT", "1")
        .env("ASTRBOT_ROOT", &astrbot_root_string);

      let (mut rx, mut _child) = sidecar_command
        .spawn()
        .map_err(|e| format!("spawn backend sidecar failed: {e}"))?;

      tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
          if let CommandEvent::Stdout(line) = event {
            println!("backend: {}", String::from_utf8_lossy(&line));
          } else if let CommandEvent::Stderr(line) = event {
            eprintln!("backend error: {}", String::from_utf8_lossy(&line));
          }
        }
      });

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
