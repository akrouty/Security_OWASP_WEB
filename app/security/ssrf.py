# app/security/ssrf.py
from __future__ import annotations
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Iterable

import httpx
from fastapi import HTTPException, status

from app.security.settings import (
    OUTBOUND_ALLOW_HOSTS,
    OUTBOUND_BLOCK_PRIVATE,
    OUTBOUND_ALLOWED_PORTS,
)

SAFE_SCHEMES = {"http", "https"}

def _host_is_allowed(host: str, allow: Iterable[str]) -> bool:
    if not allow:
        # If allow-list is empty, deny by default (safer)
        return False
    host = host.lower()
    for entry in allow:
        e = entry.lower()
        if host == e:
            return True
        if e.startswith(".") and host.endswith(e):
            return True
    return False

def _addr_is_private(addr: str) -> bool:
    ip = ipaddress.ip_address(addr)
    return any([
        ip.is_private,
        ip.is_loopback,
        ip.is_link_local,
        ip.is_reserved,
        ip.is_multicast,
        ip.is_unspecified,
    ])

def _resolve_all(host: str) -> list[str]:
    # Get all A/AAAA records
    addrs: list[str] = []
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            infos = socket.getaddrinfo(host, None, family, socket.SOCK_STREAM)
            for _family, _type, _proto, _canon, sockaddr in infos:
                addrs.append(sockaddr[0])
        except socket.gaierror:
            continue
    return list(dict.fromkeys(addrs))  # dedupe, preserve order

def validate_outbound_url(raw_url: str) -> tuple[str, str, int]:
    """
    Returns (scheme, host, port) if ok; raises HTTPException otherwise.
    """
    try:
        parsed = urlparse(raw_url)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid URL")

    if parsed.scheme not in SAFE_SCHEMES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Scheme not allowed")

    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port not in OUTBOUND_ALLOWED_PORTS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Port not allowed")

    if not _host_is_allowed(host, OUTBOUND_ALLOW_HOSTS):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Host not on allow-list")

    # Resolve and verify all IPs
    addrs = _resolve_all(host)
    if not addrs:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "DNS resolution failed")

    if OUTBOUND_BLOCK_PRIVATE:
        for addr in addrs:
            if _addr_is_private(addr):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Private address blocked")

    return parsed.scheme, host, port

async def safe_http_get(url: str, timeout: float = 5.0) -> httpx.Response:
    """
    Validate URL and perform a GET without following redirects automatically.
    If a 3xx is returned with a Location header, we re-validate the target first.
    """
    validate_outbound_url(url)

    async with httpx.AsyncClient(follow_redirects=False, timeout=timeout) as client:
        resp = await client.get(url)
        # Handle manual redirect validation (one hop is enough for demo)
        if 300 <= resp.status_code < 400 and (loc := resp.headers.get("Location")):
            validate_outbound_url(loc)
            resp = await client.get(loc)
        return resp
