"""Serve the rover's browser controller without launching the simulator."""

import argparse
import sys
from pathlib import Path

# The controller API and its templates live in the parent Sim directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api import app


if __name__ == "__main__":
    app.config["CLASS_DEMO"] = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lan", action="store_true", help="Allow the rover to upload over Wi-Fi")
    args = parser.parse_args()
    app.run(host="0.0.0.0" if args.lan else "127.0.0.1", port=5001)
