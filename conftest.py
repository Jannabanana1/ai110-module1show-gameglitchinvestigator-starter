"""Make logic_utils.py importable from tests, wherever pytest is invoked.

pytest.ini sets `pythonpath = .`, but that only applies when pytest picks this
directory as its rootdir -- i.e. when you run it from here. Running `pytest`
from the parent directory makes the parent the rootdir, the pytest.ini here is
never read, and the tests fail with ModuleNotFoundError: No module named
'logic_utils'.

pytest imports conftest.py files from the collected tree's ancestors no matter
where it was invoked, so putting this directory on sys.path here covers both.
"""

import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
