# Installer — examples

```bash
cd ~/.meta-skills

# Built-in → Hermes (all profiles); SRC is nested, DEST flat by basename
LIB=~/.meta-skills/skills/productivity/google/google-workspace/SKILL.md
REG=~/.hermes/skills/google-workspace/SKILL.md; mkdir -p "$(dirname "$REG")"
# slice + frontmatter + library link → $REG (register.md)
# IS_GLOBAL=TRUE, TYPE_OF_AI_TOOLS=HERMES, SKILL_PATH=$HOME/.hermes/skills/google-workspace

# External git skill → Claude (global): fetch once, then register
SRC=$(./install.sh fetch https://github.com/some/cool-skill.git cool-skill)
REG=~/.claude/skills/cool-skill/SKILL.md; mkdir -p "$(dirname "$REG")"

# Same skill → Cursor (this project), no re-clone
# IS_GLOBAL=FALSE, TYPE_OF_AI_TOOLS=CURSOR, SKILL_PATH='$(git rev-parse --show-toplevel)/.cursor/skills/cool-skill'

# Same skill → OpenCode (this project) / global: ${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/skills/cool-skill
# IS_GLOBAL=FALSE, TYPE_OF_AI_TOOLS=OPENCODE, SKILL_PATH='$(git rev-parse --show-toplevel)/.opencode/skills/cool-skill'

# The skill installs its OWN deps on first run (shared venv + common)
./install.sh pip init "$SRC"
```

After install: CLIs run from `~/.meta-skills/skills/…` (or `ext/<name>`) with
`~/.meta-skills/.venv/bin/python`; credentials resolve under `$CURRENT_SKILL_DIRECTORY`. `git pull`
refreshes library `SKILL.md` bodies in place; re-run `/meta-skills` to add or re-register skills.
