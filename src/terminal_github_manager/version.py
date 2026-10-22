from importlib import metadata

PACKAGE_NAME = "terminal-github-manager"
FALLBACK_VERSION = "0.1.0"


def get_version() -> str:
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return FALLBACK_VERSION


__version__ = get_version()