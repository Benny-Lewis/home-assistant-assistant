# Claude Platform docs (external snapshot)

This folder contains a local snapshot of selected documentation pages from `platform.claude.com`.
These are primarily useful for conceptual/background context, not Claude Code CLI specifics.

## Structure

- `agent-skills/overview.md` — high-level “What are Skills?” overview
- `agent-skills/_assets/images/` — images downloaded locally and linked from the markdown

## Refresh / Update

From the repo root:

~~~bash
mkdir -p docs/external/claude-platform/agent-skills
curl -L "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md" \
  -o docs/external/claude-platform/agent-skills/overview.md
~~~

## Sync embedded images

If the markdown contains site-relative image links like `![](/docs/images/...)`,
download them locally and rewrite links to `./_assets/images/...`:

~~~bash
cd docs/external/claude-platform/agent-skills
base="https://platform.claude.com"
assets="_assets/images"
mkdir -p "$assets"

grep -rhoE '!\[[^]]*\]\((/[^)]+)\)' ./*.md \
  | sed -E 's/.*\((\/[^)]+)\).*/\1/' \
  | sort -u \
  | while read -r path; do
      file="$(basename "$path")"
      dest="$assets/$file"
      [ -f "$dest" ] || curl -L "$base$path" -o "$dest"
      sed -i "s#($path)#(./$assets/$file)#g" ./*.md
    done
~~~
