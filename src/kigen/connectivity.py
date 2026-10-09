from dataclasses import dataclass, field
from math import cos, radians, sin
from kigen.labels import Label, parse_labels
from kigen.junctions import Junction, parse_junctions
from kigen.library import LibrarySymbol
from kigen.pins import LibraryPin
from kigen.symbols import PlacedSymbol
from kigen.wires import (
    WireSegment,
    parse_wires,
    point_on_segment,
)
from kigen.global_labels import (
    GlobalLabel,
    parse_global_labels,
)
from kigen.hierarchical_labels import (
    HierarchicalLabel,
    parse_hierarchical_labels,
)

@dataclass
class ResolvedPin:
    symbol: PlacedSymbol
    library_pin: LibraryPin
    x: float
    y: float

    @property
    def number(self) -> str:
        return self.library_pin.number

    @property
    def name(self) -> str | None:
        return self.library_pin.name


@dataclass
class Net:
    name: str
    pins: list[ResolvedPin] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    global_labels: list[str] = field(default_factory=list)
    hierarchical_labels: list[str] = field(default_factory=list)


def resolve_pin_position(
    symbol: PlacedSymbol,
    pin: LibraryPin,
) -> tuple[float, float]:
    if symbol.x is None or symbol.y is None:
        raise ValueError("Placed symbol has no position")

    if pin.x is None or pin.y is None:
        raise ValueError("Library pin has no position")

    angle = radians(symbol.rotation or 0.0)

    cos_a = cos(angle)
    sin_a = sin(angle)

    x = (
        symbol.x
        + pin.x * cos_a
        - pin.y * sin_a
    )

    y = (
        symbol.y
        - pin.x * sin_a
        - pin.y * cos_a
    )

    return x, y


def resolve_symbol_pins(
    schematic,
    symbol: PlacedSymbol,
) -> list[ResolvedPin]:
    library_symbol = symbol.resolve_library_symbol(
        schematic
    )

    if library_symbol is None:
        return []

    resolved: list[ResolvedPin] = []

    for pin in library_symbol.pins:
        x, y = resolve_pin_position(
            symbol,
            pin,
        )

        resolved.append(
            ResolvedPin(
                symbol=symbol,
                library_pin=pin,
                x=x,
                y=y,
            )
        )

    return resolved


def resolve_all_pins(
    schematic,
) -> list[ResolvedPin]:
    resolved: list[ResolvedPin] = []

    for symbol in schematic.placed_symbols():
        resolved.extend(
            resolve_symbol_pins(
                schematic,
                symbol,
            )
        )

    return resolved


def find_coincident_pins(
    pins: list[ResolvedPin],
    tolerance: float = 0.001,
) -> list[tuple[ResolvedPin, ResolvedPin]]:
    connections: list[
        tuple[ResolvedPin, ResolvedPin]
    ] = []

    for index, first in enumerate(pins):
        for second in pins[index + 1:]:
            if (
                abs(first.x - second.x) <= tolerance
                and abs(first.y - second.y) <= tolerance
            ):
                connections.append(
                    (first, second)
                )

    return connections


def find_pin_wire_connections(
    pins: list[ResolvedPin],
    wires: list[WireSegment],
    tolerance: float = 0.001,
) -> list[tuple[ResolvedPin, WireSegment]]:
    connections: list[
        tuple[ResolvedPin, WireSegment]
    ] = []

    for pin in pins:
        for wire in wires:
            if point_on_segment(
                pin.x,
                pin.y,
                wire,
                tolerance=tolerance,
            ):
                connections.append(
                    (pin, wire)
                )

    return connections


def find_wire_connections(
    wires: list[WireSegment],
    tolerance: float = 0.001,
) -> list[tuple[WireSegment, WireSegment]]:
    connections: list[
        tuple[WireSegment, WireSegment]
    ] = []

    for index, first in enumerate(wires):
        for second in wires[index + 1:]:
            if (
                point_on_segment(
                    first.x1,
                    first.y1,
                    second,
                    tolerance=tolerance,
                )
                or point_on_segment(
                    first.x2,
                    first.y2,
                    second,
                    tolerance=tolerance,
                )
                or point_on_segment(
                    second.x1,
                    second.y1,
                    first,
                    tolerance=tolerance,
                )
                or point_on_segment(
                    second.x2,
                    second.y2,
                    first,
                    tolerance=tolerance,
                )
            ):
                connections.append(
                    (first, second)
                )

    return connections


