"""Test bootstrap for the Student Course Registration System.

Makes the repository root importable so ``import registration`` resolves for
every pytest invocation style::

    python -m pytest tests/test_whitebox.py -v
    python -m pytest tests/
    pytest                      # from inside tests/

No test logic lives here; keeping the path fix in the test package means the
suite behaves identically locally (upstream task 8) and on a CI runner.
"""

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))
