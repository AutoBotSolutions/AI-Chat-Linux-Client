"""Repository-level pytest fixture bridge.

Exposes fixtures from tests/conftest.py to test modules located outside
that folder (for example docs/).
"""

from tests.conftest import *  # noqa: F401,F403
