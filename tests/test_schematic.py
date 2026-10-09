from pathlib import Path

from kigen.schematic import KiCadSchematic


def test_load_kicad_schematic():
    path = Path("examples/KiGenTest.kicad_sch")

    schematic = KiCadSchematic(path)

    assert schematic.starts_with_kicad_sch()
    assert schematic.size() > 0