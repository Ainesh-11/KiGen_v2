import pytest

from kigen.junctions import (
    Junction,
    parse_junction,
    parse_junctions,
)
from kigen.schematic import KiCadSchematic
from kigen.sexpr import SExprParser


def test_parse_junction():
    node = SExprParser(
        '(junction (at 100 50) (diameter 0) (color 0 0 0 0) '
        '(uuid 12345678-1234-1234-1234-123456789abc))'
    ).parse()

    junction = parse_junction(node)

    assert junction == Junction(
        x=100.0,
        y=50.0,
    )


def test_parse_junction_requires_at():
    node = SExprParser(
        '(junction (diameter 0))'
    ).parse()

    with pytest.raises(
        ValueError,
        match="Junction has no at section",
    ):
        parse_junction(node)


def test_parse_junction_requires_xy():
    node = SExprParser(
        '(junction (at 100))'
    ).parse()

    with pytest.raises(
        ValueError,
        match="must contain x and y",
    ):
        parse_junction(node)


def test_parse_junction_invalid_coordinate():
    node = SExprParser(
        '(junction (at abc 50))'
    ).parse()

    with pytest.raises(
        ValueError,
        match="Invalid junction coordinate",
    ):
        parse_junction(node)


def test_parse_junctions_from_schematic():
    schematic = KiCadSchematic()

    schematic.root = SExprParser(
        '''
        (
            kicad_sch
            (junction
                (at 100 50)
            )
            (junction
                (at 200 75)
            )
        )
        '''
    ).parse()

    junctions = parse_junctions(schematic)

    assert junctions == [
        Junction(x=100.0, y=50.0),
        Junction(x=200.0, y=75.0),
    ] 