# ha-naming — Anti-Patterns and Migration Strategy

Naming mistakes to avoid and the path to correct them.

## Anti-Patterns to Avoid

| Bad | Good | Why |
|-----|------|-----|
| `light.light_1` | `light.living_room_ceiling` | Generic names are meaningless |
| `light.lr_cl_1` | `light.living_room_ceiling_1` | Abbreviations without context |
| `light.living_room_main_ceiling_light_above_couch` | `light.living_room_ceiling_main` | Overly long |
| Mixed patterns across entities | Consistent pattern everywhere | Inconsistency creates confusion |

## Migration Strategy

When renaming existing entities:

1. **Audit current naming**: Use `/ha-naming`
2. **Choose convention**: Pick pattern that fits majority
3. **Plan changes**: Use `/ha-naming`
4. **Update dependencies**: Find all references in automations/scripts
5. **Execute carefully**: Use `/ha-apply-naming`
6. **Test thoroughly**: Verify automations work
