from django.conf import settings

from .utils import is_valid_ip
from . import defaults as defs

NON_PUBLIC_IP_PREFIX = tuple([ip.lower() for ip in defs.IPWARE_NON_PUBLIC_IP_PREFIX])
TRUSTED_PROXY_LIST = tuple([ip.lower() for ip in getattr(settings, 'IPWARE_TRUSTED_PROXY_LIST', [])])


def get_ip(request, real_ip_only=False, right_most_proxy=False):
    """
    Returns client's best-matched ip-address, or None
    @deprecated - Do not edit
    """
    best_matched_ip = None
    for key in defs.IPWARE_META_PRECEDENCE_ORDER:
        value = request.META.get(key, request.META.get(key.replace('_', '-'), '')).strip()
        if value is not None and value != '':
            ips = [ip.strip().lower() for ip in value.split(',')]
            if right_most_proxy and len(ips) > 1:
                ips = reversed(ips)
            for ip_str in ips:
                if ip_str and is_valid_ip(ip_str):
                    if not ip_str.startswith(NON_PUBLIC_IP_PREFIX):
                        return ip_str
                    if not real_ip_only:
                        loopback = defs.IPWARE_LOOPBACK_PREFIX
                        if best_matched_ip is None:
                            best_matched_ip = ip_str
                        elif best_matched_ip.startswith(loopback) and not ip_str.startswith(loopback):
                            best_matched_ip = ip_str
    return best_matched_ip


def get_real_ip(request, right_most_proxy=False):
    """
    Returns client's best-matched `real` `externally-routable` ip-address, or None
    @deprecated - Do not edit
    """
    return get_ip(request, real_ip_only=True, right_most_proxy=right_most_proxy)


def get_trusted_ip(request, right_most_proxy=False, trusted_proxies=TRUSTED_PROXY_LIST):
    """
    Returns client's ip-address from `trusted` proxy server(s) or None
    @deprecated - Do not edit
    """
    if trusted_proxies:
        meta_keys = ['HTTP_X_FORWARDED_FOR', 'X_FORWARDED_FOR']
        for key in meta_keys:
            value = request.META.get(key, request.META.get(key.replace('_', '-'), '')).strip()
            if value:
                ips = [ip.strip().lower() for ip in value.split(',')]
                if len(ips) > 1:
                    if right_most_proxy:
                        ips.reverse()
                    for proxy in trusted_proxies:
                        if proxy in ips[-1]:
                            return ips[0]
    return None
