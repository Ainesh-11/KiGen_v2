
from dataclasses import dataclass, field

from kigen.pins import LibraryPin
from kigen.sexpr import Atom, ListNode


@dataclass
class LibrarySymbol:
    name: str
    properties: dict[str, str] = field(default_factory=dict)
    pins: list[LibraryPin] = field(default_factory=list)

    @classmethod
    def from_sexpr(cls, node: ListNode) -> "LibrarySymbol":
        if not node.items:
            raise ValueError("Empty library symbol node")

        first = node.items[0]

        if not isinstance(first, Atom) or first.value != "symbol":
            raise ValueError("Expected a library symbol node")

        if len(node.items) < 2:
            raise ValueError("Library symbol has no name")

        name = node.items[1]

        if not isinstance(name, Atom):
            raise ValueError("Library symbol name must be an atom")

        properties: dict[str, str] = {}

        for item in node.items[2:]:
            if not isinstance(item, ListNode):
                continue

            if len(item.items) < 3:
                continue

            first_item = item.items[0]

            if not isinstance(first_item, Atom):
                continue

            if first_item.value != "property":
                continue

            property_name = item.items[1]
            property_value = item.items[2]

            if not isinstance(property_name, Atom):
                continue

            if not isinstance(property_value, Atom):
                continue

            properties[property_name.value] = property_value.value

        pins: list[LibraryPin] = []

        for item in node.items[2:]:
            if not isinstance(item, ListNode):
                continue

            if len(item.items) < 2:
                continue

            first_item = item.items[0]

            if not isinstance(first_item, Atom):
                continue

            if first_item.value != "symbol":
                continue

            for child in item.items[2:]:
                if not isinstance(child, ListNode):
                    continue

                if not child.items:
                    continue

                child_first = child.items[0]

                if (
                    isinstance(child_first, Atom)
                    and child_first.value == "pin"
                ):
                    pins.append(
                        LibraryPin.from_sexpr(child)
                    )

        return cls(
            name=name.value,
            properties=properties,
            pins=pins,
        )

