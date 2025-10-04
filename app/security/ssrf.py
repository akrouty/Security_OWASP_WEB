import ipaddress, socket
from urllib.parse import urlparse

PRIVATE = [ipaddress.ip_network(n) for n in (
    "10.0.0.0/8","172.16.0.0/12","192.168.0.0/16","127.0.0.0/8","169.254.0.0/16"
)]

def is_safe_url(url: str, allowlist: set[str]) -> bool:
    u = urlparse(url)
    if u.scheme not in {"http","https"}: return False
    if u.netloc not in allowlist: return False
    ips = {ai[4][0] for ai in socket.getaddrinfo(u.hostname, u.port or 80, proto=socket.IPPROTO_TCP)}
    return all(ipaddress.ip_address(ip) not in net for ip in ips for net in PRIVATE)