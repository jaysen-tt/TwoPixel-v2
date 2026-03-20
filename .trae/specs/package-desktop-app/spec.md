# 桌面端应用打包规范 (Desktop App Packaging Spec)

## 为什么 (Why)
用户需要在 macOS 和 Windows 上测试桌面客户端应用。由于在 macOS 环境下无法直接通过 Tauri 构建出 Windows 的标准安装包（如 `.msi` 或 `setup.exe`），我们需要在本地重新构建一次 macOS 的 `.dmg` 安装包供用户立即测试，同时引入自动化构建方案（GitHub Actions）来解决 Windows 环境打包问题，实现双端安装包的自动化输出。

## 改动内容 (What Changes)
- 重新在本地执行 Tauri 构建命令，生成 macOS `.dmg` 文件。
- 新增 GitHub Actions 工作流配置文件，在 GitHub 远程环境自动执行 Windows 和 macOS 的 Tauri 编译与打包。
- 工作流将配置为在推送标签或特定分支时触发，自动生成并上传对应的 `setup.exe` / `.msi` 以及 `.dmg` 产物。

## 影响范围 (Impact)
- 受影响的功能：桌面端部署流程。
- 受影响的代码：新增 `.github/workflows/tauri-build.yml` 文件。

## 新增需求 (ADDED Requirements)
### 需求：自动化打包工作流
系统应当提供一个自动化的方式来构建全平台安装包。

#### 场景：触发远程构建
- **WHEN** 开发者向仓库推送特定分支或 Tag。
- **THEN** GitHub Actions 应该分别在 `windows-latest` 和 `macos-latest` 环境下执行 Tauri 构建，并将生成的安装包作为 Release 附件或 Artifacts 输出。
