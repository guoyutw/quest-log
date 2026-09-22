"""Quest zone definitions and pipeline-stage-to-zone mapping.

Zones are a PRESENTATION grouping of pipeline stages.
They are NOT a second state machine — they derive entirely from
_pipeline/current.json + PROJECT.json + transition binding.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ── Zone definitions ─────────────────────────────────────────────

@dataclass(frozen=True)
class QuestZone:
    index: int
    name: str
    icon: str
    description: str
    is_machine_only: bool = False  # True = no owner action needed


ZONES: list[QuestZone] = [
    QuestZone(1, "建立冒險", "🧭", "確認來源、建立專案骨架"),
    QuestZone(2, "AI 偵察", "🧠", "STT #1、Fusion、VAD — 機器自動完成", is_machine_only=True),
    QuestZone(3, "剪輯地下城", "✂️", "CapCut 精修 — 留什麼、剪什麼、節奏"),
    QuestZone(4, "時間軸重建", "🔄", "Readback、STT #2、Remap — 機器重建", is_machine_only=True),
    QuestZone(5, "字幕試煉", "💬", "字幕文字、分句、timing、修正"),
    QuestZone(6, "Final Boss", "🎥", "最終成品審驗 — 畫面、聲音、字幕"),
    QuestZone(7, "發射台", "🚀", "發布與封存"),
]

ZONE_BY_INDEX = {z.index: z for z in ZONES}

# ── Stage → Zone mapping ────────────────────────────────────────
# Maps pipeline current_stage (from current.json) to zone index.
# Multiple stages can map to the same zone.

# Fresh CapCut-first route stages
_FRESH_STAGE_ZONE: dict[str, int] = {
    # Zone 1: Bootstrap
    # (no current_stage yet = before bootstrap)
    # Zone 2: AI Recon
    "stt1_done": 2,
    "fusion_rough_done": 2,
    "vad_coverage_done": 2,
    # Zone 3: CapCut Refinement
    "capcut_refinement_pending": 3,
    # Zone 4: Timeline Rebuild
    "capcut_readback_done": 4,
    "capcut_edited_media_done": 4,
    "stt2_done": 4,
    "edited_axis_done": 4,
    # Zone 5: Caption Trial
    "captions_pending": 5,
    "e6_review_pending": 5,
    # Zone 6: Final Boss
    "e8_approved": 6,
    "final_done": 6,  # Final Boss until owner says Final OK
    # Zone 7: Publish
    "published": 7,
    "archived": 7,
}

# Express legacy route stages
_EXPRESS_STAGE_ZONE: dict[str, int] = {
    "bootstrap_done": 1,
    "stt_done": 2,
    "cut_evidence_done": 2,
    "decision_proposed": 3,
    "decision_approved": 3,
    "edit_compiled": 4,
    "captions_proposed": 5,
    "captions_approved": 5,
    "captions_mechanical": 5,
    "captions_cp1b_done": 5,
    "cards_proposed": 5,
    "cards_approved": 5,
    "overlay_done": 5,
    "cards_skipped": 6,
    "cp2_approved": 6,
    "export_ready": 6,
    "post_export_PASS": 6,
    "meta_selected": 6,  # Final Boss until publish
    "published": 7,
    "archived": 7,
}

# Combined lookup
_STAGE_ZONE: dict[str, int] = {**_FRESH_STAGE_ZONE, **_EXPRESS_STAGE_ZONE}

# Stages that represent "truly complete" — all work done
_COMPLETE_STAGES = {"published", "archived"}


def stage_to_zone(current_stage: str | None, route: str | None = None) -> QuestZone:
    """Map a pipeline current_stage to its QuestZone.

    Args:
        current_stage: The current_stage field from _pipeline/current.json
        route: The route field (None = fresh_capcut_first default)

    Returns:
        The QuestZone the project is currently in.
    """
    if current_stage is None:
        return ZONES[0]  # Zone 1: 建立冒險

    zone_index = _STAGE_ZONE.get(current_stage)
    if zone_index is None:
        # Unknown stage — default to zone 1 (safest)
        return ZONES[0]

    return ZONE_BY_INDEX[zone_index]


def zone_progress(zone: QuestZone, current_stage: str | None = None) -> tuple[int, int]:
    """Return (completed_zones, total_zones) for progress bar.

    Definition: completed = zone index you have FINISHED.
    - Zone 1 active (bootstrap) → 0/7 (not done yet)
    - Zone 2 active (AI Recon) → 1/7 (zone 1 done)
    - Zone 7 active + published/archived → 7/7 (all done)
    """
    if current_stage in _COMPLETE_STAGES:
        return (len(ZONES), len(ZONES))
    return (zone.index - 1, len(ZONES))


def completed_zones_for_stage(current_stage: str | None) -> list[int]:
    """Return list of zone indices that are fully completed."""
    if current_stage is None:
        return []
    if current_stage in _COMPLETE_STAGES:
        return list(range(1, len(ZONES) + 1))
    zone_index = _STAGE_ZONE.get(current_stage, 1)
    return list(range(1, zone_index))


# ── Side quest detection ─────────────────────────────────────────

# Stages that are optional / side quests
SIDE_QUEST_STAGES = {
    "cards_proposed",
    "cards_approved",
    "overlay_done",
    "cards_skipped",
}


def is_side_quest_stage(current_stage: str | None) -> bool:
    """Check if the current stage is a side quest (optional enhancement)."""
    return current_stage in SIDE_QUEST_STAGES


# ── Completion detection ─────────────────────────────────────────

def is_completed(current_stage: str | None) -> bool:
    """Check if the project is fully completed/archived."""
    return current_stage in _COMPLETE_STAGES


def is_final_done(current_stage: str | None) -> bool:
    """Check if final is done (ready for publish)."""
    return current_stage == "final_done"
