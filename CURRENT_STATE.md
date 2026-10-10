# Current state

**Status:** 0.1 initialization complete; three finish-line gates remain. Gate 3 has bounded discovery/design progress only and is not complete.

The public sanitized Web HUD presentation reference remains at `web/index.html`. A private authenticated HUD runtime also exists. The private runtime is now a bounded read/presentation path rather than a presentation-only snapshot, but it is **not yet a proven unattended end-to-end source of truth**.

## Current private HUD read path

Current bounded architecture:

`private canonical Quest state → private read endpoint → HUD Worker → projection validation → player HUD`

The Worker may use two private KV records as transport/fail-closed support:

- `hud_projection_v1`: temporary mirror of the approved player projection when the upstream read response does not yet carry the projection directly;
- `last_good_player_v1`: last successfully validated player state used only when the current read/projection fails closed.

Neither KV record is Quest truth. Canonical Quest state remains upstream; the player projection is derived presentation state.

A sanitized reference of the current Worker is published at `runtime/quest-log-private-worker.js`. Runtime bindings, private endpoints, credentials, namespace ids, Sheet ids, and live Quest contents remain private.

## Current Web HUD behavior

- Desktop: World Map-first. Mobile: Objective Tracker-first; bottom entrances are 任務 / 地圖 / 角色.
- Quest detail supports current stage, NOW, real blocker, NEXT, and optional meaning.
- Chinese-first comprehension with icon/number/short-English texture; Modern Adventure colours; Fog of War for unconfirmed candidates.
- No fake XP, level, or progress bar; profile numbers must be real status numbers.
- Player projection freshness must exactly match canonical state/selected-route timestamps. Missing, duplicate, unknown, or stale projection data fails closed instead of falling back to raw engineering prose.
- Candidate identities remain non-formal. Both `PARKED_CANDIDATE` and `ACTIVE_CANDIDATE` are accepted by the current read adapter; neither status promotes a candidate into a formal Quest.
- The current map visually aggregates candidates into a Fog-of-War camp, while the Objective Tracker shows candidate lines individually so each candidate can expose its own NOW, NEXT, and evidence-bounded meaning. Candidate count and identity remain per candidate.
- `display_meaning` is optional. It means “why this line is worth continuing now, based on evidence,” not an AI-authored life purpose or guaranteed outcome.
- The v1 projection does **not** yet contain a durable completion/switch-condition field. The UI must not invent one from NEXT or other fields.

The durable projection/read rules are recorded in `docs/hud-runtime-contract.md`.

## Known remaining gap

The private read path still has an adapter/mirroring gap: direct unattended delivery of the player projection from the upstream read endpoint has not been proven as the sole path. The KV projection mirror is therefore still required as a bounded compatibility layer, and `last_good_player_v1` remains the fail-closed fallback.

This means Gate 1 is **not** declared complete by the existence of the private HUD read path alone. A future gate close requires a real evidence-backed unattended reconciliation/read flow with independently checkable end-to-end evidence.

A synthetic regression fixture for the read adapter is at `fixtures/hud-read-v1.json`. It includes both parked and active candidate statuses so a new candidate status cannot silently force the entire HUD back to an old snapshot.

## Gate 3 — local n8n migration

The exact `Quest Log 0.4B — Generic Quest Reconciler` was identified on 2026-09-25 and its owner-provided export and identity/hash were verified: workflow ID `bP6M5W1s5lT0UzWJ`, export SHA-256 `2955c253eacb7dcb4f45c7dc35e049abd23d45253dd41588bafbfd1810b23906`. The earlier “locate the workflow” blocker is resolved.

Migration candidate v3 exists. Its first independent review was not a valid content review because the reviewer could not access the artifact; Issue #64 remains OPEN. There is not yet evidence of implementation, local n8n installation/activation, a real E2E event, or cutover.

## NEXT ACTION

For the HUD/read path: replace the temporary projection mirror with direct projection delivery from the private read endpoint, then verify a real canonical-state change reaches the protected HUD without manual KV synchronization and without weakening fail-closed freshness checks.

For Gate 3: have the qualified reviewer obtain and review the exact same candidate v3 bytes. Only after valid review and the required owner gate may the existing authority proceed to implementation, local E2E, and cutover.

## CLEAR CONDITION

A real evidence-backed reconciliation run exists, preserves the evidence path's non-authoritative/fail-closed boundary, and has independently checkable evidence. For the HUD/read path, a canonical change must reach the protected HUD through the intended read adapter without manual projection mirroring. For Gate 3, this also requires the local runtime, real GitHub-triggered E2E, existing Quest projection/HUD readback, and post-E2E cutover evidence.

No 0.1 Retro until gates 1–3 all PASS.
