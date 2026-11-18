"""Entrypoint for the news-image-20261118 round 2 entry.

The front page image (entry.png) is already drawn by draw_frontpage.py.
This script does one small, fully deterministic job: it places an exact
copy of that image into the grader's output directory so the result can
be collected.

It needs nothing beyond the Python standard library, makes no network
request, uses no randomness, and writes nowhere except the output
directory. Running it twice always produces the same bytes.

The output directory comes from the MAKEFUN_OUTPUT_DIR environment
variable and falls back to /output when that variable is not set.
"""

import os
import shutil
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / SOURCE_NAME
    if not source.is_file():
        print(f"missing source image: {source}", file=sys.stderr)
        return 1

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    destination = output_dir / SOURCE_NAME
    shutil.copyfile(source, destination)
    print(f"wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
