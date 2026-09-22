"""ZPA application segments — list, get, update (ports / domains), delete."""

from __future__ import annotations

import argparse
from typing import Any

from zpa.client import ZpaClient
from zscaler.zpa.application_segment import ApplicationSegmentAPI

_PASSTHROUGH = (
    "description",
    "enabled",
    "bypass_type",
    "health_check_type",
    "health_reporting",
    "icmp_access_type",
    "ip_anchored",
    "is_cname_enabled",
    "double_encrypt",
    "passive_health_enabled",
    "tcp_keep_alive",
    "match_style",
    "select_connector_close_to_app",
    "bypass_on_reauth",
    "inspect_traffic_with_zia",
    "fqdn_dns_check",
)


class ApplicationSegmentClient(ZpaClient):
    @staticmethod
    def _api(client: Any) -> Any:
        zpa_svc = client.zpa
        api = getattr(zpa_svc, "application_segment", None)
        if api is not None:
            return api
        return ApplicationSegmentAPI(zpa_svc.request_executor, zpa_svc.config)

    @staticmethod
    def _clean_values(values: list[str] | None) -> list[str]:
        return [str(v).strip() for v in (values or []) if str(v).strip()]

    @staticmethod
    def _parse_port(raw: str) -> dict[str, str]:
        value = (raw or "").strip()
        if not value:
            raise ValueError("port must not be empty")
        sep = "-" if "-" in value else (":" if ":" in value else None)
        if sep:
            left, right = value.split(sep, 1)
            start, end = left.strip(), right.strip()
        else:
            start = end = value
        for part in (start, end):
            if not part.isdigit() or not 1 <= int(part) <= 65535:
                raise ValueError(f"invalid port {raw!r}; expected 1-65535 or FROM-TO")
        if int(start) > int(end):
            raise ValueError(f"invalid port range {raw!r}; FROM must be <= TO")
        return {"from": start, "to": end}

    @staticmethod
    def _parse_ports(values: list[str] | None) -> list[dict[str, str]]:
        return [ApplicationSegmentClient._parse_port(v) for v in ApplicationSegmentClient._clean_values(values)]

    @staticmethod
    def _pairs_from_flat(values: list[Any] | None) -> list[dict[str, str]]:
        items = [str(v).strip() for v in (values or []) if str(v).strip()]
        pairs: list[dict[str, str]] = []
        for i in range(0, len(items), 2):
            start = items[i]
            end = items[i + 1] if i + 1 < len(items) else items[i]
            pairs.append({"from": start, "to": end})
        return pairs

    @staticmethod
    def _port_ranges(current: dict[str, Any], structured_key: str, flat_key: str) -> list[dict[str, str]]:
        structured = current.get(structured_key) or []
        ranges: list[dict[str, str]] = []
        for item in structured:
            if isinstance(item, dict) and item.get("from") is not None:
                ranges.append({"from": str(item["from"]), "to": str(item.get("to") or item["from"])})
        if ranges:
            return ranges
        return ApplicationSegmentClient._pairs_from_flat(current.get(flat_key))

    @staticmethod
    def _merge_ranges(
        current: list[dict[str, str]], incoming: list[dict[str, str]], append: bool
    ) -> list[dict[str, str]]:
        if not incoming:
            return current
        if not append:
            return incoming
        seen = {(r["from"], r["to"]) for r in current}
        merged = list(current)
        for item in incoming:
            key = (item["from"], item["to"])
            if key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    @staticmethod
    def _server_group_ids(current: dict[str, Any]) -> list[str]:
        ids: list[str] = []
        for group in current.get("server_groups") or []:
            gid = group.get("id") if isinstance(group, dict) else group
            if gid is not None and str(gid).strip():
                ids.append(str(gid).strip())
        return ids

    def _payload_from_current(self, current: dict[str, Any]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": current.get("name"),
            "domain_names": list(current.get("domain_names") or []),
            "segment_group_id": current.get("segment_group_id"),
            "server_group_ids": self._server_group_ids(current),
            "tcp_port_range": self._port_ranges(current, "tcp_port_range", "tcp_port_ranges"),
            "udp_port_range": self._port_ranges(current, "udp_port_range", "udp_port_ranges"),
        }
        for key in _PASSTHROUGH:
            value = current.get(key)
            if value is not None:
                payload[key] = value
        return payload

    def list_segments(self, search: str | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        page = 1
        page_size = 500
        with self.get_client() as client:
            api = self._api(client)
            while True:
                query_params: dict[str, Any] = {
                    "page": str(page),
                    "page_size": str(page_size),
                }
                if search and search.strip():
                    query_params["search"] = search.strip()
                segments, _, err = api.list_segments(query_params=query_params)
                if err:
                    raise RuntimeError(f"Failed to list application segments: {err}")
                batch = [self._to_dict(segment) for segment in (segments or [])]
                results.extend(batch)
                if len(batch) < page_size:
                    break
                page += 1
        return results

    def get_segment(
        self,
        *,
        segment_id: str | None = None,
        segment_name: str | None = None,
    ) -> dict[str, Any]:
        if segment_id is not None and str(segment_id).strip():
            sid = str(segment_id).strip()
            with self.get_client() as client:
                segment, _, err = self._api(client).get_segment(sid)
                if err:
                    raise RuntimeError(f"Failed to get application segment {sid}: {err}")
                if segment is None:
                    raise RuntimeError(f"Application segment not found: {sid}")
                return self._to_dict(segment)

        if not segment_name or not segment_name.strip():
            raise ValueError("segment_id or segment_name is required")

        needle = segment_name.strip().casefold()
        matches = [
            segment
            for segment in self.list_segments(segment_name.strip())
            if str(segment.get("name") or "").casefold() == needle
        ]
        if not matches:
            matches = [
                segment
                for segment in self.list_segments()
                if str(segment.get("name") or "").casefold() == needle
            ]
        if not matches:
            raise RuntimeError(f"Application segment not found: {segment_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(segment.get("id")) for segment in matches)
            raise RuntimeError(
                f"multiple application segments named {segment_name!r}: {ids}"
            )
        return matches[0]

    def update_segment(
        self,
        *,
        segment_id: str | None = None,
        segment_name: str | None = None,
        domains: list[str] | None = None,
        tcp_ports: list[str] | None = None,
        udp_ports: list[str] | None = None,
        append: bool = False,
    ) -> dict[str, Any]:
        incoming_domains = None if domains is None else self._clean_values(domains)
        incoming_tcp = None if tcp_ports is None else self._parse_ports(tcp_ports)
        incoming_udp = None if udp_ports is None else self._parse_ports(udp_ports)

        if incoming_domains is None and incoming_tcp is None and incoming_udp is None:
            raise ValueError("at least one of --domain, --tcp-port, --udp-port is required")
        if incoming_domains is not None and not incoming_domains:
            raise ValueError("at least one --domain is required")
        if incoming_tcp is not None and not incoming_tcp:
            raise ValueError("at least one --tcp-port is required")
        if incoming_udp is not None and not incoming_udp:
            raise ValueError("at least one --udp-port is required")

        current = self.get_segment(segment_id=segment_id, segment_name=segment_name)
        sid = str(current["id"])
        kwargs = self._payload_from_current(current)

        if incoming_domains is not None:
            if append:
                existing = [str(d) for d in (kwargs.get("domain_names") or [])]
                seen = {d.casefold() for d in existing}
                merged = list(existing)
                for domain in incoming_domains:
                    if domain.casefold() not in seen:
                        seen.add(domain.casefold())
                        merged.append(domain)
                kwargs["domain_names"] = merged
            else:
                kwargs["domain_names"] = incoming_domains

        if incoming_tcp is not None:
            kwargs["tcp_port_range"] = self._merge_ranges(
                kwargs.get("tcp_port_range") or [], incoming_tcp, append
            )
        if incoming_udp is not None:
            kwargs["udp_port_range"] = self._merge_ranges(
                kwargs.get("udp_port_range") or [], incoming_udp, append
            )

        if not kwargs.get("domain_names"):
            raise ValueError("application segment must keep at least one domain / IP")
        if not kwargs.get("tcp_port_range") and not kwargs.get("udp_port_range"):
            raise ValueError("application segment must keep at least one TCP or UDP port")
        if not kwargs.get("name"):
            raise RuntimeError(f"Application segment {sid} is missing a name")
        if not kwargs.get("segment_group_id"):
            raise RuntimeError(f"Application segment {sid} is missing segment_group_id")
        if not kwargs.get("server_group_ids"):
            raise RuntimeError(f"Application segment {sid} is missing server_groups")

        with self.get_client() as client:
            updated, _, err = self._api(client).update_segment(sid, **kwargs)
            if err:
                raise RuntimeError(f"Failed to update application segment {sid}: {err}")
            payload = self._to_dict(updated)
        if payload.get("id"):
            return payload
        return self.get_segment(segment_id=sid)

    def delete_segment(
        self,
        *,
        segment_id: str | None = None,
        segment_name: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        current = self.get_segment(segment_id=segment_id, segment_name=segment_name)
        sid = str(current["id"])
        with self.get_client() as client:
            _, _, err = self._api(client).delete_segment(sid, force_delete=force)
            if err:
                raise RuntimeError(f"Failed to delete application segment {sid}: {err}")
        return {"deleted": True, "id": sid, "name": current.get("name")}

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(self.list_segments(search=args.search or None))
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_segment(
                segment_id=args.id or None,
                segment_name=args.name or None,
            )
        )
        return None

    def cmd_update(self, args: argparse.Namespace) -> None:
        self.dump(
            self.update_segment(
                segment_id=args.id or None,
                segment_name=args.name or None,
                domains=args.domain,
                tcp_ports=args.tcp_port,
                udp_ports=args.udp_port,
                append=bool(args.append),
            )
        )
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(
            self.delete_segment(
                segment_id=args.id or None,
                segment_name=args.name or None,
                force=bool(args.force),
            )
        )
        return None

    @staticmethod
    def _add_segment_ref(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", help="Segment id")
        parser.add_argument("--name", help="Exact segment name")

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = ApplicationSegmentClient()
        p = sub.add_parser(
            "application-segment", help="ZPA application segments"
        )
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", help="List segments")
        u_list.add_argument("--search", default="", help="Filter by name")
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", help="Get a segment")
        ApplicationSegmentClient._add_segment_ref(u_get)
        u_get.set_defaults(func=client.cmd_get)

        u_update = cmds.add_parser(
            "update", help="Update ports and domains / IPs"
        )
        ApplicationSegmentClient._add_segment_ref(u_update)
        u_update.add_argument(
            "--domain",
            action="append",
            help="IP, FQDN, or URL (repeatable; replaces unless --append)",
        )
        u_update.add_argument(
            "--tcp-port",
            action="append",
            help="TCP port or FROM-TO range (repeatable; replaces unless --append)",
        )
        u_update.add_argument(
            "--udp-port",
            action="append",
            help="UDP port or FROM-TO range (repeatable; replaces unless --append)",
        )
        u_update.add_argument(
            "--append",
            action="store_true",
            help="Append --domain / --tcp-port / --udp-port instead of replacing",
        )
        u_update.set_defaults(func=client.cmd_update)

        u_del = cmds.add_parser("delete", help="Delete a segment")
        ApplicationSegmentClient._add_segment_ref(u_del)
        u_del.add_argument(
            "--force",
            action="store_true",
            help="Unmap from segment group before delete",
        )
        u_del.set_defaults(func=client.cmd_delete)
