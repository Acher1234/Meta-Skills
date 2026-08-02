# Meta-Skills — install prompt

Copy-paste the block below into a fresh Cursor / Claude Code / Hermes agent chat. It installs
the **`meta-skills`** meta-skill (the installer itself) into your **global** skills folder,
so that `/meta-skills` becomes available everywhere.

- Repo: <https://github.com/Acher1234/Meta-Skills.git>
- Shared library: `~/.meta-skills`
- Meta-skill installed: `meta-skills` → `<global skills dir>/meta-skills/SKILL.md`

---

## Prompt (paste this)

```
Install the "meta-skills" meta-skill into my GLOBAL skills folder.

0. Detect the tool from the RUNNING agent's env vars (not ~/.cursor / ~/.claude presence):
   - $CLAUDECODE / $CLAUDE_CODE_ENTRYPOINT set -> Claude Code -> ~/.claude/skills/meta-skills/SKILL.md
   - $TERMINAL_ENV non-empty                   -> Hermes      -> ~/.hermes/skills/meta-skills/SKILL.md
   - $CURSOR_AGENT / $CURSOR_TRACE_ID set       -> Cursor      -> ~/.cursor/skills/meta-skills/SKILL.md
   - none / ambiguous                          -> ask "Cursor / Claude Code / Hermes global?".

1. Clone or update the shared library:
     REPO=https://github.com/Acher1234/Meta-Skills.git
     LIB=~/.meta-skills
     if [ -d "$LIB/.git" ]; then git -C "$LIB" pull --ff-only; else git clone "$REPO" "$LIB"; fi

2. Register ONLY the meta-skill's SKILL.md into the chosen global folder:
     # Cursor global:
     mkdir -p ~/.cursor/skills/meta-skills && cp "$LIB/SKILL.md" ~/.cursor/skills/meta-skills/SKILL.md
     # OR Claude Code global:
     mkdir -p ~/.claude/skills/meta-skills && cp "$LIB/SKILL.md" ~/.claude/skills/meta-skills/SKILL.md
     # OR Hermes global:
     mkdir -p ~/.hermes/skills/meta-skills && cp "$LIB/SKILL.md" ~/.hermes/skills/meta-skills/SKILL.md

3. Confirm the file exists, then tell me to reload Cursor / Claude Code (or restart the Hermes
   agent) and run /meta-skills to install any other skill.

Do NOT copy other skills yet — just the installer. /meta-skills handles the rest
(including placeholder substitution {IS_GLOBAL}, {TYPE_OF_AI_TOOLS}, {SKILL_PATH} on skill copies).
```

---

## One-liners (if you prefer to run it yourself)

**Cursor — global** (`~/.cursor/skills/`):

```bash
REPO=https://github.com/Acher1234/Meta-Skills.git; LIB=~/.meta-skills
[ -d "$LIB/.git" ] && git -C "$LIB" pull --ff-only || git clone "$REPO" "$LIB"
mkdir -p ~/.cursor/skills/meta-skills && cp "$LIB/SKILL.md" ~/.cursor/skills/meta-skills/SKILL.md
```

**Claude Code — global** (`~/.claude/skills/`):

```bash
REPO=https://github.com/Acher1234/Meta-Skills.git; LIB=~/.meta-skills
[ -d "$LIB/.git" ] && git -C "$LIB" pull --ff-only || git clone "$REPO" "$LIB"
mkdir -p ~/.claude/skills/meta-skills && cp "$LIB/SKILL.md" ~/.claude/skills/meta-skills/SKILL.md
```

**Hermes — global** (`~/.hermes/skills/`):

```bash
REPO=https://github.com/Acher1234/Meta-Skills.git; LIB=~/.meta-skills
[ -d "$LIB/.git" ] && git -C "$LIB" pull --ff-only || git clone "$REPO" "$LIB"
mkdir -p ~/.hermes/skills/meta-skills && cp "$LIB/SKILL.md" ~/.hermes/skills/meta-skills/SKILL.md
```

Then reload Cursor / Claude Code (or restart the Hermes agent) and run `/meta-skills` to
install/refresh the rest of the catalog.