def find_junction_wire_connections(
    junctions: list[Junction],
    wires: list[WireSegment],
    tolerance: float = 0.001,
) -> list[tuple[Junction, WireSegment]]:
    connections: list[
        tuple[Junction, WireSegment]
    ] = []

    for junction in junctions:
        for wire in wires:
            if point_on_segment(
                junction.x,
                junction.y,
                wire,
                tolerance=tolerance,
            ):
                connections.append(
                    (junction, wire)
                )

    return connections

def find_label_connections(
    labels: list[Label],
    pins: list[ResolvedPin],
    wires: list[WireSegment],
    tolerance: float = 0.001,
) -> list[tuple[Label, int]]:
    connections: list[tuple[Label, int]] = []

    for label in labels:
        for index, pin in enumerate(pins):
            if (
                abs(label.x - pin.x) <= tolerance
                and abs(label.y - pin.y) <= tolerance
            ):
                connections.append((label, index))

        for index, wire in enumerate(wires):
            if point_on_segment(
                label.x,
                label.y,
                wire,
                tolerance=tolerance,
            ):
                connections.append(
                    (label, len(pins) + index)
                )

    return connections

def find_global_label_connections(
    labels: list[GlobalLabel],
    pins: list[ResolvedPin],
    wires: list[WireSegment],
    tolerance: float = 0.001,
) -> list[tuple[GlobalLabel, int]]:
    connections: list[
        tuple[GlobalLabel, int]
    ] = []

    for label in labels:
        for index, pin in enumerate(pins):
            if (
                abs(label.x - pin.x) <= tolerance
                and abs(label.y - pin.y) <= tolerance
            ):
                connections.append(
                    (label, index)
                )

        for index, wire in enumerate(wires):
            if point_on_segment(
                label.x,
                label.y,
                wire,
                tolerance=tolerance,
            ):
                connections.append(
                    (
                        label,
                        len(pins) + index,
                    )
                )

    return connections

def find_hierarchical_label_connections(
    labels: list[HierarchicalLabel],
    pins: list[ResolvedPin],
    wires: list[WireSegment],
    tolerance: float = 0.001,
) -> list[tuple[HierarchicalLabel, int]]:
    connections: list[tuple[HierarchicalLabel, int]] = []

    for label in labels:
        for index, pin in enumerate(pins):
            if (
                abs(label.x - pin.x) <= tolerance
                and abs(label.y - pin.y) <= tolerance
            ):
                connections.append((label, index))

        for index, wire in enumerate(wires):
            if point_on_segment(
                label.x,
                label.y,
                wire,
                tolerance=tolerance,
            ):
                connections.append((label, len(pins) + index))

    return connections

def resolve_net_name(
    labels: list[str],
    default_name: str,
) -> str:
    unique_labels = list(dict.fromkeys(labels))

    if not unique_labels:
        return default_name

    if len(unique_labels) == 1:
        return unique_labels[0]

    raise ValueError(
        "Conflicting labels on the same net: "
        + ", ".join(unique_labels)
    )

