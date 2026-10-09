
from pathlib import Path

from kigen.inspect import inspect_schematic


SCHEMATIC = (
    Path(__file__).parent.parent
    / "examples"
    / "KiGenTest.kicad_sch"
)


if __name__ == "__main__":
    inspect_schematic(SCHEMATIC)
