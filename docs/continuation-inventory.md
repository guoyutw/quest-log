# Current implementation continuation inventory

This is an explicit publication boundary for the 0.1 initialization and current bounded HUD runtime. The legacy video mapper in `src/quest_hud/` is not the current Quest Log runtime.

| Current material | Public status | Bounded reason / continuation pointer |
|---|---|---|
| Current Web HUD presentation | PUBLIC SANITIZED REFERENCE EXISTS | Owner-approved presentation reference remains at `web/index.html` with synthetic demo data. |
| Current private HUD Worker logic | PUBLIC SANITIZED RUNTIME REFERENCE EXISTS | `runtime/quest-log-private-worker.js` captures current projection validation, candidate-status handling, and fail-closed last-good behavior. Private bindings, endpoints, ids, credentials, and live Quest data are excluded. |
| HUD read/projection contract | PUBLIC SANITIZED CONTRACT EXISTS | `docs/hud-runtime-contract.md` records authority, freshness, candidate enum semantics, optional meaning, KV mirror role, and fail-closed rules. |
| HUD adapter regression fixture | PUBLIC SYNTHETIC FIXTURE EXISTS | `fixtures/hud-read-v1.json` contains no live Quest data and covers both `PARKED_CANDIDATE` and `ACTIVE_CANDIDATE`. |
| Current n8n reconciliation/read workflows | NOT PUBLISHED | The discoverable `portfolio_demos/lead-intake-n8n/` material is a separate lead-intake demo, not Quest Log, and is not represented as the Quest workflow. The Quest n8n export was not present in the bounded public scope. |
| Current Quest-state/source schema | PARTIAL / PRIVATE CANONICAL | The public contract records the presentation/read boundary, but live canonical Quest instances, private Sheet schema/data, source lineage, and credentials remain private. |
| Current setup/export instructions | PARTIAL | Runtime binding names and behavior are documented; private deployment values and live-data setup are intentionally not published. |
| `src/quest_hud/` | PUBLISHED / LEGACY REFERENCE | Sanitized presentation-only video pipeline mapper; not the current Web HUD or live Quest implementation. |

## Current bounded private path

The private runtime currently uses a read endpoint plus exact projection freshness checks. A temporary private KV projection mirror may supply the approved projection when the upstream response does not yet include it directly. A separate last-good player snapshot is used only for fail-closed presentation.

The KV mirror is not authority. The remaining continuation is to remove manual projection mirroring by proving direct projection delivery through the private read endpoint, while preserving fail-closed behavior.

## Search boundary

Public files must not expose live Quest instances, private Sheet ids, worker URLs, account/namespace ids, credentials, secrets, private repo identifiers/config, local paths, or sensitive runtime evidence. Fixtures must remain synthetic.

## Next continuation action

Complete direct projection delivery through the private read endpoint and verify protected HUD E2E on a real canonical change. Do not call the read path autonomous while manual projection mirroring is still required.
