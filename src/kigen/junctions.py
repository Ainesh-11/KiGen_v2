from dataclasses import dataclass

from kigen.sexpr import Atom, ListNode


@dataclass(frozen=True)
class Junction:
    x: float
    y: float


def parse_junction(node: ListNode) -> Junction:
    if not node.items:
        raise ValueError("Empty junction node")

    first = node.items[0]

    if not isinstance(first, Atom) or first.value != "junction":
        raise ValueError("Expected a junction node")

    at = _find_list(node, "at")

    if at is None:
        raise ValueError("Junction has no at section")

    if len(at.items) < 3:
        raise ValueError(
            "Junction at section must contain x and y"
        )

    x = _parse_number(at.items[1])
    y = _parse_number(at.items[2])

    return Junction(
        x=x,
        y=y,
    )


def parse_junctions(schematic) -> list[Junction]:
    return [
        parse_junction(section)
        for section in schematic.get_sections("junction")
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


def _parse_number(node) -> float:
    if not isinstance(node, Atom):
        raise ValueError(
            "Junction coordinate must be an atom"
        )

    try:
        return float(node.value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid junction coordinate: {node.value}"
        ) from exc