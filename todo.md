# TODO

## SKILL.md token budget (CI + pre-commit)

Add automated checks so every `SKILL.md` stays under a token limit.

### Scope

- Scan all `**/*.md` in the repo (root installer + `skills/**`).
- Fail if estimated tokens exceed the configured limit.
- Optional: different limits per file type (e.g. root `SKILL.md` vs registered slice `### TO COPY` only).

### Suggested limits (to tune)

| File | Max tokens (estimate) |
|------|------------------------|
| Root `SKILL.md` (meta-skills installer) | 2500 |
| Standard skill library `SKILL.md` | 2000 |
| `### TO COPY` slice only | 500 |

---

## Python linter (CI + pre-commit)

Add a shared Python lint/format setup for `meta-skill-common/` and skill scripts under `skills/**`.

### Scope

- Pick one stack (e.g. **ruff** for lint + format, or **ruff** + **mypy** if type-checking is wanted).
- Config at repo root (`pyproject.toml` or `ruff.toml`) with sensible defaults for scripts/CLIs.
- **Pre-commit** — run on staged `.py` files (fast).
- **GitHub Action** — full-tree check on `pull_request` / `push` to `main`.
- Document how to run locally (`ruff check`, `ruff format --check`, etc.) in README or `setup.sh` output.

### Notes

- Respect existing style where possible; avoid a huge one-shot reformat unless agreed.
- Exclude vendored/generated paths if any appear later.

---

## Project dependencies

Centralize and document repo-wide dependencies (installer, shared venv, skills).

### Scope

- Root **`dependencies.md`** (or `project-dependencies.md`) listing:
  - shared Python packages (`meta-skill-common`, root `requirements` if any)
  - global npm tools used by the installer
  - system prerequisites (`git`, `python3`, `gitleaks`, etc.)
- Per-skill: keep or align existing `dependencies.md` / `requirements.txt` with a common template.
- Optional: script or CI check that `requirements.txt` files match what `install.sh pip init` expects.
- Link from root `README.md` / `SKILL.md` installer docs.

---

## License (repo + skills)

Make the PolyForm Noncommercial license visible and consistent across the project.

### Scope

- Root **`LICENSE`** is done — keep as source of truth.
- Add a short **License** blurb to root `SKILL.md` installer (and templates: `SKILL_TEMPLATE.md`, `ORIGIN_TEMPLATE.md`).
- Per-skill: optional `LICENSE` symlink or one-line pointer in `README.md` / `ORIGIN.md` (“same license as Meta-Skills root”).
- Optional: SPDX header in shared Python modules (`SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0`).
- Document commercial licensing contact path in README if offering paid use later.

