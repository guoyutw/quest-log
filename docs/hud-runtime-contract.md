# HUD runtime contract v1

This file durably records the current sanitized Quest Log player-read boundary. It is a presentation/read contract, not canonical Quest truth and not an authorization for autonomous Quest mutation.

## Authority chain

`canonical Quest state → derived player projection → private read adapter → HUD`

- Canonical Quest state is authoritative for Quest/candidate identity and current state.
- Player projection is derived presentation state.
- The Worker validates projection freshness before rendering.
- KV is transport/cache only and never becomes Quest truth.

## Projection v1

Current projection rows are keyed by `(entity_type, entity_id)`, where `entity_type` is `quest` or `candidate`.

Current fields:

- `display_title`
- `display_status`
- `display_stage`
- `display_now`
- `display_blocker`
- `display_next`
- `display_meaning`
- `source_state_updated_at`
- `source_route_updated_at`
- `projection_updated_at`
- `projection_contract_version`
- `projection_quality`

Freshness is exact: the source timestamps carried by the projection must match canonical state and the selected route. Missing, duplicate, unrecognized, or mismatched projection data fails closed.

## Candidate identity and status

Candidates remain candidate identities until owner-confirmed promotion. The player adapter currently accepts:

- `PARKED_CANDIDATE`: candidate exists but is not currently being actively explored.
- `ACTIVE_CANDIDATE`: candidate is currently being explored or continued.

Both remain Fog-of-War / non-formal identities. `ACTIVE_CANDIDATE` is **not** a formal Quest promotion.

Unknown candidate statuses fail closed. Presentation may aggregate candidate rows into one visual camp, but cardinality and identity remain per candidate.

## Meaning

`display_meaning` is optional and evidence-bounded.

It answers:

> Why is this line worth continuing now, given what is currently known?

It must not become an AI-authored life purpose, guaranteed gain, motivational filler, or unsupported interpretation. When evidence is insufficient, leave it empty.

Possible gain and earned growth remain separate concepts under `PRODUCT.md`.

## Completion / switch condition

Projection v1 currently has no dedicated durable field for completion/switch condition.

Therefore the read adapter and HUD must not derive a completion condition from `NEXT`, blocker text, route state, or other prose. A future field such as `display_clear_condition` requires an explicit schema/contract change before it is treated as authoritative.

Until then, the UI may omit the field or display it as unavailable.

## Fail-closed behavior

The private Worker validates the complete projection before rendering.

If current data cannot be validated:

1. do not fall back to raw canonical engineering prose;
2. use the last successfully validated player state when available;
3. visibly mark the result stale/pending synchronization;
4. if no last-good state exists, fail closed instead of showing an empty world as if no Quests existed.

Unknown status values are validation failures.

## Private KV roles

Two private KV records may be used by the current bounded runtime:

- `hud_projection_v1`: temporary compatibility mirror of the approved projection;
- `last_good_player_v1`: last successfully validated player payload.

Neither is authoritative. The intended continuation is direct projection delivery from the private read endpoint so the projection mirror can be removed.

## Runtime bindings

The sanitized Worker source expects binding names only:

- `QUEST_HUD_ENDPOINT`
- `QUEST_HUD_ACCESS_KEY`
- `QUEST_CACHE`

Values, URLs, ids, credentials, and live data are private and must never be committed.

## Regression acceptance

The synthetic fixture `fixtures/hud-read-v1.json` must remain sufficient to check these invariants:

- five formal Quest rows can be projected;
- multiple candidate rows preserve candidate cardinality;
- both `PARKED_CANDIDATE` and `ACTIVE_CANDIDATE` validate;
- candidate identities do not become formal Quests;
- stale source timestamps fail closed;
- unknown candidate status fails closed;
- meaning may be empty;
- no completion/switch condition is invented.

The existence of a passing presentation fixture does not prove external/private E2E behavior.
