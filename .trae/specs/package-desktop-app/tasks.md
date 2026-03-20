# 任务列表 (Tasks)

- [ ] Task 1: 重新在本地构建 macOS DMG
  - [ ] SubTask 1.1: 确保前端已最新编译（`npm run build`）
  - [ ] SubTask 1.2: 执行 `npx tauri build --bundles dmg` 构建 macOS 安装包
  - [ ] SubTask 1.3: 确认 DMG 产物路径并向用户汇报

- [ ] Task 2: 配置 Windows/macOS GitHub Actions 自动化打包链路
  - [ ] SubTask 2.1: 创建 `.github/workflows` 目录
  - [ ] SubTask 2.2: 编写 `tauri-build.yml` 文件，配置 Node, Rust 及 Tauri 构建环境，分别在 `windows-latest` 和 `macos-latest` 上执行
  - [ ] SubTask 2.3: 配置打包产物的上传步骤 (Upload Artifacts / Release)
