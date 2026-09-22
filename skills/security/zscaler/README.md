# zscaler

Zscaler CLI (ZPA / ZIA / ZIdentity). Shared code under Meta-Skills; per-workspace `.env`.

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/zscaler"
cd ~/.meta-skills/skills/security/zscaler
~/.meta-skills/install.sh pip init .
cp .env.example "$CURRENT_SKILL_DIRECTORY/.env"   # set ZPA__* / ZIA__* / ZIDENTITY__*
python scripts/cli.py env
python scripts/cli.py zia activate status
python scripts/cli.py zia users list --page 1 --page-size 20
python scripts/cli.py zia users groups
python scripts/cli.py zia users departments --search {SEARCH}
python scripts/cli.py zia url-categories list
python scripts/cli.py zia url-cloud-apps list
python scripts/cli.py zia url-cloud-apps categories
python scripts/cli.py zia url-categories create {NAME} --url {URL}
python scripts/cli.py zia url-filtering-policy list
python scripts/cli.py zia url-filtering-policy create {NAME} --action BLOCK --category-id {CATEGORY_ID}
python scripts/cli.py zia ip-fqdn-groups list
python scripts/cli.py zia dedicated-ip-gateways list
python scripts/cli.py zia forwarding-rule list
python scripts/cli.py zia forwarding-rule create {NAME} --forward-method ENATDEDIP --gateway-name {GATEWAY_NAME}
python scripts/cli.py zpa application-segment list
python scripts/cli.py zpa application-segment get --name {SEGMENT_NAME}
python scripts/cli.py zpa application-segment update --name {SEGMENT_NAME} --domain {DOMAIN} --tcp-port 443
python scripts/cli.py zpa access-policy list
python scripts/cli.py zpa access-policy get --name {RULE_NAME}
python scripts/cli.py zpa forwarding-policy list
python scripts/cli.py zpa forwarding-policy get --name {RULE_NAME}
python scripts/cli.py zpa app-connector-group list
python scripts/cli.py zpa app-connector-group get --name {GROUP_NAME}
python scripts/cli.py zpa app-connector list
python scripts/cli.py zpa app-connector get --name {CONNECTOR_NAME}
python scripts/cli.py zpa app-connector health
```

Nested JSON keys use `__`: `{"zpa":{"client_id":"…"}}` → `ZPA__CLIENT_ID`.
