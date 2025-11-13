"""Expose the legacy ``config/settings.py`` module when ``config.settings``
is imported.

Without this shim the presence of this package prevents Django from
finding the real settings module, which removes apps such as
``django.contrib.staticfiles`` and makes management commands like
``collectstatic`` unavailable.
"""

from pathlib import Path
import importlib.util

_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "settings.py"

if not _SETTINGS_PATH.exists():
    raise ImportError(
        f"Cannot import default settings because {_SETTINGS_PATH} is missing."
    )

_spec = importlib.util.spec_from_file_location(
    "config._legacy_settings", _SETTINGS_PATH
)
if _spec is None or _spec.loader is None:
    raise ImportError(
        f"Cannot import default settings because {_SETTINGS_PATH} is invalid."
    )

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

for _attr in dir(_module):
    if _attr.startswith("__"):
        continue
    globals()[_attr] = getattr(_module, _attr)

__all__ = [
    name for name in globals()
    if not name.startswith("__")
]
