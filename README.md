# Quest Log

Quest Log is an AI-native work HUD, not a manual task manager. Evidence updates Quest state; the HUD shows what exists, where it is, and what to do next.

This is the public, self-hostable/reference home. Version 0.1 is a shareable reference implementation, not a polished zero-config product.

- [Product](PRODUCT.md)
- [0.1 roadmap](ROADMAP.md)
- [Current state](CURRENT_STATE.md)
- [Privacy boundary](PRIVACY.md)
- [Lifecycle](LIFECYCLE.md)
- [HUD runtime contract](docs/hud-runtime-contract.md)
- [Sanitized current HUD Worker](runtime/quest-log-private-worker.js)
- [Synthetic HUD read fixture](fixtures/hud-read-v1.json)
- [Reference HUD code](src/quest_hud/)
- [Current Web HUD presentation reference](web/index.html) (sanitized, synthetic demo data)

Run the sanitized reference tests with `python -m pytest src/quest_hud/test_final_xp_zone.py`.
