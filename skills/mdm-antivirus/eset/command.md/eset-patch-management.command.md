# eset-patch-management — Commands

API docs: [Patch Management](https://help.eset.com/eset_connect/en-US/patch_management.html)

### API gateway

`ESET_PATCH_URL` — `https://<region>.patch-management.eset.systems` (from `ESET_URL` unless overridden).

`patches apply` uses the Automation gateway (`ApplyApplicationPatch`), same as `/eset_tasks_apply-patch`.

| Slash | CLI | Notes |
|-------|-----|--------|
| `/eset_patches_list` | `python cli.py patches list [--device UUID] [--group UUID] [--patch-type PATCH_TYPE_APPLICATION\|…] [--page-size N]` | pending patches |
| `/eset_patches_recent` | `python cli.py patches recent` | recent app patching details |
| `/eset_patches_details` | `python cli.py patches details [--page-size N]` | process details |
| `/eset_patches_apply` | `python cli.py patches apply --device UUID --application-uuid UUID [--display-name N] [--expire-time RFC3339]` | Automation `ApplyApplicationPatch` |

**UUID mapping:** from `patches list`, use `devices[].uuid` as `--application-uuid` (same as `applicationUuid` in `patches recent` / `patches details`). It is not the device UUID. Prefer `--device` on list (unfiltered can timeout) and `--expire-time` on apply. Confirm target app + device with the user before applying. Equivalent: `/eset_tasks_apply-patch`.
