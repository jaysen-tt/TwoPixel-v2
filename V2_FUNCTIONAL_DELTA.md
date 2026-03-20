# TwoPixel V2 功能差异记录（相对原始 AstrBot）

本文件用于两类场景：
- AGPL 合规对外说明（修改点清单）
- 对内/对外宣传素材沉淀（功能演进）

## 已落地功能

### 1) 品牌与产品化外显
- CLI 与启动文案替换为 TwoPixel 品牌。
- WebUI 启动日志与帮助页版本文案改为 TwoPixel。
- 聊天侧边栏底部新增用户资料入口，支持昵称与头像编辑。

### 2) 工具执行能力增强
- 启用本地工具运行时（`computer_use_runtime=local`）与低门槛执行策略。
- 接入 MCP 文件系统服务，支持读写工作目录文件。
- 增加 shell 危险命令拦截策略，降低高风险误操作。

### 3) 账号体系升级（Supabase 面向 V2）
- 登录支持 Supabase 邮箱密码直连校验。
- 新增注册接口与前端注册入口（邮箱 + 密码）。
- 登录后同步保存 Supabase access/refresh token（用于后续服务联动）。

### 4) 长期记忆增强（持久化）
- 从进程内会话记忆升级为磁盘持久化：
  - `data/twopixel_memory/sessions`
  - `data/twopixel_memory/daily`
  - `data/twopixel_memory/durable`
- 用户偏好自动提取与长期保存（显式“记住”与偏好表达）。

### 5) 记忆压缩总结
- 会话超限时执行压缩总结，减少上下文膨胀。
- 压缩结果同时写入：
  - 每日日志
  - compaction 结构化记录

### 6) 记忆蒸馏 v1（结构化）
- 新增蒸馏记忆存储层：`data/twopixel_memory/distilled`
- 单条记录结构：
  - `exchange_core`
  - `specific_context`
  - `thematic_room_assignments`
  - `files_touched`
- 请求前检索注入：
  - 基于当前用户 query 对蒸馏记忆召回 top-k
  - 将召回结果注入 system prompt（与 durable memory 并行）

### 7) 分级多 Agent 策略
- 开启 `subagent_orchestrator`。
- 主路由策略：
  - 简单任务主代理直接处理
  - 复杂任务委派 `transfer_to_*`
- 预置子代理：
  - `planner`
  - `executor`

### 8) 轻量心跳（Heartbeat）
- 新增低打扰心跳能力（基于 cron active_agent）：
  - `every_minutes`
  - `prompt`
  - `target`（`last` / `none`）
  - `active_hours`
  - `ack_max_chars`
- 支持 `HEARTBEAT_OK` 抑制：无事时不写入对话历史，不打扰用户。
- 每个会话自动维护单一 heartbeat 任务，避免重复任务膨胀。
- 在 Cron 页面展示 heartbeat 最近状态与触发时间，便于运营观察。

## 配置新增项（关键）

### `provider_ltm_settings.distillation`
- `enable`
- `max_records`
- `retrieval_top_k`
- `min_score`

### `provider_ltm_settings.heartbeat`
- `enable`
- `every_minutes`
- `prompt`
- `ack_max_chars`
- `active_hours.enable/start/end/timezone`

## 说明

- 本记录聚焦“功能性差异”，不覆盖纯样式与文案微调。
- 发布前可按版本打 tag 并补充“本版本新增项”小节。
