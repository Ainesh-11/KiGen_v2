from pathlib import Path

from kigen.schematic import KiCadSchematic
from kigen.sexpr import ListNode


SCHEMATIC = (
    Path(__file__).parent.parent
    / "examples"
    / "KiGenTest.kicad_sch"
)


def test_get_sections_returns_list():
    schematic = KiCadSchematic.load(SCHEMATIC)

    sections = schematic.get_sections("symbol")

    assert isinstance(sections, list)

    for section in sections:
        assert isinstance(section, ListNode)


def test_get_sections_returns_empty_for_unknown_section():
    schematic = KiCadSchematic.load(SCHEMATIC)

    sections = schematic.get_sections("definitely_not_a_kicad_section")

    assert sections == []


def test_get_section_returns_first_match():
    schematic = KiCadSchematic.load(SCHEMATIC)

    sections = schematic.get_sections("symbol")
    first_section = schematic.get_section("symbol")

    if sections:
        assert first_section is sections[0]
    else:
        assert first_section is None