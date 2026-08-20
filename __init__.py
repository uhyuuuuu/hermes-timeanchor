"""timeanchor —— 每轮注入当前时间（中文版），跨天自动强调。

思路抄自社区插件：
- hermes-live-time (chenfeijiang95-ui): pre_llm_call 钩子每轮注入精确时间
- time-gap (Randool): 从 state.db 读上一条 assistant 消息时间戳判断跨天

效果：每轮 API 请求自动带上 [当前时间：…]，不写历史、不碰系统提示缓存、
几乎零 token 成本。时区跟随系统本地时区（自动适配世界各地用户）。
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

_WEEKDAYS = "一二三四五六日"


def _now() -> tuple[datetime, str]:
    """当前时间（系统本地时区），返回 (时间, 时区标签如 UTC+8)。"""
    now = datetime.now().astimezone()
    off = now.utcoffset()
    label = ""
    if off is not None:
        total_min = int(off.total_seconds() // 60)
        sign = "+" if total_min >= 0 else "-"
        total_min = abs(total_min)
        label = f"UTC{sign}{total_min // 60:02d}:{total_min % 60:02d}"
    return now, label


def _db_path() -> Optional[Path]:
    home = os.environ.get("HERMES_HOME") or str(Path.home() / ".hermes")
    p = Path(home) / "state.db"
    return p if p.exists() else None


def _last_assistant_ts(session_id: str) -> Optional[float]:
    """上一条 assistant 消息的时间戳（只读，任何失败返回 None 不阻塞轮次）。"""
    path = _db_path()
    if not session_id or path is None:
        return None
    conn = None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=1.0)
        row = conn.execute(
            "SELECT MAX(timestamp) FROM messages "
            "WHERE session_id = ? AND role = 'assistant'",
            (session_id,),
        ).fetchone()
        ts = row[0] if row else None
        return float(ts) if ts else None
    except Exception:
        return None
    finally:
        if conn is not None:
            conn.close()


def _on_pre_llm_call(*, session_id: str = "", **_kw: Any) -> Optional[dict]:
    """返回注入文本：每轮当前时间；跨天时加一句强调。"""
    now, tz = _now()
    text = (
        f"[当前时间：{now.year}年{now.month}月{now.day}日 "
        f"星期{_WEEKDAYS[now.weekday()]} {now.hour:02d}:{now.minute:02d}（{tz}）"
    )
    prev = _last_assistant_ts(session_id)
    if prev:
        try:
            pdt = datetime.fromtimestamp(prev, now.tzinfo)
            if (now.date() - pdt.date()).days >= 1:
                text += "；注意：距上一条消息已跨天，现在是新的一天，旧的日期/时间概念已过时"
        except Exception:
            pass
    text += "]"
    return {"context": text}


def register(ctx) -> None:
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
