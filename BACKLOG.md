# Backlog

Ideas, optimizations, and future considerations. Not urgent — revisit when time allows.

---

## Ideas

- [ ] **Use cheaper/faster models for subagents.** Entity resolver, config validator, and other subagents may work fine with Haiku or lower temperature settings. Could reduce cost and latency significantly (e.g., resolver went from 54s to 24s just by fixing docs — model choice could cut further). Need to investigate whether Claude Code plugin agents support model/temperature overrides in frontmatter.

- [ ] **Edit uniqueness guidance for repeated YAML blocks.** When editing files with multiple scenes/automations/scripts, the model's `old_string` often matches multiple blocks (e.g., same entity in multiple scenes). Skills need guidance to include surrounding context (scene name, automation alias) to make edits unique. Observed in B1 test: `light.entryway_chandelier` matched 3 times in scenes.yaml. Could add to ha-scenes, ha-automations, ha-scripts skill docs, or to a shared editing reference.

---

## Notes

_(Observations worth remembering but not actionable yet)_
