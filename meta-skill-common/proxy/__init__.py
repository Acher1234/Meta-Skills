"""Proxy settings shared by browser and http (:class:`Proxy`, defined in :mod:`common.proxy.proxy`)."""

from common.proxy.proxy import (
    DATAIMPULSE,
    DATAIMPULSE_ENV_KEYS,
    PROXY_ENV_KEYS,
    Proxy,
    dataimpulse_proxy,
    detect_proxy_type,
    resolve_proxy,
    system_proxy,
    url_proxy,
)

__all__ = [
    "DATAIMPULSE",
    "DATAIMPULSE_ENV_KEYS",
    "PROXY_ENV_KEYS",
    "Proxy",
    "dataimpulse_proxy",
    "detect_proxy_type",
    "resolve_proxy",
    "system_proxy",
    "url_proxy",
]
