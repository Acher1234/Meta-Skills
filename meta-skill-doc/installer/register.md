# Installer — register a skill

## `install.sh` (3 commands, shared cache/env only)

```bash
./install.sh fetch <git-url> [name]   # clone/pull → ~/.meta-skills/ext/<name>
./install.sh pip init [dir]           # shared venv + meta-skill-common + <dir> deps
./install.sh npm init [dir]           # <dir> node deps (shared skill dir)
```

Windows: same commands via `install.ps1`; interpreter `~/.meta-skills/.venv/Scripts/python.exe`.
The installer does **not** install skill deps: each skill runs `pip init .` / `npm init .` on first run.

## Resolve `SRC`

```bash
SRC=$(cd ~/.meta-skills && ./install.sh fetch <git-url> [name])   # external git skill
SRC=~/.meta-skills/<catalog Folder>                                # built-in, e.g. skills/mdm-antivirus/eset
# local: SRC is the given path.  <name> for DEST = basename of SRC (eset), never the category path
```

## Standard skill — TO COPY slice + library link

```bash
LIB_SKILL="$SRC/SKILL.md"; REG="$DEST/<name>/SKILL.md"; mkdir -p "$DEST/<name>"
sed -n '/^### TO COPY$/,/^##### END TO COPY$/p' "$LIB_SKILL" | sed '1d;$d' > /tmp/skill-slice.md
{
  awk '/^---$/{n++} {print} n==2{print ""; exit}' "$LIB_SKILL"   # frontmatter
  cat /tmp/skill-slice.md
  printf '\n---\n\n## Library reference\n\n'
  echo "Full commands, examples, and prerequisites — read from the shared library (updates on \`git pull\`):"
  printf '\n`%s`\n' "$LIB_SKILL"
} > "$REG"
# then substitute {IS_GLOBAL} {TYPE_OF_AI_TOOLS} {SKILL_PATH} {PROJECT_PATH} — see placeholders.md
```

Legacy skill without TO COPY markers → `cp "$LIB_SKILL" "$REG"` and substitute only.

## Meta-skill hub (`meta-{domain}/` + sub-skills)

No TO COPY, no copy of library files: write a **stub** per install (meta + each chosen sub-skill)
with `CURRENT_SKILL_DIRECTORY`, substituted placeholders (`{SKILL_PATH}` / `{META_SKILL_PATH}`) and a
library reference. Templates: `~/.meta-skills/META_SKILL_TEMPLATE.md`.

```bash
LIB=~/.meta-skills/skills/<category>/…/meta-{domain}; META_DEST="$DEST/meta-{domain}"
mkdir -p "$META_DEST" && cp "$LIB/.env.example" "$META_DEST/.env"
# write $META_DEST/SKILL.md stub → $LIB/SKILL.md; per sub-skill <id>: $DEST/<id>/SKILL.md → $LIB/sub_skills/<id>/SKILL.md
```

## Copy map

| Source (`~/.meta-skills/…`)          | Registered (`$DEST/…`)                                                  |
| ------------------------------------ | ----------------------------------------------------------------------- |
| Standard skill → `### TO COPY` slice | `$DEST/<name>/SKILL.md` = frontmatter + slice + library link            |
| Meta-skill `meta-{domain}/SKILL.md`  | `$DEST/meta-{domain}/SKILL.md` = **stub** + library link + local `.env` |
| Sub-skill `sub_skills/<id>/SKILL.md` | `$DEST/<id>/SKILL.md` = **stub** + library link                         |
| `SKILL.md` (the installer)           | **Full copy**, global-only — `~/.meta-skills/INSTALL_PROMPT.md`         |
