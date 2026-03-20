# 完整桌面端一体包构建规范 (Full Desktop Bundle Spec)

## 为什么 (Why)
目前的 Tauri 安装包仅包含了前端 UI 壳，不包含 Python 运行时及后端核心逻辑（原 AstrBot 引擎），导致小白用户下载安装后无法真正实现“开箱即用”。我们需要将 Python 解释器、项目依赖及后端启动逻辑完全打包进桌面客户端，并彻底消除所有用户可见的“AstrBot”字样，将其统一替换为“TwoPixel”，以实现商业化交付。

## 改动内容 (What Changes)
- **引入 Tauri Sidecar 机制**：将 Python 后端（打包为单文件可执行文件或便携版环境）作为 `externalBin` 嵌入 Tauri。
- **Python 后端打包**：使用 PyInstaller 将后端代码打包成独立可执行文件，消除对宿主机 Python 环境的依赖。
- **品牌白标化 (White-labeling)**：全局搜索并替换后端启动日志、报错信息、默认配置名中的 `AstrBot` 为 `TwoPixel`（确保不破坏代码级别的内部依赖，仅修改展示层）。
- **进程生命周期绑定**：在 Tauri Rust 入口中，随着主窗口的启动自动拉起后端服务，并在应用关闭时优雅杀掉后端进程。

## 影响范围 (Impact)
- 桌面端打包配置：`tauri.conf.json`、`src-tauri/src/main.rs`。
- 后端打包配置：新增 `build.spec` 或打包脚本。
- 品牌感知层：所有对外的日志和报错提示。

## 新增需求 (ADDED Requirements)
### 需求：免环境的独立桌面包
系统 SHALL 将后端服务及其运行环境完全封装入客户端安装包内，用户无需安装 Python 或配置环境变量。

#### 场景：小白用户首次安装运行
- **WHEN** 用户双击打开 TwoPixel 桌面应用。
- **THEN** 应用底层自动在后台启动内置的 Python API 服务，前端成功连接并渲染数据，全程不提示“Python is not installed”。

### 需求：全品牌覆盖 (White-labeling)
系统对用户展示的所有文案、日志、进程名称 SHALL 仅使用“TwoPixel”。

#### 场景：应用启动或报错
- **WHEN** 应用在终端输出日志或前端弹出系统错误。
- **THEN** 绝对不能出现 `AstrBot` 字样。
