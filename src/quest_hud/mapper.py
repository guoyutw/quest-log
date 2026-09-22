"""Quest Presentation Mapper — the core of the RPG HUD.

Reads pipeline state and generates RPG-style Telegram text.
NEVER creates, modifies, or acts as authority for production state.

Architecture:
    _pipeline/current.json + PROJECT.json + transition binding
        ↓
    quest_mapper.py  (this module)
        ↓
    Telegram text (presentation only)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from quest_hud.zones import (
    ZONES,
    QuestZone,
    stage_to_zone,
    zone_progress,
    is_side_quest_stage,
    is_completed,
    is_final_done,
    _COMPLETE_STAGES,
)

# ── XP System (deterministic, no persistence) ───────────────────
# XP ONLY from owner main quest completions.
# Rule: ONLY OWNER MAIN QUEST COMPLETION EARNS XP.
#
# The caption quest is ONE owner-facing quest (💬 字幕試煉) regardless of
# how many technical sub-stages (E6, E8, correction loop) it contains.
# One quest = one XP reward. Technical stage count does NOT multiply XP.

_HUMAN_CHECKPOINT_XP: dict[str, int] = {
    # XP earned at quest COMPLETION markers.
    #
    # capcut_readback_done: CapCut quest done → +120
    # e8_approved: Caption quest done → +150
    # published: Publish done → +500
    #
    # NOTE: final_done is NOT here. Final +250 requires valid
    # final_review.approval.json — see compute_xp(final_approved=...).
    "capcut_readback_done": 120,
    "e8_approved": 150,
    "published": 500,
}
# capcut_refinement_pending = entering CapCut zone ≠ completing it → 0
# e6_review_pending = caption review is ACTIVE, not completed → 0
# final_done = waiting for owner to inspect final, NOT approved yet → 0
# archived = machine step, published already earned +500 → 0

# Final Boss +250 XP — only with valid approval
_FINAL_APPROVAL_XP = 250


def compute_xp(completed_stages: list[str], current_stage: str | None,
                final_approved: bool = False) -> int:
    """Compute total XP from completed human checkpoints. Deterministic, no persistence.

    XP is awarded when a completion marker appears — either in completed_stages
    (we've moved past it) OR as the current_stage (we just arrived at it).
    Final +250 requires valid final_review.approval.json (final_approved=True).
    """
    total = 0
    for stage in completed_stages:
        total += _HUMAN_CHECKPOINT_XP.get(stage, 0)
    # Also check current stage — it may itself be a completion marker
    if current_stage:
        total += _HUMAN_CHECKPOINT_XP.get(current_stage, 0)
    # Final +250 only with valid approval
    if final_approved:
        total += _FINAL_APPROVAL_XP
    return total


def is_human_quest(zone: QuestZone) -> bool:
    """Zone requires owner action = human quest."""
    return not zone.is_machine_only


# ── Achievement definitions ──────────────────────────────────────

@dataclass(frozen=True)
class Achievement:
    name: str
    icon: str
    description: str


ACHIEVEMENTS: list[Achievement] = [
    Achievement("Pipeline Finisher", "🏆", "有完整 production evidence"),
    Achievement("Back From AFK", "💤", "中斷數天後成功 resume"),
    Achievement("Stop Building Systems", "🔧", "完成一支影片沒有新增 architecture"),
    Achievement("Speed Runner", "⚡", "從 bootstrap 到 publish 用最短路徑"),
    Achievement("Caption Master", "✍️", "零修正通過字幕審查"),
    Achievement("CapCut Warrior", "⚔️", "完成 CapCut 精修"),
    Achievement("First Blood", "🩸", "第一支上片的影片"),
]


def detect_achievements(
    current_stage: str | None,
    completed_stages: list[str],
    project_data: dict[str, Any] | None = None,
) -> list[Achievement]:
    """Detect earned achievements from pipeline state. Fun layer only."""
    earned: list[Achievement] = []

    if current_stage in {"published", "archived"}:
        earned.append(ACHIEVEMENTS[0])  # Pipeline Finisher

    if current_stage == "capcut_refinement_pending":
        earned.append(ACHIEVEMENTS[5])  # CapCut Warrior

    if current_stage == "captions_pending" and "e6_review_pending" in completed_stages:
        earned.append(ACHIEVEMENTS[4])  # Caption Master

    return earned


# ── Zone detail data ─────────────────────────────────────────────

@dataclass
class ZoneDetail:
    """Detailed info about what's happening in a zone."""
    zone: QuestZone
    is_current: bool
    is_completed: bool
    is_locked: bool
    status_icon: str  # ✅ 🔥 🔒 ⚙️


@dataclass
class QuestState:
    """Complete state for rendering the Quest HUD."""
    project_title: str
    project_id: str
    current_zone: QuestZone
    current_stage: str | None
    transition: dict[str, Any] | None
    completed_stages: list[str]
    all_zones: list[ZoneDetail]
    xp: int
    achievements: list[Achievement]
    is_machine_only: bool
    is_campaign_complete: bool
    final_approved: bool  # True = valid final_review.approval.json exists
    errors: list[str]
    holds: list[str]


# ── Main mapper ──────────────────────────────────────────────────

def map_quest_state(
    project_data: dict[str, Any],
    current_data: dict[str, Any] | None,
    transition: dict[str, Any] | None = None,
    errors: list[str] | None = None,
    holds: list[str] | None = None,
    final_approved: bool = False,
) -> QuestState:
    """Map pipeline state to QuestState. Pure function, no side effects.

    final_approved: True when valid final_review.approval.json exists for
    the current final.mp4. This overrides zone mapping for final_done
    (advances to Launch Pad) and adds +250 XP.
    """
    current_stage = current_data.get("current_stage") if current_data else None
    route = current_data.get("route") if current_data else None

    current_zone = stage_to_zone(current_stage, route)

    # Override: final_done + valid approval → advance to zone 7 (Launch Pad)
    if current_stage == "final_done" and final_approved:
        current_zone = ZONES[6]  # Zone 7: Launch Pad

    is_machine = current_zone.is_machine_only
    is_complete = current_stage in _COMPLETE_STAGES

    # Build completed stages list
    completed: list[str] = []
    if current_data:
        for stage_name in _FRESH_ORDER:
            if stage_name == current_stage:
                break
            completed.append(stage_name)

    # Build zone details
    zone_details: list[ZoneDetail] = []
    for zone in ZONES:
        if zone.index < current_zone.index:
            zone_details.append(ZoneDetail(zone, False, True, False, "✅"))
        elif zone.index == current_zone.index:
            if is_complete:
                zone_details.append(ZoneDetail(zone, False, True, False, "✅"))
            elif zone.is_machine_only:
                zone_details.append(ZoneDetail(zone, True, False, False, "⚙️"))
            else:
                zone_details.append(ZoneDetail(zone, True, False, False, "🔥"))
        else:
            zone_details.append(ZoneDetail(zone, False, False, True, "🔒"))

    # When final_approved, mark Final Boss as completed in zone details
    if final_approved and current_stage == "final_done":
        for zd in zone_details:
            if zd.zone.index == 6:  # Final Boss
                zd.status_icon = "✅"
                zd.is_current = False
                zd.is_completed = True

    xp = compute_xp(completed, current_stage, final_approved=final_approved)
    achievements = detect_achievements(current_stage, completed, project_data)

    return QuestState(
        project_title=project_data.get("title", project_data.get("project_id", "Unknown")),
        project_id=project_data.get("project_id", "unknown"),
        current_zone=current_zone,
        current_stage=current_stage,
        transition=transition,
        completed_stages=completed,
        all_zones=zone_details,
        xp=xp,
        achievements=achievements,
        is_machine_only=is_machine,
        is_campaign_complete=is_complete,
        final_approved=final_approved,
        errors=errors or [],
        holds=holds or [],
    )


# Fresh route stage order (for deriving completed stages)
_FRESH_ORDER = [
    None,  # bootstrap (no stage yet)
    "stt1_done",
    "fusion_rough_done",
    "vad_coverage_done",
    "capcut_refinement_pending",
    "capcut_readback_done",
    "capcut_edited_media_done",
    "stt2_done",
    "edited_axis_done",
    "captions_pending",
    "e6_review_pending",
    "e8_approved",
    "final_done",
    "published",
    "archived",
]


# ── Quest copy: MAIN QUEST / NOW ACTION / COMPLETION ────────────
# Each must be DISTINCT. No copy-paste across the three.

_QUEST_COPY: dict[int, dict[str, str]] = {
    3: {  # CapCut
        "main": "調整影片節奏",
        "now": "打開 CapCut，看完整支 rough cut。\n修掉不自然停頓、誤剪與節奏問題。",
        "done": "你確認剪輯完成，儲存並關閉 CapCut。",
        "why": (
            "這一步是為了讓影片節奏真的由你決定。\n"
            "Fusion 可以先剪明顯空白，但什麼該留、什麼該剪，"
            "以及停頓是否自然，仍需要你的內容判斷。"
        ),
        "dont": "字幕 / Cards / Upload / Pipeline debug",
    },
    5: {  # 字幕試煉
        "main": "完成字幕試煉",
        "now": "看字幕預覽。\n修正錯字、分句與 timing。",
        "done": "所有需要修改的字幕已確認完成。",
        "why": (
            "字幕分行決定觀眾閱讀節奏，這是内容判斷不是格式問題。\n"
            "機器只能產生連續文字，換行時機和停頓保留需要你決定。"
        ),
        "dont": "Cards / Upload / 重新剪輯 / Pipeline debug",
    },
    6: {  # Final Boss
        "main": "擊敗 Final Boss",
        "now": "看真正的最終成品。\n確認畫面、聲音、字幕與整體節奏。",
        "done": "你確認「Final OK」。",
        "why": (
            "最終 QA 是上片前最後一道安全網。\n"
            "你需要用耳朵和眼睛確認畫面、聲音、字幕都對，"
            "因為機器無法判斷「整體節奏 OK」這種主觀感受。"
        ),
        "dont": "上傳 / 封存 / 改字幕",
    },
    7: {  # 發射台
        "main": "發布影片",
        "now": "確認要發布的 final 與發布設定。",
        "done": "你明確授權發布。",
        "why": (
            "發布是不可逆操作，需要你最後確認。\n"
            "確認 final 成品、標題、描述都對，然後授權上傳。"
        ),
        "dont": "",
    },
    1: {  # 建立冒險
        "main": "建立專案並確認來源",
        "now": "確認這是哪支影片，確認來源檔案正確。",
        "done": "PROJECT.json 建立、來源綁定完成。",
        "why": (
            "所有後續工作都基於正確的來源。\n"
            "確認來源才能確保 pipeline 不會白跑。"
        ),
        "dont": "",
    },
}


# ── Telegram text renderer ───────────────────────────────────────

def render_quest_hud(state: QuestState) -> str:
    """Render QuestState to Telegram-formatted text."""
    lines: list[str] = []

    lines.append("⚔️ LULUMI VIDEO QUEST")
    lines.append("")

    lines.append("🎬 Campaign")
    lines.append(f"  {state.project_title}")
    lines.append("")

    # Progress bar
    completed_count, total = zone_progress(state.current_zone, state.current_stage)
    bar_len = 10
    filled = int(completed_count / total * bar_len) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    lines.append("進度")
    lines.append(f"  {bar}  {completed_count} / {total}")
    lines.append("")

    # Campaign Complete — early return
    if state.is_campaign_complete:
        lines.append("🏆 CAMPAIGN COMPLETE")
        lines.append("")
        lines.append(f"🏆 XP: {state.xp}")
        if state.achievements:
            lines.append("")
            lines.append("🏅 成就")
            for ach in state.achievements:
                lines.append(f"  {ach.icon} {ach.name}")
        return "\n".join(lines)

    # Current Zone
    lines.append("📍目前區域")
    lines.append(f"  {state.current_zone.icon} {state.current_zone.name}")
    lines.append("")

    # MAIN QUEST vs SYSTEM JOURNEY
    if state.is_machine_only:
        lines.append("⚙️ SYSTEM JOURNEY")
        lines.append(f"  目前處理：{_get_machine_summary(state)}")
        lines.append("")
        lines.append("  你現在：不需要操作")
        lines.append("")
        next_zone = _get_next_zone(state)
        if next_zone:
            lines.append(f"  完成後自動前往：{next_zone.icon} {next_zone.name}")
    else:
        copy = _QUEST_COPY.get(state.current_zone.index, {})
        lines.append("🔥 MAIN QUEST")
        lines.append(f"  {copy.get('main', _get_main_quest(state))}")
        lines.append("")
        lines.append("🎯 現在只做")
        for line in copy.get("now", _get_now_action(state)).split("\n"):
            lines.append(f"  {line}")
        lines.append("")
        lines.append("✅ 完成條件")
        lines.append(f"  {copy.get('done', _get_done_condition(state))}")

    lines.append("")

    # NEXT
    if not state.is_machine_only:
        next_zone = _get_next_zone(state)
        if next_zone:
            lines.append("🔮 下一區")
            lines.append(f"  {next_zone.icon} {next_zone.name}")
            lines.append("")

    # DO NOT DO
    if not state.is_machine_only:
        copy = _QUEST_COPY.get(state.current_zone.index, {})
        dont = copy.get("dont", "")
        if dont:
            lines.append("🚫 現在不要做")
            lines.append(f"  {dont}")
            lines.append("")

    # XP
    if state.xp > 0:
        lines.append(f"🏆 XP: {state.xp}")

    # Achievements
    if state.achievements:
        lines.append("")
        lines.append("🏅 成就")
        for ach in state.achievements:
            lines.append(f"  {ach.icon} {ach.name}")

    return "\n".join(lines)


def render_world_map(state: QuestState) -> str:
    """Render the world map view."""
    lines: list[str] = []
    lines.append("🗺 VIDEO CAMPAIGN")
    lines.append("")

    for zone_detail in state.all_zones:
        z = zone_detail.zone
        icon = zone_detail.status_icon
        if zone_detail.is_current:
            if z.is_machine_only:
                label = " ← SYSTEM WORKING"
            else:
                label = " ← YOU ARE HERE"
        else:
            label = ""
        lines.append(f"  {icon} {z.icon} {z.name}{label}")

    lines.append("")
    if state.xp > 0:
        lines.append(f"🏆 XP: {state.xp}")

    return "\n".join(lines)


# ── Intent handlers ──────────────────────────────────────────────

def render_next_step(state: QuestState) -> str:
    """Render response for '下一步' intent."""
    lines: list[str] = []
    lines.append("⚔️ QUEST STATUS")
    lines.append("")
    lines.append(f"📍 {state.current_zone.icon} {state.current_zone.name}")
    lines.append("")

    if state.is_machine_only:
        lines.append("⚙️ SYSTEM JOURNEY")
        lines.append(f"  目前處理：{_get_machine_summary(state)}")
        lines.append("")
        lines.append("  你現在：不需要操作")
    else:
        copy = _QUEST_COPY.get(state.current_zone.index, {})
        lines.append("🔥 現在只做：")
        for line in copy.get("now", _get_now_action(state)).split("\n"):
            lines.append(f"  {line}")
        lines.append("")
        lines.append("✅ 完成條件：")
        lines.append(f"  {copy.get('done', _get_done_condition(state))}")

    return "\n".join(lines)


def render_stuck(state: QuestState, detail: str = "") -> str:
    """Render response for '我卡住了' intent."""
    lines: list[str] = []
    lines.append("⚠️ ENCOUNTER")
    lines.append("")

    if state.is_machine_only:
        lines.append("系統仍在處理中。")
        lines.append("")
        lines.append(f"目前處理：{_get_machine_summary(state)}")
        lines.append("目前沒有證據顯示失敗。")
    else:
        lines.append("目前這個任務尚未完成。")
        lines.append("")
        lines.append(f"我目前只知道：{_get_main_quest(state)}仍在進行中。")
        lines.append("")

        if detail:
            lines.append("🎯 需要修正：")
            lines.append(f"  {detail}")
            lines.append("")
        else:
            lines.append("🎯 你可以告訴我：")
            lines.append("  具體卡在哪個點，我幫你找到下一步。")
            lines.append("")

    return "\n".join(lines)


def render_show_me(state: QuestState) -> str:
    """Render response for 'Show me' — technical details."""
    lines: list[str] = []
    lines.append("🔍 TECHNICAL STATUS")
    lines.append("")
    lines.append(f"Project: {state.project_id}")
    lines.append(f"Stage: {state.current_stage or '(none)'}")
    lines.append(f"Zone: {state.current_zone.name}")
    lines.append("")

    if state.transition:
        lines.append("Transition Binding:")
        lines.append(f"  Status: {state.transition.get('status', '?')}")
        action = state.transition.get("next_action", {})
        lines.append(f"  Instruction: {action.get('instruction', '?')}")
        lines.append(f"  Command: {action.get('command', '?')}")
        surface = state.transition.get("primary_surface", {})
        lines.append(f"  Surface: {surface.get('kind', '?')}")

    if state.errors:
        lines.append("")
        lines.append("Errors:")
        for e in state.errors:
            lines.append(f"  ❌ {e}")

    if state.holds:
        lines.append("")
        lines.append("Holds:")
        for h in state.holds:
            lines.append(f"  ⏸ {h}")

    return "\n".join(lines)


def render_why(state: QuestState) -> str:
    """Render response for '為什麼要做這一步'.

    Format:
    第一句：這一步對影片的價值。
    後面最多兩句：為什麼需要 owner。
    """
    copy = _QUEST_COPY.get(state.current_zone.index, {})
    if copy.get("why"):
        return copy["why"]

    if state.current_zone.is_machine_only:
        return "這是機器自動處理的步驟。等它完成就好。"

    return "這是影片製作流程中的一步。跟我說「下一步」看具體要做什麼。"


# ── Internal helpers ─────────────────────────────────────────────

def _get_machine_summary(state: QuestState) -> str:
    """Get a human-readable summary of what the machine is doing."""
    summaries: dict[int, str] = {
        1: "project bootstrap",
        2: "STT #1 → Fusion → VAD",
        4: "Readback → STT #2 → Remap",
    }
    return summaries.get(state.current_zone.index, "processing")


def _get_main_quest(state: QuestState) -> str:
    """Fallback main quest title."""
    quests: dict[int, str] = {
        1: "建立專案並確認來源",
        3: "調整影片節奏",
        5: "完成字幕試煉",
        6: "擊敗 Final Boss",
        7: "發布影片",
    }
    if state.transition:
        action = state.transition.get("next_action", {})
        instruction = action.get("instruction", "")
        if instruction:
            return instruction
    return quests.get(state.current_zone.index, "繼續前進")


def _get_now_action(state: QuestState) -> str:
    """Fallback now action."""
    if state.transition:
        action = state.transition.get("next_action", {})
        instruction = action.get("instruction", "")
        if instruction:
            return instruction
    defaults: dict[int, str] = {
        1: "確認這是哪支影片",
        3: "打開 CapCut，修剪空白與節奏",
        5: "看字幕預覽，逐句修正",
        6: "看成品，確認畫面聲音字幕",
        7: "確認發布",
    }
    return defaults.get(state.current_zone.index, "繼續前進")


def _get_done_condition(state: QuestState) -> str:
    """Fallback completion condition."""
    conditions: dict[int, str] = {
        1: "PROJECT.json 建立、來源綁定完成",
        3: "你確認剪輯完成，儲存並關閉 CapCut",
        5: "所有需要修改的字幕已確認完成",
        6: "你確認「Final OK」",
        7: "你明確授權發布",
    }
    return conditions.get(state.current_zone.index, "完成當前任務")


def _get_next_zone(state: QuestState) -> QuestZone | None:
    """Get the next zone after current."""
    current_idx = state.current_zone.index
    if current_idx < len(ZONES):
        return ZONES[current_idx]
    return None
