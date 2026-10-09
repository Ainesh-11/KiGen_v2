from dataclasses import dataclass

from kigen.sexpr import Atom, ListNode


@dataclass(frozen=True)
class GlobalLabel:
    text: str
    x: float
    y: float
    rotation: float | None = None
    shape: str | None = None


def parse_global_label(
    node: ListNode,
) -> GlobalLabel:
    if not node.items:
        raise ValueError("Empty global label node")

    first = node.items[0]

    if (
        not isinstance(first, Atom)
        or first.value != "global_label"
    ):
        raise ValueError(
            "Expected a global_label node"
        )

    if len(node.items) < 2:
        raise ValueError(
            "Global label has no text"
        )

    text_node = node.items[1]

    if not isinstance(text_node, Atom):
        raise ValueError(
            "Global label text must be an atom"
        )

    at = _find_list(node, "at")

    if at is None:
        raise ValueError(
            "Global label has no at section"
        )

    if len(at.items) < 3:
        raise ValueError(
            "Global label at section must contain x and y"
        )

    x = _parse_number(at.items[1])
    y = _parse_number(at.items[2])

    rotation = None

    if len(at.items) >= 4:
        rotation = _parse_number(at.items[3])

    shape = _find_value(
        node,
        "shape",
    )

    return GlobalLabel(
        text=text_node.value,
        x=x,
        y=y,
        rotation=rotation,
        shape=shape,
    )


def parse_global_labels(
    schematic,
) -> list[GlobalLabel]:
    return [
        parse_global_label(section)
        for section in schematic.get_sections(
            "global_label"
        )
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


def _find_value(
    node: ListNode,
    name: str,
) -> str | None:
    section = _find_list(
        node,
        name,
    )

    if section is None:
        return None

    if len(section.items) < 2:
        return None

    value = section.items[1]

    if isinstance(value, Atom):
        return value.value

    return None


def _parse_number(
    node: object,
) -> float:
    if not isinstance(node, Atom):
        raise ValueError(
            "Global label coordinate must be an atom"
        )

    try:
        return float(node.value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid global label coordinate: "
            f"{node.value}"
        ) from exc