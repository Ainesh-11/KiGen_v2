from dataclasses import dataclass

from kigen.sexpr import Atom, ListNode


@dataclass
class LibraryPin:
    number: str
    name: str | None = None
    electrical_type: str | None = None
    graphic_style: str | None = None
    x: float | None = None
    y: float | None = None
    rotation: float | None = None
    length: float | None = None

    @classmethod
    def from_sexpr(cls, node: ListNode) -> "LibraryPin":
        if not node.items:
            raise ValueError("Empty pin node")

        first = node.items[0]

        if not isinstance(first, Atom) or first.value != "pin":
            raise ValueError("Expected a pin node")

        electrical_type = _atom_at(node, 1)
        graphic_style = _atom_at(node, 2)

        at = _find_list(node, "at")
        length_node = _find_list(node, "length")
        name_node = _find_list(node, "name")
        number_node = _find_list(node, "number")

        number = _value_at(number_node, 1)

        if number is None:
            raise ValueError("Pin has no number")

        name = _value_at(name_node, 1)

        return cls(
            number=number,
            name=name,
            electrical_type=electrical_type,
            graphic_style=graphic_style,
            x=_number_at(at, 1),
            y=_number_at(at, 2),
            rotation=_number_at(at, 3),
            length=_number_at(length_node, 1),
        )


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


def _atom_at(node: ListNode, index: int) -> str | None:
    if len(node.items) <= index:
        return None

    value = node.items[index]

    if isinstance(value, Atom):
        return value.value

    return None


def _value_at(
    node: ListNode | None,
    index: int,
) -> str | None:
    if node is None:
        return None

    return _atom_at(node, index)


def _number_at(
    node: ListNode | None,
    index: int,
) -> float | None:
    value = _value_at(node, index)

    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None