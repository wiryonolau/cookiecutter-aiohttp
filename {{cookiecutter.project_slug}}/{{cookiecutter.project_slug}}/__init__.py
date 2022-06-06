import os
from pathlib import Path

with open(os.path.join(Path(__file__).parent.absolute(), "VERSION"), "r") as f:
    __version__ = f.read().strip().replace("\n", "")
