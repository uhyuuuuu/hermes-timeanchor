# timeanchor —— Hermes 时间锚点插件

让 Hermes 助手**每轮都知道当前时间**的中文插件。零依赖、零配置、几乎零 token 成本。

## 解决什么问题

大语言模型天生没有"钟"——它不知道现在是几点、今天几号。问它"现在几点"，它只能瞎猜或翻聊天记录，经常闹出"下午说大半夜"的笑话。

timeanchor 在每次 API 请求前，自动往上下文里注入一行当前时间，让助手每轮开口前都能"瞄一眼表"。

## 效果

每轮自动注入：

```
[当前时间：2026年8月20日 星期四 14:47（UTC+08:00）]
```

**跨天自动强调**：如果上一条消息是昨天（或更早）的，会追加一句"距上一条消息已跨天，现在是新的一天"，避免助手沿用旧日期概念。

## 特性

- 🕐 每轮注入精确时间（年/月/日/星期/时分，**自动跟随系统时区**）
- 🌙 跨天自动提醒（读本地 state.db 最后一条 assistant 消息时间戳，只读、失败静默回退）
- ⚡ 几乎零成本：每轮仅十几个 token
- 🧹 不写聊天历史、不碰系统提示缓存（prompt cache 前缀稳定）
- 📦 纯 Python 标准库，零依赖

## 安装

1. 把 `timeanchor/` 目录放到你的 Hermes 插件目录（`~/AppData/Local/hermes/plugins/` 或 `$HERMES_HOME/plugins/`）
2. 启用插件：

```bash
hermes plugins enable timeanchor
```

3. 重启 Hermes，完事。

验证：随便问助手"现在几点"，它能准确说出当前时间就是生效了。

## 原理

- 钩子：`pre_llm_call`（每次 LLM 请求前触发，返回 `{"context": "文本"}`，自动追加到当轮 user 消息，不落库）
- 时区：自动跟随系统本地时区，任何国家的用户装上即得本地时间
- 跨天检测：只读查询 `state.db` 的 `messages` 表，取当前 session 最后一条 assistant 消息的 `timestamp`，与当前时间比较
- 任何失败都静默回退为纯时间注入，绝不阻塞对话

## 致谢

思路借鉴自社区插件：

- [hermes-live-time](https://github.com/chenfeijiang95-ui/hermes-live-time) —— 每轮注入精确时间
- [time-gap](https://github.com/Randool/time-gap) —— 跨天检测提醒

本插件将其合并为单一中文实现，去掉配置项、时区自动跟随系统，开箱即用。

## License

MIT
