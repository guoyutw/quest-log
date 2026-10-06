# Product definition

Quest Log recovers useful Quest state from evidence instead of asking the owner to maintain another task system.

## 0.1 goal

After normal work, recover and show: Quests, current stage/state, the actionable next step, and blockers only for real stop conditions.

## Conceptual architecture

`Evidence Sources → Reconciler → Quest State → Read API → HUD`

This is conceptual for 0.1, not a permanent architecture freeze. Quest Log is not a manual task manager, percentage engine, autonomous new-Quest generator, or replacement for private runtime stores.

## Working product direction — 2026-10-07

**Working product direction; not frozen product requirements and not a change to the 0.1 goal.**

Quest Log's near-term role is not to decide the owner's life or the single correct next Quest. It should make the currently viable Quest routes clear; after the owner chooses one, it should make that Quest easy to resume and keep moving.

When an owner opens a Quest, the useful minimum understanding is:

- where the Quest is now in its progress/state;
- what the next actionable step could be;
- what may remain, be learned, or become unlocked by continuing or finishing it.

The product direction is closer to an open-world game HUD than a traditional task manager: multiple Quests may exist at once, there need not be one universally correct next Quest, and the owner keeps route-selection and trade-off authority. Once a route is selected, AI can help organize the current state and next action without turning the owner into the daily maintainer of a task system.

A Quest's possible gain is broader than a finished artifact. It may include a skill, reusable method, money, evidence, understanding, a clearer decision, elimination of a wrong direction, an unlocked option/Quest, or a portable work product. When a gain is inferred rather than demonstrated, it must remain a **hypothesis / possible gain**, not a guaranteed outcome.

Possible gain and earned growth are distinct. A possible gain is a not-yet-proven potential benefit; earned growth requires actual evidence that something was learned, built, retained, or made more transferable. One occurrence may be treated as growth evidence/a candidate. Repetition, transfer across contexts, or retention can increase confidence that the character has genuinely developed the capability. This is a working product distinction only: it does not freeze XP, levels, skill trees, reward taxonomy, or a 0.1 completion gate.

Exploration and research-system work can be valid Quest work when they leave something portable: tested understanding, a reusable method, an artifact, a decision, durable learning, or evidence useful to a later direction. **Allow exploration, but do not let exploration evaporate.**

AI may infer Quest state from evidence, propose Quest decomposition and next actions, and suggest possible gains/unlocks. These are working interpretations that should be revised through actual use; they are not permanent rules. The owner retains direction and trade-off authority, while AI may offer a usable first version before every detail is settled.

### First validation question

The first practical question is not whether the full game layer works. It is whether, on opening a Quest, the owner can quickly understand **where I am now** and **what I can do next**. Actual use should then reveal whether Quest granularity, possible gains, or additional game mechanics need refinement.

### Deliberately not frozen

This direction does not freeze main/side Quest categories, red/yellow/green/grey colours, XP, levels, skill trees, a reward taxonomy, a unique Quest granularity rule, a required split depth, an automatic priority engine, or AI choosing which Quest the owner should do. These remain future design candidates to validate, not 0.1 scope expansion or current requirements.

### Current HUD presentation decisions

The owner-approved current Web HUD reference is intentionally an open-world / WoW-like presentation, not a generic dashboard or todo list:

- Desktop is **World Map-first**; mobile is **Objective Tracker-first** and is a primary use context.
- Mobile navigation uses three entrances: 任務 / 地圖 / 角色. Quest detail is a bottom sheet showing current stage, NOW, completion/switch condition, real blocker only, NEXT, and the Quest's meaning.
- Chinese carries comprehension. Icons, numbers, and small short-English labels may add visual rhythm, but English is never a prerequisite for understanding.
- The visual language is **Modern Adventure**: dark neutral base; warm gold for active/tracked; teal for continue; blue-grey for paused; purple for unexplored/fog/candidate; red only for real blocker/danger.
- No fake XP, level, or progress bar. Profile may show only real status numbers; XP/skill/level require trustworthy earned-growth evidence first.
- Unconfirmed candidate lines use Fog of War / 迷霧 language and do not become formal Quests automatically.

The sanitized presentation reference is [`web/index.html`](web/index.html). It uses synthetic demo data only. A private authenticated deployment has been owner-verified as a presentation snapshot; it is not the live Quest data path and does not imply any 0.1 finish-line gate passed.
