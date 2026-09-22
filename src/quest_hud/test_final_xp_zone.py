#!/usr/bin/env python3
"""Focused tests for Final XP timing + zone mapping."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from quest_hud.mapper import map_quest_state, compute_xp, _HUMAN_CHECKPOINT_XP, _FINAL_APPROVAL_XP
from quest_hud.zones import stage_to_zone, zone_progress, ZONES

PROJ = {"project_id": "test", "title": "T", "route": "capcut"}

def _cs(stage):
    return {"schema_version": 1, "project_id": "test", "route": "capcut",
            "status": "running", "current_stage": stage, "revision": 1}


def run_tests():
    errors = []

    # ── TEST 1: final_done, no approval → XP=270, Zone=Final Boss ──
    s = map_quest_state(PROJ, _cs("final_done"), final_approved=False)
    if s.xp != 270:
        errors.append(f"T1 XP: got {s.xp} expected 270")
    if s.current_zone.index != 6:
        errors.append(f"T1 Zone: got {s.current_zone.index} expected 6 (Final Boss)")
    if s.final_approved:
        errors.append(f"T1 final_approved should be False")
    print(f"TEST 1 (final_done, no approval): XP={s.xp} Zone={s.current_zone.name} {'PASS' if not errors else 'FAIL'}")

    # ── TEST 2: final_done, valid approval → XP=520, Zone=Launch Pad ──
    s2 = map_quest_state(PROJ, _cs("final_done"), final_approved=True)
    if s2.xp != 520:
        errors.append(f"T2 XP: got {s2.xp} expected 520")
    if s2.current_zone.index != 7:
        errors.append(f"T2 Zone: got {s2.current_zone.index} expected 7 (Launch Pad)")
    if not s2.final_approved:
        errors.append(f"T2 final_approved should be True")
    # Final Boss should be marked completed
    fb = [z for z in s2.all_zones if z.zone.index == 6][0]
    if not fb.is_completed:
        errors.append(f"T2 Final Boss should be completed")
    print(f"TEST 2 (final_done, valid approval): XP={s2.xp} Zone={s2.current_zone.name} {'PASS' if not errors[-1:] else 'FAIL'}")

    # ── TEST 3: stale approval (simulated) → same as no approval ──
    # We simulate this by passing final_approved=False even though approval file exists
    s3 = map_quest_state(PROJ, _cs("final_done"), final_approved=False)
    if s3.xp != 270:
        errors.append(f"T3 XP: got {s3.xp} expected 270")
    if s3.current_zone.index != 6:
        errors.append(f"T3 Zone: got {s3.current_zone.index} expected 6")
    print(f"TEST 3 (stale approval → treated as no approval): XP={s3.xp} Zone={s3.current_zone.name} {'PASS' if not errors[-1:] else 'FAIL'}")

    # ── TEST 4: published → XP=1020, Campaign Complete ──
    s4 = map_quest_state(PROJ, _cs("published"), final_approved=True)
    if s4.xp != 1020:
        errors.append(f"T4 XP: got {s4.xp} expected 1020")
    if not s4.is_campaign_complete:
        errors.append(f"T4 should be campaign complete")
    print(f"TEST 4 (published): XP={s4.xp} Complete={s4.is_campaign_complete} {'PASS' if not errors[-1:] else 'FAIL'}")

    # ── TEST 5: archived → XP=1020, 7/7 ──
    s5 = map_quest_state(PROJ, _cs("archived"), final_approved=True)
    c, t = zone_progress(s5.current_zone, s5.current_stage)
    if s5.xp != 1020:
        errors.append(f"T5 XP: got {s5.xp} expected 1020")
    if not (c == t == 7):
        errors.append(f"T5 Progress: got {c}/{t} expected 7/7")
    print(f"TEST 5 (archived): XP={s5.xp} Progress={c}/{t} {'PASS' if not errors[-1:] else 'FAIL'}")

    # ── TEST 6: World Map before Final OK ──
    hud_no = render_world_map(s)  # s = final_done, no approval
    if "🔥 🎥 Final Boss" not in hud_no:
        errors.append("T6 World Map should show Final Boss as current")
    if "🔒 🚀 發射台" not in hud_no:
        errors.append("T6 World Map should show Launch Pad locked")
    print(f"TEST 6 (World Map before Final OK): {'PASS' if '🔥 🎥 Final Boss' in hud_no and '🔒 🚀 發射台' in hud_no else 'FAIL'}")

    # ── TEST 7: World Map after Final OK ──
    hud_yes = render_world_map(s2)  # s2 = final_done, approved
    if "✅ 🎥 Final Boss" not in hud_yes:
        errors.append("T7 World Map should show Final Boss completed")
    if "🔥 🚀 發射台" not in hud_yes:
        errors.append("T7 World Map should show Launch Pad as current")
    print(f"TEST 7 (World Map after Final OK): {'PASS' if '✅ 🎥 Final Boss' in hud_yes and '🔥 🚀 發射台' in hud_yes else 'FAIL'}")

    # ── TEST 8: Next step before Final OK ──
    next_no = render_next_step(s)
    if "Final Boss" not in next_no:
        errors.append("T8 Next step should mention Final Boss")
    print(f"TEST 8 (Next before Final OK): {'PASS' if 'Final Boss' in next_no else 'FAIL'}")

    # ── TEST 9: Next step after Final OK ──
    next_yes = render_next_step(s2)
    if "發射台" in next_yes and "Final OK" not in next_yes:
        pass  # Good — shows Launch Pad, not Final OK
    else:
        errors.append("T9 Next step should show Launch Pad, not Final OK")
    print(f"TEST 9 (Next after Final OK): {'PASS' if '發射台' in next_yes and 'Final OK' not in next_yes else 'FAIL'}")

    # ── TEST 10: Quest HUD before Final OK ──
    from quest_hud.mapper import render_quest_hud
    hud_full_no = render_quest_hud(s)
    if "🔥 MAIN QUEST" in hud_full_no and "擊敗 Final Boss" in hud_full_no:
        pass  # Good
    else:
        errors.append("T10 HUD should show Final Boss main quest")
    if "XP: 520" in hud_full_no or "XP: 520" in hud_full_no:
        errors.append("T10 HUD should NOT show XP 520 without approval")
    print(f"TEST 10 (HUD before Final OK): {'PASS' if '擊敗 Final Boss' in hud_full_no and '520' not in hud_full_no else 'FAIL'}")

    # ── TEST 11: Quest HUD after Final OK ──
    hud_full_yes = render_quest_hud(s2)
    if "🚀 發射台" in hud_full_yes and "發布影片" in hud_full_yes:
        pass  # Good — shows publish quest
    else:
        errors.append("T11 HUD should show Launch Pad / Publish")
    if "擊敗 Final Boss" in hud_full_yes:
        errors.append("T11 HUD should NOT show Final Boss after approval")
    print(f"TEST 11 (HUD after Final OK): {'PASS' if '發布影片' in hud_full_yes and '擊敗 Final Boss' not in hud_full_yes else 'FAIL'}")

    # ── Summary ──
    if errors:
        print(f"\n❌ {len(errors)} FAILURES:")
        for e in errors:
            print(f"  {e}")
    else:
        print(f"\n✅ ALL 11 TESTS PASS")

    return len(errors) == 0


def render_world_map(state):
    lines = ["🗺 VIDEO CAMPAIGN", ""]
    for zd in state.all_zones:
        z = zd.zone
        icon = zd.status_icon
        if zd.is_current:
            label = " ← SYSTEM WORKING" if z.is_machine_only else " ← YOU ARE HERE"
        else:
            label = ""
        lines.append(f"  {icon} {z.icon} {z.name}{label}")
    if state.xp > 0:
        lines.append("")
        lines.append(f"🏆 XP: {state.xp}")
    return "\n".join(lines)


def render_next_step(state):
    lines = ["⚔️ QUEST STATUS", "", f"📍 {state.current_zone.icon} {state.current_zone.name}", ""]
    if state.is_machine_only:
        lines.append("⚙️ SYSTEM JOURNEY")
    else:
        from quest_hud.mapper import _QUEST_COPY, _get_now_action, _get_done_condition
        copy = _QUEST_COPY.get(state.current_zone.index, {})
        lines.append("🔥 現在只做：")
        lines.append(f"  {copy.get('now', _get_now_action(state))}")
        lines.append("")
        lines.append("✅ 完成條件：")
        lines.append(f"  {copy.get('done', _get_done_condition(state))}")
    return "\n".join(lines)


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
