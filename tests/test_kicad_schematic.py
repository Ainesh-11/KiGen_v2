from pathlib import Path

from kigen.schematic import KiCadSchematic


SCHEMATIC = (
    Path(__file__).parent.parent
    / "examples"
    / "KiGenTest.kicad_sch"
)


def test_load_schematic():
    schematic = KiCadSchematic.load(SCHEMATIC)

    assert schematic.root is not None


def test_schematic_metadata():
    schematic = KiCadSchematic.load(SCHEMATIC)

    assert schematic.version == "20250114"
    assert schematic.generator == "eeschema"