from dataclasses import dataclass

from kigen.sexpr import Atom, ListNode


@dataclass(frozen=True)
class Label:
    text: str
    x: float
    y: float
    rotation: float | None = None


def parse_label(node: ListNode) -> Label:
    if not node.items:
        raise ValueError("Empty label node")

    first = node.items[0]

    if not isinstance(first, Atom) or first.value != "label":
        raise ValueError("Expected a label node")

    if len(node.items) < 2:
        raise ValueError("Label has no text")

    text_node = node.items[1]

    if not isinstance(text_node, Atom):
        raise ValueError("Label text must be an atom")

    at = _find_list(node, "at")

    if at is None:
        raise ValueError("Label has no at section")

    if len(at.items) < 3:
        raise ValueError(
            "Label at section must contain x and y"
        )

    x = _parse_number(at.items[1])
    y = _parse_number(at.items[2])

    rotation = None

    if len(at.items) >= 4:
        rotation = _parse_number(at.items[3])

    return Label(
        text=text_node.value,
        x=x,
        y=y,
        rotation=rotation,
    )


def parse_labels(schematic) -> list[Label]:
    return [
        parse_label(section)
        for section in schematic.get_sections("label")
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


def _parse_number(node: object) -> float:
    if not isinstance(node, Atom):
        raise ValueError(
            "Label coordinate must be an atom"
        )

    try:
        return float(node.value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid label coordinate: {node.value}"
        ) from exc
