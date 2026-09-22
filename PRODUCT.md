# Product definition

Quest Log recovers useful Quest state from evidence instead of asking the owner to maintain another task system.

## 0.1 goal

After normal work, recover and show: Quests, current stage/state, the actionable next step, and blockers only for real stop conditions.

## Conceptual architecture

`Evidence Sources → Reconciler → Quest State → Read API → HUD`

This is conceptual for 0.1, not a permanent architecture freeze. Quest Log is not a manual task manager, percentage engine, autonomous new-Quest generator, or replacement for private runtime stores.
