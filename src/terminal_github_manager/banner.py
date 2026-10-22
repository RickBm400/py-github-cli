import sys

from .version import get_version

ASCII_ART = r"""
 ██████╗ ██╗  ██╗      ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗ 
██╔════╝ ██║  ██║      ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗
██║  ███╗███████║█████╗██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝
██║   ██║██╔══██║╚════╝██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║      ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝                     
"""

ASCII_FALLBACK = r"""
 _   _ _   _ _____ __  __ ____   ___
| | | | |_   |_   _|  \/  |   \ / __|
| |_| | | | | | | | | |\/| |) |  __ |
|  _  | | | | | | | | |  | |   / __|
|_| |_| |_| |_| |_| |_|  |_|  |_| |___|
"""

def supports_unicode() -> bool:
    encoding = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        "█".encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return False
    return True


def render_banner() -> str:
    art = ASCII_ART if supports_unicode() else ASCII_FALLBACK
    return f"{art.strip()}\n\nv{get_version()}"


def render_version() -> str:
    return f"v{get_version()}"