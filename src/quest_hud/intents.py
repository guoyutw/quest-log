"""Quest intent classifier — narrow-matches owner text to quest intents.

Returns None for non-quest text (general chat, unrelated requests).
This is a PRESENTATION-LAYER classifier — it never modifies production state.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QuestIntent:
    """Classified quest intent with optional extracted detail."""
    intent: str
    detail: str = ""  # e.g. "CapCut 開不了" from "我卡住了 CapCut 開不了"


# ── Intent patterns ──────────────────────────────────────────────
# Order matters: more specific patterns first.

_PATTERNS: list[tuple[str, re.Pattern, bool]] = [
    # (intent_name, compiled_regex, has_detail_group)

    # "下一步" variants
    ("next", re.compile(r"^(下一步|現在做什麼|現在幹嘛|現在要幹嘛|what.?s.?next|next)$", re.I), False),

    # "看世界地圖" variants
    ("world_map", re.compile(r"^(看世界地圖|世界地圖|world.?map|campaign.?map|地圖)$", re.I), False),

    # "Show me" variants
    ("show_me", re.compile(r"^(show\s*me|技術細節|technical|debug|診斷|diagnostic)$", re.I), False),

    # "為什麼要做這一步" variants — require context, don't match bare "為什麼"
    ("why", re.compile(r"^(為什麼要做這一步|為什麼要做|為什麼要|為什麼這步|這步做什麼|這一步做什麼|why.*(step|quest|zone|this))$", re.I), False),

    # "我卡住了" variants — may have trailing detail
    ("stuck", re.compile(r"^(?:我卡住了|卡住了|stuck|blocked|出錯了|出問題了)(?:\s+(.+))?$", re.I), True),

    # Completion intents — these trigger production verification, NOT fake advance
    ("complete_capcut", re.compile(r"^(我剪好了|剪好了|capcut.?done|capcut.?完成)$", re.I), False),
    ("complete_captions", re.compile(r"^(字幕完成|字幕好了|captions??.?done|字幕?.?審查完成)$", re.I), False),
    ("complete_final", re.compile(r"^(final.?ok|final.?done|成片.?ok|成片完成|成品.?ok|確認.?final)$", re.I), False),
    ("complete_publish", re.compile(r"^(發布|publish|上片|上傳|發佈)$", re.I), False),
]


def classify_quest_intent(text: str) -> Optional[QuestIntent]:
    """Classify user text as a quest intent.

    Returns QuestIntent if the text matches a quest pattern.
    Returns None for general chat / unrelated text.

    This is NARROW matching — only exact short phrases are recognized.
    Long messages, questions, and requests fall through to normal agent.
    """
    if not text:
        return None

    # Normalize: strip whitespace, take first line only
    normalized = text.strip().split("\n")[0].strip()

    # Reject long messages — quest intents are short
    if len(normalized) > 50:
        return None

    for intent_name, pattern, has_detail in _PATTERNS:
        match = pattern.match(normalized)
        if match:
            detail = ""
            if has_detail and match.lastindex and match.lastindex >= 1:
                detail = (match.group(1) or "").strip()
            return QuestIntent(intent=intent_name, detail=detail)

    return None