def build_nets(
    schematic,
    tolerance: float = 0.001,
) -> list[Net]:
    pins = resolve_all_pins(schematic)
    wires = parse_wires(schematic)
    junctions = parse_junctions(schematic)
    labels = parse_labels(schematic)
    global_labels = parse_global_labels(schematic)
    hierarchical_labels = parse_hierarchical_labels(schematic)
    pin_count = len(pins)
    wire_offset = pin_count
    junction_offset = pin_count + len(wires)

    node_count = (
        pin_count
        + len(wires)
        + len(junctions)
    )

    adjacency: list[set[int]] = [
        set()
        for _ in range(node_count)
    ]

    pin_indices = {
        id(pin): index
        for index, pin in enumerate(pins)
    }

    wire_indices = {
        id(wire): wire_offset + index
        for index, wire in enumerate(wires)
    }

    junction_indices = {
        id(junction): junction_offset + index
        for index, junction in enumerate(junctions)
    }

    # Pin ↔ coincident pin
    for first, second in find_coincident_pins(
        pins,
        tolerance=tolerance,
    ):
        first_index = pin_indices[id(first)]
        second_index = pin_indices[id(second)]

        adjacency[first_index].add(second_index)
        adjacency[second_index].add(first_index)

    # Pin ↔ wire
    for pin, wire in find_pin_wire_connections(
        pins,
        wires,
        tolerance=tolerance,
    ):
        pin_index = pin_indices[id(pin)]
        wire_index = wire_indices[id(wire)]

        adjacency[pin_index].add(wire_index)
        adjacency[wire_index].add(pin_index)

    # Wire ↔ wire
    for first, second in find_wire_connections(
        wires,
        tolerance=tolerance,
    ):
        first_index = wire_indices[id(first)]
        second_index = wire_indices[id(second)]

        adjacency[first_index].add(second_index)
        adjacency[second_index].add(first_index)

    # Junction ↔ wire
    for junction, wire in find_junction_wire_connections(
        junctions,
        wires,
        tolerance=tolerance,
    ):
        junction_index = junction_indices[id(junction)]
        wire_index = wire_indices[id(wire)]

        adjacency[junction_index].add(wire_index)
        adjacency[wire_index].add(junction_index)

    # Label ↔ pin/wire
    #
    # Labels are not graph nodes.
    # They are metadata attached to an existing
    # electrical node and are associated with the
    # connected component below.
    label_connections = find_label_connections(
        labels,
        pins,
        wires,
        tolerance=tolerance,
    )
    global_label_connections = find_global_label_connections(
    global_labels,
    pins,
    wires,
    tolerance=tolerance,
)
    hierarchical_label_connections = find_hierarchical_label_connections(
    hierarchical_labels,
    pins,
    wires,
)

    visited: set[int] = set()
    nets: list[Net] = []

    for start_index in range(node_count):
        if start_index in visited:
            continue

        stack = [start_index]
        component: list[int] = []

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            component.append(current)

            for neighbour in adjacency[current]:
                if neighbour not in visited:
                    stack.append(neighbour)

        component_pins = [
            pins[index]
            for index in component
            if index < pin_count
        ]

        labels_for_component = [
            label.text
            for label, node_index in label_connections
            if node_index in component
        ]

        labels_for_component.extend(
            label.text
            for label, node_index in global_label_connections
            if node_index in component
        )

        name = resolve_net_name(
            labels_for_component,
            f"NET_{len(nets) + 1}",
        )

        component_labels = [
            label.text
            for label, node_index in label_connections
            if node_index in component
        ]

        component_global_labels = [
            label.text
            for label, node_index in global_label_connections
            if node_index in component
        ]

        component_hierarchical_labels = [
            label.text
            for label, node_index in hierarchical_label_connections
            if node_index in component
        ]
        
        nets.append(
            Net(
                name=name,
                pins=component_pins,
                labels=component_labels,
                global_labels=component_global_labels,
                hierarchical_labels=component_hierarchical_labels
            )
        )

    return merge_global_label_nets(nets)

def merge_global_label_nets(
    nets: list[Net],
) -> list[Net]:
    """Merge nets that share global labels, including transitive matches."""
    parent = list(range(len(nets)))
    label_to_net: dict[str, int] = {}

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first: int, second: int) -> None:
        first_root = find(first)
        second_root = find(second)

        if first_root != second_root:
            parent[second_root] = first_root

    # First pass: identify all nets connected by matching global labels.
    for index, net in enumerate(nets):
        for label in net.global_labels:
            if label in label_to_net:
                union(index, label_to_net[label])
            else:
                label_to_net[label] = index

    # Second pass: aggregate every net into its final connected group.
    merged: dict[int, Net] = {}

    for index, net in enumerate(nets):
        root = find(index)

        if root not in merged:
            merged[root] = Net(
                name=net.name,
                pins=[],
                labels=[],
                global_labels=[],
                hierarchical_labels=[],
            )

        target = merged[root]

        target.pins.extend(net.pins)

        for label in net.labels:
            if label not in target.labels:
                target.labels.append(label)

        for label in net.global_labels:
            if label not in target.global_labels:
                target.global_labels.append(label)

        for label in net.hierarchical_labels:
            if label not in target.hierarchical_labels:
                target.hierarchical_labels.append(label)

        # Prefer an explicit global name over an autogenerated net name.
        if (
            target.name.startswith("NET_")
            and net.global_labels
        ):
            target.name = net.global_labels[0]

    return list(merged.values())