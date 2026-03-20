# 任务列表 (Tasks)

- [x] Task 1: 品牌文案彻底清理 (White-labeling)
  - [x] SubTask 1.1: 搜索 `main.py` 和核心启动文件中的 `AstrBot` 启动日志，将其替换为 `TwoPixel`。
  - [x] SubTask 1.2: 检查默认配置文件生成的占位符或报错提示，将对外展示的 `AstrBot` 替换掉。

- [x] Task 2: 后端独立可执行文件构建 (PyInstaller)
  - [x] SubTask 2.1: 在项目中引入 `pyinstaller`，编写 `twopixel_backend.spec` 打包配置。
  - [x] SubTask 2.2: 解决静态资源（如 `data/` 目录默认结构）在打包后的路径问题。
  - [x] SubTask 2.3: 尝试在本地构建出单文件可执行后端 `twopixel-backend-mac` (或 .exe)。

- [x] Task 3: 配置 Tauri Sidecar
  - [x] SubTask 3.1: 修改 `tauri.conf.json`，在 `bundle.externalBin` 中注册 `twopixel-backend`。
  - [x] SubTask 3.2: 编写 `src-tauri/src/lib.rs` 启动逻辑，在应用启动时拉起 `twopixel-backend` 子进程，并处理进程退出时的销毁。

- [x] Task 4: 端到端联调打包
  - [x] SubTask 4.1: 执行 `npx tauri build`，验证打包出的新版 DMG 体积是否符合预期（预期应包含后端体积，可能在百MB以上）。
  - [x] SubTask 4.2: 安装并运行新版 DMG，断开外部 Python 环境，验证应用能否独立正常运行。
