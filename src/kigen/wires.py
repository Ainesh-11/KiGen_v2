from dataclasses import dataclass

from kigen.sexpr import Atom, ListNode


@dataclass
class WireSegment:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def start(self) -> tuple[float, float]:
        return self.x1, self.y1

    @property
    def end(self) -> tuple[float, float]:
        return self.x2, self.y2


def parse_wire(node: ListNode) -> WireSegment:
    if not node.items:
        raise ValueError("Empty wire node")

    first = node.items[0]

    if not isinstance(first, Atom) or first.value != "wire":
        raise ValueError("Expected a wire node")

    pts = _find_list(node, "pts")

    if pts is None:
        raise ValueError("Wire has no pts section")

    points = [
        item
        for item in pts.items[1:]
        if isinstance(item, ListNode)
    ]

    if len(points) != 2:
        raise ValueError(
            "Wire must contain exactly two points"
        )

    start = _parse_xy(points[0])
    end = _parse_xy(points[1])

    return WireSegment(
        x1=start[0],
        y1=start[1],
        x2=end[0],
        y2=end[1],
    )


def parse_wires(
    schematic,
) -> list[WireSegment]:
    return [
        parse_wire(section)
        for section in schematic.get_sections("wire")
    ]


def _find_list(
    node: ListNode,
    name: str,
) -> ListNode | None:
    for item in node.items[1:]:
        if not isinstance(item, ListNode):
            continue

        if not item.items:
            continue

        first = item.items[0]

        if (
            isinstance(first, Atom)
            and first.value == name
        ):
            return item

    return None


def _parse_xy(
    node: ListNode,
) -> tuple[float, float]:
    if not node.items:
        raise ValueError("Empty xy node")

    first = node.items[0]

    if not isinstance(first, Atom) or first.value != "xy":
        raise ValueError("Expected an xy node")

    if len(node.items) < 3:
        raise ValueError(
            "xy node must contain x and y"
        )

    x = _parse_number(node.items[1])
    y = _parse_number(node.items[2])

    return x, y


def _parse_number(node) -> float:
    if not isinstance(node, Atom):
        raise ValueError(
            "Coordinate must be an atom"
        )

    try:
        return float(node.value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid coordinate: {node.value}"
        ) from exc

def point_on_segment(
    x: float,
    y: float,
    wire: WireSegment,
    tolerance: float = 0.001,
) -> bool:
    x1 = wire.x1
    y1 = wire.y1
    x2 = wire.x2
    y2 = wire.y2

    dx = x2 - x1
    dy = y2 - y1

    length_squared = (
        dx * dx
        + dy * dy
    )

    if length_squared == 0:
        return (
            abs(x - x1) <= tolerance
            and abs(y - y1) <= tolerance
        )

    cross = (
        (x - x1) * dy
        - (y - y1) * dx
    )

    if abs(cross) > tolerance:
        return False

    dot = (
        (x - x1) * dx
        + (y - y1) * dy
    )

    if dot < -tolerance:
        return False

    if dot > length_squared + tolerance:
        return False

    return True