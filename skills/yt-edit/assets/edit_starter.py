"""Author all times against the source transcript. No absolute installation path.

python3 src/edit.py            # plan only
python3 src/edit.py --build    # composition, after plan approval
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "runtime"))
from ytlib import init, at, full, side, sidel, row, tag, pip, note, tool_card, plan, build

init(HERE.parent)

# Examples, to replace with cues from the real transcript:
# full(at("the next section"), at("the next section") + 4, "PART 01", "A clear idea", "One short subline")
# side(20, 28, "THE STEPS", "Start here", [row(20, "01", "First point"), row(23, "02", "Second point")])
# pip(30, 40, dict(broll="demo.mp4", label="The actual demonstration"), [note(30, "DEMO", "What to notice")])
# tag(42, 47, "KEEP THIS", [(42, "One useful thought.")])

if "--build" in sys.argv:
    build()
else:
    plan()
