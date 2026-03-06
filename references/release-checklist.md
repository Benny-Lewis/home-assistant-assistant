# Release Checklist

Complete this checklist **before tagging any release**.

## 1) Docs and command syntax parity

- [ ] Any command syntax changes are reflected in all README command examples.
- [ ] README examples were spot-checked by running or validating the updated command forms.

## 2) Hook/runtime assumptions verified

- [ ] Hook and runtime assumptions are still correct (for example: bash scripts run in bash, JS/Node hooks run in Node).
- [ ] `hooks/hooks.json` and referenced scripts were reviewed for runtime compatibility after command or tooling changes.

## 3) Project metadata and inventory updates

- [ ] `CHANGELOG.md` includes a release-ready summary of user-visible changes.
- [ ] Component inventory docs are updated when needed (`CLAUDE.md`, `COMPONENTS.md`, skill/agent listings).

## 4) Breaking wording flag

Set this flag during release prep and carry it into release notes/changelog:

- [ ] **Breaking wording:** `YES` / `NO`
  - Mark `YES` if there are install command renames (for example installation flow command names changed).
  - Mark `YES` if there are skill command renames (slash command changes, renamed skill entrypoints).
  - If `YES`, add a clearly labeled **Breaking Changes** section to the changelog/release notes with migration guidance.

## Release gate

- [ ] Checklist fully completed before creating or pushing a release tag.
