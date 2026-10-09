
from pathlib import Path

from kigen.schematic import KiCadSchematic
from kigen.sexpr import Atom, ListNode


def describe_node(
    node: ListNode,
    depth: int = 0,
    max_depth: int = 2,
) -> str:
    indent = "  " * depth

    if not node.items:
        return f"{indent}()"

    first = node.items[0]

    if isinstance(first, Atom):
        name = first.value
    else:
        name = "(list)"

    result = [f"{indent}{name}"]

    if depth >= max_depth:
        return "\n".join(result)

    for item in node.items[1:]:
        if isinstance(item, Atom):
            result.append(f"{indent}  {item.value}")
        elif isinstance(item, ListNode):
            result.append(
                describe_node(
                    item,
                    depth=depth + 1,
                    max_depth=max_depth,
                )
            )

    return "\n".join(result)


def inspect_schematic(path: str | Path) -> None:
    schematic = KiCadSchematic.load(path)

    print(f"File: {schematic.source_path}")
    print(f"Version: {schematic.version}")
    print(f"Generator: {schematic.generator}")
    print(f"Top-level entries: {schematic.size()}")
    print()

    print("Top-level sections:")
    for section in schematic.top_level_sections():
        print(f"  {section}")

    print()

    for section_name in (
        "wire",
        "junction",
        "label",
        "global_label",
        "connection",
    ):
        sections = schematic.get_sections(section_name)

        print(
            f"{section_name}: {len(sections)} section(s)"
        )

        for index, section in enumerate(sections[:10]):
            print()
            print(f"--- {section_name} [{index}] ---")
            print(describe_node(section, max_depth=10))

    print()

    for section_name in ("lib_symbols", "symbol"):
        sections = schematic.get_sections(section_name)

        print(
            f"{section_name}: {len(sections)} section(s)"
        )

        for index, section in enumerate(sections[:3]):
            print()
            print(f"--- {section_name} [{index}] ---")
            print(describe_node(section, max_depth=6))

