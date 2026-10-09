from pathlib import Path

from kigen.schematic import KiCadSchematic
from kigen.sexpr import ListNode


SCHEMATIC = (
    Path(__file__).parent.parent
    / "examples"
    / "KiGenTest.kicad_sch"
)


def test_top_level_sections():
    schematic = KiCadSchematic.load(SCHEMATIC)

    sections = schematic.top_level_sections()

    assert "version" in sections
    assert "generator" in sections
    assert "uuid" in sections
    assert "paper" in sections
    assert "lib_symbols" in sections


def test_has_section():
    schematic = KiCadSchematic.load(SCHEMATIC)

    assert schematic.has_section("lib_symbols")
    assert not schematic.has_section("this_does_not_exist")


def test_get_section():
    schematic = KiCadSchematic.load(SCHEMATIC)

    section = schematic.get_section("lib_symbols")

    assert isinstance(section, ListNode)
    assert section.items[0].value == "lib_symbols"