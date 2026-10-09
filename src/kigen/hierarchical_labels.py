from dataclasses import dataclass

from kigen.sexpr import Atom, ListNode


@dataclass(frozen=True)
class HierarchicalLabel:
    text: str
    x: float
    y: float
    rotation: float | None = None
    shape: str | None = None


def parse_hierarchical_label(node: ListNode) -> HierarchicalLabel:
    if not node.items:
        raise ValueError("Empty hierarchical label node")

    first = node.items[0]
    if not isinstance(first, Atom) or first.value != "hierarchical_label":
        raise ValueError("Expected a hierarchical_label node")

    if len(node.items) < 2:
        raise ValueError("Hierarchical label has no text")

    text_node = node.items[1]
    if not isinstance(text_node, Atom):
        raise ValueError("Hierarchical label text must be an atom")

    at = _find_list(node, "at")
    if at is None:
        raise ValueError("Hierarchical label has no at section")

    if len(at.items) < 3:
        raise ValueError(
            "Hierarchical label at section must contain x and y"
        )

    x = _parse_number(at.items[1])
    y = _parse_number(at.items[2])

    rotation = None
    if len(at.items) >= 4:
        rotation = _parse_number(at.items[3])

    shape = _find_value(node, "shape")

    return HierarchicalLabel(
        text=text_node.value,
        x=x,
        y=y,
        rotation=rotation,
        shape=shape,
    )


def parse_hierarchical_labels(schematic) -> list[HierarchicalLabel]:
    return [
        parse_hierarchical_label(section)
        for section in schematic.get_sections("hierarchical_label")
    ]


def _find_list(node: ListNode, name: str) -> ListNode | None:
    for item in node.items[1:]:
        if not isinstance(item, ListNode):
            continue

        if not item.items:
            continue

        first = item.items[0]
        if isinstance(first, Atom) and first.value == name:
            return item

    return None


def _find_value(node: ListNode, name: str) -> str | None:
    section = _find_list(node, name)

    if section is None:
        return None

    if len(section.items) < 2:
        return None

    value = section.items[1]

    if isinstance(value, Atom):
        return value.value

    return None


def _parse_number(node: object) -> float:
    if not isinstance(node, Atom):
        raise ValueError(
            "Hierarchical label coordinate must be an atom"
        )

    try:
        return float(node.value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid hierarchical label coordinate: {node.value}"
        ) from exc