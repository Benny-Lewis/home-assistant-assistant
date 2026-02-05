# Claude Code docs (external snapshot)

This folder contains a local snapshot of selected documentation pages from `code.claude.com` so they can be searched, referenced, and used offline.

## Structure

- `skills/skills.md` — overview of Agent Skills in Claude Code
- `docs/` — additional Claude Code pages (CLI, slash commands, plugins, hooks, etc.)

## Refresh / Update

From the repo root:

```bash
# Skills overview
mkdir -p docs/external/claude-code/skills
curl -L "https://code.claude.com/docs/en/skills.md" \
  -o docs/external/claude-code/skills/skills.md

# Selected docs pages
mkdir -p docs/external/claude-code/docs
base="https://code.claude.com/docs/en"
for page in \
  cli-reference \
  slash-commands \
  plugins-reference \
  hooks \
  common-workflows \
  sub-agents \
  settings \
  memory \
  statusline
do
  echo "Downloading $page.md"
  curl -L "$base/$page.md" -o "docs/external/claude-code/docs/$page.md"
done

