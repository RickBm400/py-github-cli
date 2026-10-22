import sys

from .version import get_version

APP_TITLE = "GH Manager"
TAGLINE = "GitHub repository manager"

ASCII_ART = r"""
 ██████╗ ██╗  ██╗      ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗  
██╔════╝ ██║  ██║      ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗
██║  ███╗███████║█████╗██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝
██║   ██║██╔══██║╚════╝██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║      ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""

ASCII_FALLBACK = r"""
        _                                                       
       | |                                                      
   __ _| |__ ______ _ __ ___   __ _ _ __   __ _  __ _  ___ _ __ 
  / _` | '_ \______| '_ ` _ \ / _` | '_ \ / _` |/ _` |/ _ \ '__|
 | (_| | | | |     | | | | | | (_| | | | | (_| | (_| |  __/ |   
  \__, |_| |_|     |_| |_| |_|\__,_|_| |_|\__,_|\__, |\___|_|   
   __/ |                                         __/ |          
  |___/                                         |___/           
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
    return f"{art}\n\n{APP_TITLE} v{get_version()} - {TAGLINE}"


def render_version() -> str:
    return f"{APP_TITLE} v{get_version()}"