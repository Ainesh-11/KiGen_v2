
from dataclasses import dataclass
from kigen.library import LibrarySymbol
from kigen.sexpr import Atom, ListNode


@dataclass
class PlacedSymbol:
    lib_id: str | None = None
    uuid: str | None = None
    reference: str | None = None
    value: str | None = None
    x: float | None = None
    y: float | None = None
    rotation: float | None = None

    @classmethod
    def from_sexpr(cls, node: ListNode) -> "PlacedSymbol":
        if not node.items:
            raise ValueError("Empty symbol node")

        first = node.items[0]

        if not isinstance(first, Atom) or first.value != "symbol":
            raise ValueError("Expected a symbol node")

        symbol = cls()

        lib_id = _find_value(node, "lib_id")
        uuid = _find_value(node, "uuid")
        reference = _find_property(node, "Reference")
        value = _find_property(node, "Value")
        at = _find_list(node, "at")

        symbol.lib_id = lib_id
        symbol.uuid = uuid
        symbol.reference = reference
        symbol.value = value

        if at is not None:
            symbol.x = _number_at(at, 1)
            symbol.y = _number_at(at, 2)
            symbol.rotation = _number_at(at, 3)

        return symbol
    
    def resolve_library_symbol(
        self,
        schematic,
    ) -> LibrarySymbol | None:
        if self.lib_id is None:
            return None

        return schematic.get_library_symbol(self.lib_id)

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

    if section is None or len(section.items) < 2:
        return None

    value = section.items[1]

    if isinstance(value, Atom):
        return value.value

    return None


def _find_property(node: ListNode, property_name: str) -> str | None:
    for item in node.items[1:]:
        if not isinstance(item, ListNode):
            continue

        if not item.items:
            continue

        first = item.items[0]

        if not isinstance(first, Atom) or first.value != "property":
            continue

        if len(item.items) < 3:
            continue

        name = item.items[1]

        if not isinstance(name, Atom):
            continue

        if name.value != property_name:
            continue

        value = item.items[2]

        if isinstance(value, Atom):
            return value.value

    return None


def _number_at(node: ListNode, index: int) -> float | None:
    if len(node.items) <= index:
        return None

    value = node.items[index]

    if not isinstance(value, Atom):
        return None

    try:
        return float(value.value)
    except ValueError:
        return None