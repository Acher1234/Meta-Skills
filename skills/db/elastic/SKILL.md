---
name: elastic
description: >-
  Elasticsearch cluster via a Python CLI (basic auth). Ping, cluster health,
  and list indices. Use when the user mentions Elasticsearch, Elastic, an
  ES cluster, or invokes /elastic_*.
disable-model-invocation: true
---

### TO COPY

# elastic

Per-workspace registration slice. Credentials live in `{SKILL_PATH}/.env`.

## Working directory

Placeholders changed by `/meta-skills` at copy time (NAME => {PLACEHOLDER}):

IS_GLOBAL => {IS_GLOBAL}
TYPE_OF_AI_TOOLS => {TYPE_OF_AI_TOOLS}
SKILL_PATH => {SKILL_PATH}

```bash
export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"
~/.meta-skills/.venv/bin/python ~/.meta-skills/skills/db/elastic/scripts/cli.py env
```

##### END TO COPY

# elastic

Elasticsearch REST API via the official Python client ([docs](https://www.elastic.co/docs/api/doc/elasticsearch)). Auth: HTTP basic (`USERNAME` / `PASSWORD`) against `URL`.

## When to use

Trigger phrases: "Elasticsearch", "Elastic cluster", "list ES indices", "cluster health", `/elastic_*`.

`skill_env.py` loads `.env` via SkillCred — do not `source` it in the shell. `CURRENT_SKILL_DIRECTORY` is the only required export.

Prefer `~/.meta-skills/.venv/bin/python` from `~/.meta-skills/skills/db/elastic/`.

## Credentials — SkillCred `.env`

`.env` is next to the **registered** skill, resolved by `SkillCred("elastic", [".env"])`.

| Variable | Notes |
|----------|--------|
| `URL` | Cluster URL (`https://localhost:9200` or Elastic Cloud endpoint) |
| `USERNAME` | Basic-auth user |
| `PASSWORD` | Basic-auth password |

```bash
cp ~/.meta-skills/skills/db/elastic/.env.example "{SKILL_PATH}/.env"
# edit URL / USERNAME / PASSWORD
python scripts/cli.py env
```

First deps: `cd ~/.meta-skills/skills/db/elastic && ~/.meta-skills/install.sh pip init .`

Local self-signed certs (localhost / 127.0.0.1) skip TLS verify. Elastic Cloud keeps verify on.

## Slash commands

Map `/elastic_<…>` → `python scripts/cli.py …`; return JSON.

| Slash | CLI | Description |
|-------|-----|-------------|
| `/elastic_env` | `python scripts/cli.py env` | Validate `.env` (no network) |
| `/elastic_ping` | `python scripts/cli.py ping` | `GET /` cluster info |
| `/elastic_health` | `python scripts/cli.py health` | Cluster health |
| `/elastic_indices_list` | `python scripts/cli.py indices list` | List indices |
| `/elastic_indices_fields` | `python scripts/cli.py indices fields INDEX` | List field paths + types |

## How to run

1. `export CURRENT_SKILL_DIRECTORY="{SKILL_PATH}"` then `cd ~/.meta-skills/skills/db/elastic`.
2. Ensure `.env` exists next to the registered skill; `/elastic_env`.
3. Map `/elastic_<…>` → `~/.meta-skills/.venv/bin/python scripts/cli.py …`; return JSON.

## Notes

- Confirm with the user before destructive index/document writes (none in this CLI yet).
- Never commit `.env` or echo `PASSWORD`.
- Docs: [Elasticsearch Python client](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html).
