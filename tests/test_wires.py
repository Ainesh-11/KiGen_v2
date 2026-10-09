from kigen.sexpr import SExprParser
from kigen.wires import (
    WireSegment,
    parse_wire,
    point_on_segment,
)


def test_parse_wire():
    node = SExprParser(
        """
        (wire
            (pts
                (xy 100.0 50.0)
                (xy 120.0 50.0)
            )
            (stroke
                (width 0)
                (type default)
            )
            (uuid "test-wire")
        )
        """
    ).parse()

    wire = parse_wire(node)

    assert isinstance(wire, WireSegment)

    assert wire.start == (100.0, 50.0)
    assert wire.end == (120.0, 50.0)


def test_wire_coordinates_are_floats():
    node = SExprParser(
        """
        (wire
            (pts
                (xy 128.27 105.41)
                (xy 128.27 113.03)
            )
        )
        """
    ).parse()

    wire = parse_wire(node)

    assert wire.x1 == 128.27
    assert wire.y1 == 105.41
    assert wire.x2 == 128.27
    assert wire.y2 == 113.03


def test_wire_requires_two_points():
    node = SExprParser(
        """
        (wire
            (pts
                (xy 100 50)
            )
        )
        """
    ).parse()

    try:
        parse_wire(node)
    except ValueError as exc:
        assert "exactly two points" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )
        
from kigen.wires import point_on_segment


def test_point_on_horizontal_wire():
    wire = WireSegment(
        x1=100.0,
        y1=50.0,
        x2=120.0,
        y2=50.0,
    )

    assert point_on_segment(
        110.0,
        50.0,
        wire,
    )


def test_point_on_vertical_wire():
    wire = WireSegment(
        x1=128.27,
        y1=105.41,
        x2=128.27,
        y2=113.03,
    )

    assert point_on_segment(
        128.27,
        109.22,
        wire,
    )


def test_point_at_wire_endpoint():
    wire = WireSegment(
        x1=100.0,
        y1=50.0,
        x2=120.0,
        y2=50.0,
    )

    assert point_on_segment(
        100.0,
        50.0,
        wire,
    )

    assert point_on_segment(
        120.0,
        50.0,
        wire,
    )


def test_point_not_on_wire():
    wire = WireSegment(
        x1=100.0,
        y1=50.0,
        x2=120.0,
        y2=50.0,
    )

    assert not point_on_segment(
        110.0,
        55.0,
        wire,
    )


def test_point_beyond_wire_endpoint():
    wire = WireSegment(
        x1=100.0,
        y1=50.0,
        x2=120.0,
        y2=50.0,
    )

    assert not point_on_segment(
        130.0,
        50.0,
        wire,
    )