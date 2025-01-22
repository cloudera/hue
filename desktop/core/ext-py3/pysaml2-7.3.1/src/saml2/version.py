try:
    from importlib.metadata import version as _resolve_package_version
except ImportError:
    from importlib_metadata import version as _resolve_package_version


def _parse_version():
    value = _resolve_package_version("pysaml2")
    return value


version = _parse_version()
