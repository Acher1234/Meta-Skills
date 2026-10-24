# Installer — copy-time placeholders

Each built-in skill's library `SKILL.md` has a `### TO COPY` … `##### END TO COPY` block.
Registration copies **only** that slice into `$DEST/<name>/SKILL.md`, substitutes placeholders,
then appends a **library reference** so `git pull` on `~/.meta-skills` refreshes commands without
re-registering.

```
IS_GLOBAL => {IS_GLOBAL}                 # TRUE if tool-global, else FALSE
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}   # CURSOR / HERMES / OPENCODE / OPENCLAW / CLAUDE
SKILL_PATH => {SKILL_PATH}               # dir of the registered SKILL.md (see below)
PROJECT_PATH => {PROJECT_PATH}           # main project folder — only in skills that use it
```

## `{SKILL_PATH}` value (portable across users)

| Install | `{SKILL_PATH}` becomes | Example |
|---------|------------------------|---------|
| **Project** scope **and** `$PWD` inside a git repo | `$(git rev-parse --show-toplevel)/<DEST relative to git root>/<name>` (kept **literal**) | `$(git rev-parse --show-toplevel)/.claude/skills/godaddy` |
| **Global** scope (root skill dirs, Hermes) **or** no git repo | absolute path of `$DEST/<name>` | `/Users/you/.claude/skills/godaddy` |

`$(git rev-parse --show-toplevel)` is **not** expanded at install time: the Working directory block
evaluates it at run time, so a committed `SKILL.md` works for every teammate (bash/zsh and PowerShell).
Always the **destination** dir, never the library path under `~/.meta-skills/skills/…`.

```bash
if GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ "$SCOPE" = project ]; then
  REL=$(cd "$DEST/<name>" && pwd -P); REL=${REL#"$(cd "$GIT_ROOT" && pwd -P)/"}
  SKILL_PATH_VALUE='$(git rev-parse --show-toplevel)/'"$REL"
else
  SKILL_PATH_VALUE=$(cd "$DEST/<name>" && pwd -P)
fi
```

## `{PROJECT_PATH}` value (main project folder)

Only for skills whose slice has `PROJECT_PATH => {PROJECT_PATH}` (e.g. `folder-crypt` resolves
relative paths from it, `jewish-calendar` downloads into it). Kept **literal**, evaluated at run time:

| Install | `{PROJECT_PATH}` becomes |
|---------|--------------------------|
| **Project** scope **and** `$PWD` inside a git repo | `$(git rev-parse --show-toplevel)` |
| **Global** scope **or** no git repo | `$PWD` (folder the agent runs from) |

Never the skill dir: `{PROJECT_PATH}` is where the user's files are, `{SKILL_PATH}` is where the `.env` is.

Project scope inside git: append to the project `.gitignore` (if missing) `.<tool>/skills/*/.env`
plus the skill's token files (e.g. `google_token.json`, `.bw-appdata/`).

The slice has a **bash/zsh** and a **PowerShell** variant — keep both:

```bash
export CURRENT_SKILL_DIRECTORY="$(git rev-parse --show-toplevel)/.cursor/skills/google-workspace"
export IS_GLOBAL="FALSE"
export TYPE_OF_AI_TOOLS="CURSOR"
```

```powershell
$env:CURRENT_SKILL_DIRECTORY = "{SKILL_PATH}"
$env:IS_GLOBAL = "{IS_GLOBAL}"
$env:TYPE_OF_AI_TOOLS = "{TYPE_OF_AI_TOOLS}"
```

## Library reference (appended after the slice)

```markdown
---

## Library reference

Full commands, examples, and prerequisites — read from the shared library (updates on `git pull`):

`~/.meta-skills/skills/<category>/…/<name>/SKILL.md`
```

Agents read that library path for slash commands; the registered file only holds credentials
context + placeholders.
