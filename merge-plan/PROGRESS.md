# HA Plugins Merge Progress

> **Last updated:** 2026-02-05 by Claude
> **Current phase:** 1 - Foundation & Structure
> **Overall:** 0/61 items complete

This file tracks incremental progress on merging the two plugin implementations. Each checkbox represents one commit-sized unit of work. See `ha_plugins_merge_fix_plan-v4.md` for detailed context on each item.

---

## Phase 1: Foundation & Structure (0/8)
*From merge plan sections 0.2, 2.6, 2.11, 3.2.1*

- [ ] **1.1** Fix ha-toolkit manifest homepage (currently points to wrong repo)
- [ ] **1.2** Add explicit commands/agents/skills/hooks paths to HAA manifest
- [ ] **1.3** Establish final merged plugin directory layout
- [ ] **1.4** Unify settings storage → `.claude/settings.local.json`
- [ ] **1.5** Merge hooks.json (post-edit lint + neutral deploy posture)
- [ ] **1.6** Frontmatter compliance audit - all skills (name: lowercase-hyphenated)
- [ ] **1.7** Frontmatter compliance audit - all commands
- [ ] **1.8** Frontmatter compliance audit - all agents

---

## Phase 2: Core Shared Modules (0/4)
*From merge plan section 3.3*

- [ ] **2.1** Create Resolver module (entity resolution, capability snapshots)
- [ ] **2.2** Create Editor module (YAML AST editing via ruamel.yaml or fallback)
- [ ] **2.3** Create Validator module (evidence-based, HA-backed)
- [ ] **2.4** Create Connection check procedure (reusable across commands)

---

## Phase 3: Safety Invariants Implementation (0/6)
*From merge plan section 0 (North-star invariants)*

- [ ] **3.1** Add capability snapshot requirement before emitting YAML attributes
- [ ] **3.2** Add semantic classifier (inactivity vs pure delay) to prevent timer substitution
- [ ] **3.3** Replace brittle string edits with AST editing calls
- [ ] **3.4** Add secret handling rules (never echo tokens/prefixes)
- [ ] **3.5** Add "never deploy unless requested" guards to all side-effectful commands
- [ ] **3.6** Add "what ran vs skipped" evidence tables to all validation outputs

---

## Phase 4: Skills Consolidation (0/15)
*From merge plan sections 1.1-1.16, 2.17-2.22*

- [ ] **4.1** ha-automations: Add intent classifier (inactivity vs delay)
- [ ] **4.2** ha-automations: Update YAML examples to current schema (triggers/conditions/actions)
- [ ] **4.3** ha-scripts: Add capability checks, remove implicit deploy
- [ ] **4.4** ha-scenes: Add capability checks, remove implicit deploy
- [ ] **4.5** ha-conventions: Fix tool mismatch, replace timer heuristic with classifier
- [ ] **4.6** ha-conventions: Output to `.claude/ha.conventions.json`
- [ ] **4.7** ha-troubleshooting: Make read-only, add resolver integration
- [ ] **4.8** ha-config: Fix frontmatter name, add file-target rules
- [ ] **4.9** ha-devices: Fix frontmatter, add capability snapshot contract
- [ ] **4.10** ha-jinja: Fix frontmatter, clarify where Jinja runs
- [ ] **4.11** ha-lovelace: Fix frontmatter, avoid teaching unsupported templating
- [ ] **4.12** ha-naming: Fix frontmatter, progressive disclosure (move tables to references/)
- [ ] **4.13** Consolidate YAML syntax references (automations/scenes/scripts)
- [ ] **4.14** Update log-patterns reference (resolver-first, portable)
- [ ] **4.15** Add ha-log-analyzer resolver-driven fixes

---

## Phase 5: Commands Consolidation (0/15)
*From merge plan sections 1.2-1.7, 2.5-2.16*

- [ ] **5.1** /ha-connect: Add secret safety (never print tokens), cross-platform guidance
- [ ] **5.2** /ha-connect: Prefer standard env vars (HASS_SERVER, HASS_TOKEN)
- [ ] **5.3** /ha-deploy: Add disable-model-invocation, explicit side-effect gating
- [ ] **5.4** /ha-deploy: Add resolver-driven verification (not automation.<name>)
- [ ] **5.5** /ha-rollback: Add disable-model-invocation, dry-run default
- [ ] **5.6** /ha-validate: Make evidence-first, add "what ran vs skipped" table
- [ ] **5.7** /ha-validate: Route to HA-backed validation when available
- [ ] **5.8** /ha:generate: Make thin router, move logic to skills
- [ ] **5.9** /ha:generate: Update YAML schema (ban automation: root)
- [ ] **5.10** /ha:setup: Unify with /ha-connect shared procedure
- [ ] **5.11** /ha:onboard: Merge into unified connection wizard
- [ ] **5.12** /ha:new-device: Add capability checks, naming contract integration
- [ ] **5.13** /ha:analyze: Make data-derived, require evidence for metrics
- [ ] **5.14** /ha:audit-naming: Ensure read-only, cite data sources
- [ ] **5.15** /ha:apply-naming: Add dry-run default, AST editing, disable-model-invocation

---

## Phase 6: Agents Consolidation (0/7)
*From merge plan sections 1.12, 2.8-2.10*

- [ ] **6.1** ha-entity-resolver: Standardize capability snapshot flow
- [ ] **6.2** ha-config-validator: Add evidence tables, remove python dependency
- [ ] **6.3** ha-log-analyzer: Make resolver-driven, add portable trace guidance
- [ ] **6.4** ha-naming-analyzer: Tighten tool scope (read-only), add output scaling
- [ ] **6.5** ha-convention-analyzer: Align with conventions skill
- [ ] **6.6** config-debugger: Wire into troubleshooting spine
- [ ] **6.7** device-advisor: Add mandatory capability discovery step

---

## Phase 7: Testing & Cleanup (0/6)
*From merge plan section 4*

- [ ] **7.1** Add regression test: plugin-onboarding (no secrets printed)
- [ ] **7.2** Add regression test: scene-creation (capability-checked)
- [ ] **7.3** Add regression test: simple-automation (inactivity preserved)
- [ ] **7.4** Add regression test: ambiguous-entity (resolver + gating)
- [ ] **7.5** Add regression test: complex-automation (helper creation)
- [ ] **7.6** Final cleanup: remove duplicate files, update README

---

## Notes

### How to use this file
1. Claude reads this file at the start of each session
2. Work proceeds on the first unchecked item in the current phase
3. Each completed item = one git commit
4. Update the "Last updated" header and phase counts after each item

### Commit message format
```
merge: <item-id> <short description>

Addresses item X.Y from PROGRESS.md
```

### If blocked
Add a note under the item explaining the blocker, then move to the next item. Example:
```
- [ ] **1.3** Establish final merged plugin directory layout
  > BLOCKED: Need decision on whether to keep both plugin folders or flatten
```
