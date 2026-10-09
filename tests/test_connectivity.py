from pathlib import Path
from kigen.connectivity import (
    Net,
    build_nets,
    find_coincident_pins,
    find_global_label_connections,
    find_junction_wire_connections,
    find_label_connections,
    find_hierarchical_label_connections,
    find_pin_wire_connections,
    find_wire_connections,
    merge_global_label_nets,
    resolve_all_pins,
    resolve_net_name,
    resolve_pin_position,
    resolve_symbol_pins,
)
from kigen.labels import (
    Label,
    parse_label,
    parse_labels,
)
from kigen.global_labels import (
    GlobalLabel,
    parse_global_label,
    parse_global_labels,
)
from kigen.wires import WireSegment
from kigen.schematic import KiCadSchematic
from kigen.sexpr import ListNode, SExprParser
from kigen.hierarchical_labels import HierarchicalLabel

SCHEMATIC = (
    Path(__file__).parent.parent
    / "examples"
    / "KiGenTest.kicad_sch"
)


def test_resolve_all_pins():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    assert len(pins) == 4


def test_resolved_pin_positions():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    resistor_pins = [
        pin
        for pin in pins
        if pin.symbol.reference == "R1"
    ]

    assert len(resistor_pins) == 2

    pin1 = next(
        pin
        for pin in resistor_pins
        if pin.number == "1"
    )

    pin2 = next(
        pin
        for pin in resistor_pins
        if pin.number == "2"
    )

    assert abs(pin1.x - 128.27) < 0.001
    assert abs(pin1.y - 105.41) < 0.001

    assert abs(pin2.x - 128.27) < 0.001
    assert abs(pin2.y - 113.03) < 0.001


def test_find_coincident_pins():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    connections = find_coincident_pins(pins)

    assert len(connections) == 2

    connected_pairs = {
        (
            first.symbol.reference,
            first.number,
            second.symbol.reference,
            second.number,
        )
        for first, second in connections
    }

    assert (
        ("R1", "1", "#PWR01", "1") in connected_pairs
        or ("#PWR01", "1", "R1", "1") in connected_pairs
    )

    assert (
        ("R1", "2", "#PWR02", "1") in connected_pairs
        or ("#PWR02", "1", "R1", "2") in connected_pairs
    )


def test_build_nets():
    schematic = KiCadSchematic.load(SCHEMATIC)

    nets = build_nets(schematic)

    assert len(nets) == 2


def test_each_net_contains_two_pins():
    schematic = KiCadSchematic.load(SCHEMATIC)

    nets = build_nets(schematic)

    assert all(
        len(net.pins) == 2
        for net in nets
    )


def test_net_membership():
    schematic = KiCadSchematic.load(SCHEMATIC)

    nets = build_nets(schematic)

    net_members = [
        {
            (
                pin.symbol.reference,
                pin.number,
            )
            for pin in net.pins
        }
        for net in nets
    ]

    assert {
        ("R1", "1"),
        ("#PWR01", "1"),
    } in net_members

    assert {
        ("R1", "2"),
        ("#PWR02", "1"),
    } in net_members


def test_find_pin_wire_connection():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    wire = WireSegment(
        x1=128.27,
        y1=105.41,
        x2=140.0,
        y2=105.41,
    )

    connections = find_pin_wire_connections(
        pins,
        [wire],
    )

    assert len(connections) == 2

    connected_pins = {
        (
            pin.symbol.reference,
            pin.number,
        )
        for pin, _ in connections
    }

    assert ("R1", "1") in connected_pins
    assert ("#PWR01", "1") in connected_pins


def test_find_no_pin_wire_connection():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    wire = WireSegment(
        x1=140.0,
        y1=100.0,
        x2=150.0,
        y2=100.0,
    )

    connections = find_pin_wire_connections(
        pins,
        [wire],
    )

    assert connections == []


def test_build_nets_with_wire():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    wire = WireSegment(
        x1=128.27,
        y1=105.41,
        x2=140.0,
        y2=105.41,
    )

    pin_wire_connections = []

    for pin in pins:
        if (
            pin.symbol.reference == "R1"
            and pin.number == "1"
        ):
            pin_wire_connections.append(pin)

    assert len(pin_wire_connections) == 1


def test_wire_connects_two_pins():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    wires = [
        WireSegment(
            x1=128.27,
            y1=105.41,
            x2=128.27,
            y2=113.03,
        )
    ]

    connections = find_pin_wire_connections(
        pins,
        wires,
    )

    connected_pins = {
        (
            pin.symbol.reference,
            pin.number,
        )
        for pin, _ in connections
    }

    assert ("R1", "1") in connected_pins
    assert ("R1", "2") in connected_pins
    assert ("#PWR01", "1") in connected_pins
    assert ("#PWR02", "1") in connected_pins


def test_wire_wire_connection():
    first = WireSegment(
        x1=100.0,
        y1=50.0,
        x2=120.0,
        y2=50.0,
    )

    second = WireSegment(
        x1=120.0,
        y1=50.0,
        x2=120.0,
        y2=70.0,
    )

    connections = find_wire_connections(
        [first, second]
    )

    assert len(connections) == 1


def test_build_nets_with_connected_wire_chain():
    schematic = KiCadSchematic.load(SCHEMATIC)

    pins = resolve_all_pins(schematic)

    wires = [
        WireSegment(
            x1=128.27,
            y1=105.41,
            x2=140.0,
            y2=105.41,
        ),
        WireSegment(
            x1=140.0,
            y1=105.41,
            x2=150.0,
            y2=105.41,
        ),
    ]

    connections = find_pin_wire_connections(
        pins,
        wires,
    )

    connected_pins = {
        (
            pin.symbol.reference,
            pin.number,
        )
        for pin, _ in connections
    }

    assert ("R1", "1") in connected_pins
    assert ("#PWR01", "1") in connected_pins


def _schematic_with_wires(
    wires: list[str] | None = None,
    junctions: list[str] | None = None,
):
    schematic_path = (
        Path(__file__).parent.parent
        / "examples"
        / "KiGenTest.kicad_sch"
    )

    schematic = KiCadSchematic.load(
        schematic_path
    )

    if schematic.root is None:
        raise ValueError(
            "Test schematic has no root"
        )

    default_wires = [
        (
            "(wire "
            "(pts "
            "(xy 128.27 105.41) "
            "(xy 140 105.41)"
            ")"
            ")"
        ),
        (
            "(wire "
            "(pts "
            "(xy 140 105.41) "
            "(xy 150 105.41)"
            ")"
            ")"
        ),
    ]

    wire_texts = (
        default_wires
        if wires is None
        else wires
    )

    junction_texts = junctions or []

    for wire_text in wire_texts:
        wire_node = SExprParser(
            wire_text
        ).parse()

        if not isinstance(
            wire_node,
            ListNode,
        ):
            raise ValueError(
                "Wire must parse to a list"
            )

        schematic.root.items.append(
            wire_node
        )

    for junction_text in junction_texts:
        junction_node = SExprParser(
            junction_text
        ).parse()

        if not isinstance(
            junction_node,
            ListNode,
        ):
            raise ValueError(
                "Junction must parse to a list"
            )

        schematic.root.items.append(
            junction_node
        )

    return schematic

def _schematic_with_global_labels():
    schematic = KiCadSchematic.load(SCHEMATIC)

    assert schematic.root is not None

    first_label = SExprParser(
        '(global_label "SHARED_NET" '
        '(shape passive) '
        '(at 128.27 105.41 0))'
    ).parse()

    second_label = SExprParser(
        '(global_label "SHARED_NET" '
        '(shape passive) '
        '(at 128.27 113.03 0))'
    ).parse()

    schematic.root.items.extend(
        [
            first_label,
            second_label,
        ]
    )

    return schematic

def test_build_nets_with_actual_wires():
    schematic = _schematic_with_wires()

    nets = build_nets(schematic)

    r1_pin1_net = next(
        net
        for net in nets
        if any(
            pin.symbol.reference == "R1"
            and pin.number == "1"
            for pin in net.pins
        )
    )

    members = {
        (
            pin.symbol.reference,
            pin.number,
        )
        for pin in r1_pin1_net.pins
    }

    assert ("R1", "1") in members
    assert ("#PWR01", "1") in members

    assert ("R1", "2") not in members
    assert ("#PWR02", "1") not in members


def test_build_nets_merges_wire_chain():
    schematic = _schematic_with_wires()

    nets = build_nets(schematic)

    r1_pin1_net = next(
        net
        for net in nets
        if any(
            pin.symbol.reference == "R1"
            and pin.number == "1"
            for pin in net.pins
        )
    )

    members = {
        (
            pin.symbol.reference,
            pin.number,
        )
        for pin in r1_pin1_net.pins
    }

    assert members == {
        ("R1", "1"),
        ("#PWR01", "1"),
    }


def test_junction_connects_two_wires():
    from kigen.junctions import Junction

    junctions = [
        Junction(
            x=100.0,
            y=100.0,
        ),
    ]

    wires = [
        WireSegment(
            x1=90.0,
            y1=100.0,
            x2=100.0,
            y2=100.0,
        ),
        WireSegment(
            x1=100.0,
            y1=100.0,
            x2=110.0,
            y2=100.0,
        ),
    ]

    connections = find_junction_wire_connections(
        junctions,
        wires,
    )

    assert len(connections) == 2


def test_build_nets_with_junction():
    schematic = _schematic_with_wires(
        wires=[
            "(wire (pts (xy 90 100) (xy 110 100)))",
            "(wire (pts (xy 100 90) (xy 100 110)))",
        ],
        junctions=[
            "(junction (at 100 100))",
        ],
    )

    nets = build_nets(schematic)

    assert len(nets) == 3

    synthetic_nets = [
        net
        for net in nets
        if net.pins == []
    ]

    assert len(synthetic_nets) == 1


def test_build_nets_crossing_wires_without_junction():
    schematic = _schematic_with_wires(
        wires=[
            "(wire (pts (xy 90 100) (xy 110 100)))",
            "(wire (pts (xy 100 90) (xy 100 110)))",
        ],
    )

    nets = build_nets(schematic)

    assert len(nets) == 4

    synthetic_nets = [
        net
        for net in nets
        if net.pins == []
    ]

    assert len(synthetic_nets) == 2

def test_parse_label():
    node = SExprParser(
        '(label "SDA" (at 120 80 0))'
    ).parse()

    label = parse_label(node)

    assert label == Label(
        text="SDA",
        x=120.0,
        y=80.0,
        rotation=0.0,
    )


def test_parse_label_without_rotation():
    node = SExprParser(
        '(label "SCL" (at 120 90))'
    ).parse()

    label = parse_label(node)

    assert label.text == "SCL"
    assert label.x == 120.0
    assert label.y == 90.0
    assert label.rotation is None


def test_parse_label_rejects_wrong_node():
    node = SExprParser(
        '(wire (pts (xy 120 80) (xy 130 80)))'
    ).parse()

    try:
        parse_label(node)
    except ValueError as exc:
        assert str(exc) == "Expected a label node"
    else:
        raise AssertionError(
            "Expected parse_label() to reject a wire"
        )


def test_parse_labels_from_schematic():
    schematic = KiCadSchematic.load(
        Path("examples/KiGenTest.kicad_sch")
    )

    label = ListNode(
        [
            SExprParser("label").parse(),
            SExprParser('"SDA"').parse(),
            SExprParser("(at 120 80 0)").parse(),
        ]
    )

    assert schematic.root is not None

    schematic.root.items.append(label)

    labels = parse_labels(schematic)

    assert len(labels) == 1
    assert labels[0].text == "SDA"
    assert labels[0].x == 120.0
    assert labels[0].y == 80.0
    
def test_find_label_connections_to_pin():
    schematic = KiCadSchematic.load(
        Path("examples/KiGenTest.kicad_sch")
    )

    pins = resolve_all_pins(schematic)

    assert pins

    target = pins[0]

    label = Label(
        text="TEST_NET",
        x=target.x,
        y=target.y,
    )

    connections = find_label_connections(
        [label],
        pins,
        [],
    )

    assert len(connections) == 2

    connected_indices = {
        connection[1]
        for connection in connections
    }

    assert connected_indices == {0, 2}

    assert all(
        connection[0] == label
        for connection in connections
    )


def test_find_label_connections_to_wire():
    wire = WireSegment(
        x1=100.0,
        y1=100.0,
        x2=120.0,
        y2=100.0,
    )

    label = Label(
        text="SDA",
        x=110.0,
        y=100.0,
    )

    connections = find_label_connections(
        [label],
        [],
        [wire],
    )

    assert len(connections) == 1
    assert connections[0][0] == label
    assert connections[0][1] == 0


def test_label_names_net():
    schematic = KiCadSchematic.load(
        Path("examples/KiGenTest.kicad_sch")
    )

    assert schematic.root is not None

    pins = resolve_all_pins(schematic)

    assert pins

    target = pins[0]

    schematic.root.items.append(
        ListNode(
            [
                SExprParser("label").parse(),
                SExprParser('"SDA"').parse(),
                ListNode(
                    [
                        SExprParser("at").parse(),
                        SExprParser(str(target.x)).parse(),
                        SExprParser(str(target.y)).parse(),
                        SExprParser("0").parse(),
                    ]
                ),
            ]
        )
    )

    nets = build_nets(schematic)

    matching = [
        net
        for net in nets
        if any(
            pin.symbol.reference == target.symbol.reference
            and pin.number == target.number
            for pin in net.pins
        )
    ]

    assert len(matching) == 1
    assert matching[0].name == "SDA"
    
def test_label_names_connected_wire_net():
    schematic = KiCadSchematic.load(
        Path("examples/KiGenTest.kicad_sch")
    )

    assert schematic.root is not None

    pins = resolve_all_pins(schematic)

    assert len(pins) >= 2

    first = pins[0]
    second = pins[2]

    assert first.x == second.x
    assert first.y == second.y

    wire = ListNode(
        [
            SExprParser("wire").parse(),
            ListNode(
                [
                    SExprParser("pts").parse(),
                    ListNode(
                        [
                            SExprParser("xy").parse(),
                            SExprParser(str(first.x)).parse(),
                            SExprParser(str(first.y)).parse(),
                        ]
                    ),
                    ListNode(
                        [
                            SExprParser("xy").parse(),
                            SExprParser(str(first.x + 10)).parse(),
                            SExprParser(str(first.y)).parse(),
                        ]
                    ),
                ]
            ),
        ]
    )

    label = ListNode(
        [
            SExprParser("label").parse(),
            SExprParser('"SDA"').parse(),
            ListNode(
                [
                    SExprParser("at").parse(),
                    SExprParser(str(first.x + 5)).parse(),
                    SExprParser(str(first.y)).parse(),
                    SExprParser("0").parse(),
                ]
            ),
        ]
    )

    schematic.root.items.extend(
        [
            wire,
            label,
        ]
    )

    nets = build_nets(schematic)

    matching = [
        net
        for net in nets
        if any(
            pin.symbol.reference == first.symbol.reference
            and pin.number == first.number
            for pin in net.pins
        )
    ]

    assert len(matching) == 1

    net = matching[0]

    assert net.name == "SDA"

    connected = {
        (pin.symbol.reference, pin.number)
        for pin in net.pins
    }

    assert (
        first.symbol.reference,
        first.number,
    ) in connected

    assert (
        second.symbol.reference,
        second.number,
    ) in connected

def test_resolve_net_name_without_labels():
    assert resolve_net_name(
        [],
        "NET_1",
    ) == "NET_1"


def test_resolve_net_name_with_one_label():
    assert resolve_net_name(
        ["SDA"],
        "NET_1",
    ) == "SDA"


def test_resolve_net_name_with_duplicate_labels():
    assert resolve_net_name(
        ["SDA", "SDA", "SDA"],
        "NET_1",
    ) == "SDA"


def test_resolve_net_name_with_multiple_identical_labels():
    assert resolve_net_name(
        ["SDA", "SDA"],
        "NET_7",
    ) == "SDA"


def test_resolve_net_name_rejects_conflicting_labels():
    try:
        resolve_net_name(
            ["SDA", "I2C_DATA"],
            "NET_1",
        )
    except ValueError as exc:
        assert str(exc) == (
            "Conflicting labels on the same net: "
            "SDA, I2C_DATA"
        )
    else:
        raise AssertionError(
            "Expected conflicting labels to raise ValueError"
        )

def test_parse_global_label():
    node = SExprParser(
        """
        (global_label
            "SPI_MOSI"
            (shape output)
            (at 100.0 50.0 90)
        )
        """
    ).parse()

    assert isinstance(node, ListNode)

    label = parse_global_label(node)

    assert label == GlobalLabel(
        text="SPI_MOSI",
        x=100.0,
        y=50.0,
        rotation=90.0,
        shape="output",
    )


def test_parse_global_label_without_rotation():
    node = SExprParser(
        """
        (global_label
            "RESET"
            (shape input)
            (at 10.0 20.0)
        )
        """
    ).parse()

    assert isinstance(node, ListNode)

    label = parse_global_label(node)

    assert label.text == "RESET"
    assert label.x == 10.0
    assert label.y == 20.0
    assert label.rotation is None
    assert label.shape == "input"


def test_parse_global_label_passive_shape():
    node = SExprParser(
        """
        (global_label
            "VBAT"
            (shape passive)
            (at 25.4 76.2 0)
        )
        """
    ).parse()

    assert isinstance(node, ListNode)

    label = parse_global_label(node)

    assert label.text == "VBAT"
    assert label.shape == "passive"


def test_parse_global_labels_from_schematic():
    schematic = KiCadSchematic()

    schematic.root = SExprParser(
        """
        (kicad_sch
            (version 20250114)
            (generator kigen)

            (global_label
                "SPI_MOSI"
                (shape output)
                (at 10 20 0)
            )

            (global_label
                "SPI_MISO"
                (shape input)
                (at 30 40 180)
            )
        )
        """
    ).parse()

    labels = parse_global_labels(
        schematic
    )

    assert len(labels) == 2

    assert labels[0] == GlobalLabel(
        text="SPI_MOSI",
        x=10.0,
        y=20.0,
        rotation=0.0,
        shape="output",
    )

    assert labels[1] == GlobalLabel(
        text="SPI_MISO",
        x=30.0,
        y=40.0,
        rotation=180.0,
        shape="input",
    )

def test_find_global_label_connection_to_pin():
    schematic = KiCadSchematic.load(SCHEMATIC)
    pins = resolve_all_pins(schematic)

    label = GlobalLabel(
        text="TEST_NET",
        x=128.27,
        y=105.41,
    )

    connections = find_global_label_connections(
        [label],
        pins,
        [],
    )

    connected_indices = {
        index
        for _, index in connections
    }

    assert connected_indices == {0, 2}

def test_find_global_label_connection_to_wire():
    schematic = KiCadSchematic.load(SCHEMATIC)
    pins = resolve_all_pins(schematic)

    wire = WireSegment(
        x1=128.27,
        y1=105.41,
        x2=140.0,
        y2=105.41,
    )

    label = GlobalLabel(
        text="SPI_MOSI",
        x=135.0,
        y=105.41,
    )

    connections = find_global_label_connections(
        [label],
        pins,
        [wire],
    )

    assert connections == [
        (label, len(pins))
    ]

def test_build_nets_preserves_global_labels():
    schematic = KiCadSchematic.load(SCHEMATIC)

    root = schematic.root
    assert root is not None

    root.items.append(
        SExprParser(
            '(global_label "TEST_GLOBAL" '
            '(shape input) '
            '(at 128.27 105.41 0))'
        ).parse()
    )

    nets = build_nets(schematic)

    matching_nets = [
        net
        for net in nets
        if "TEST_GLOBAL" in net.global_labels
    ]

    assert len(matching_nets) == 1
    assert matching_nets[0].name == "TEST_GLOBAL"

def test_global_labels_merge_transitive_nets():
    nets = [
        Net(
            name="NET_1",
            pins=[],
            global_labels=["SPI_MOSI"],
        ),
        Net(
            name="NET_2",
            pins=[],
            global_labels=["SPI_MISO", "SPI_MOSI"],
        ),
        Net(
            name="NET_3",
            pins=[],
            global_labels=["SPI_MISO"],
        ),
    ]

    merged = merge_global_label_nets(nets)

    assert len(merged) == 1
    assert set(merged[0].global_labels) == {
        "SPI_MOSI",
        "SPI_MISO",
    }
    
def test_build_nets_merges_global_labels():
    schematic = _schematic_with_global_labels()

    nets = build_nets(schematic)

    matching_nets = [
        net
        for net in nets
        if "SHARED_NET" in net.global_labels
    ]

    assert len(matching_nets) == 1

    net = matching_nets[0]

    members = {
        (
            pin.symbol.reference,
            pin.number,
        )
        for pin in net.pins
    }

    assert members == {
        ("R1", "1"),
        ("#PWR01", "1"),
        ("R1", "2"),
        ("#PWR02", "1"),
    }

    assert net.global_labels == [
        "SHARED_NET",
    ]

def test_build_nets_rejects_conflicting_global_labels():
    schematic = KiCadSchematic.load(SCHEMATIC)

    assert schematic.root is not None

    label_1 = SExprParser(
        '(global_label "SPI_MOSI" '
        '(shape passive) '
        '(at 128.27 105.41 0))'
    ).parse()

    label_2 = SExprParser(
        '(global_label "SPI_MISO" '
        '(shape passive) '
        '(at 128.27 105.41 0))'
    ).parse()

    schematic.root.items.extend(
        [
            label_1,
            label_2,
        ]
    )

    try:
        build_nets(schematic)
    except ValueError as exc:
        assert str(exc) == (
            "Conflicting labels on the same net: "
            "SPI_MOSI, SPI_MISO"
        )
    else:
        raise AssertionError(
            "Expected conflicting global labels "
            "to raise ValueError"
        )
        
def test_parse_hierarchical_label():
    from kigen.hierarchical_labels import (
        HierarchicalLabel,
        parse_hierarchical_label,
    )

    node = SExprParser(
        """
        (hierarchical_label
            "MOTOR_UART"
            (shape input)
            (at 100.0 50.0 90)
        )
        """
    ).parse()

    assert isinstance(node, ListNode)

    label = parse_hierarchical_label(node)

    assert label == HierarchicalLabel(
        text="MOTOR_UART",
        x=100.0,
        y=50.0,
        rotation=90.0,
        shape="input",
    )


def test_parse_hierarchical_label_without_rotation():
    from kigen.hierarchical_labels import (
        parse_hierarchical_label,
    )

    node = SExprParser(
        """
        (hierarchical_label
            "RESET"
            (shape output)
            (at 10.0 20.0)
        )
        """
    ).parse()

    label = parse_hierarchical_label(node)

    assert label.text == "RESET"
    assert label.x == 10.0
    assert label.y == 20.0
    assert label.rotation is None
    assert label.shape == "output"
    
def test_schematic_hierarchical_labels():
    from kigen.hierarchical_labels import HierarchicalLabel

    schematic = KiCadSchematic()

    schematic.root = SExprParser(
        """
        (kicad_sch
            (hierarchical_label
                "MOTOR_UART"
                (shape input)
                (at 100.0 50.0 90)
            )
            (hierarchical_label
                "RESET"
                (shape output)
                (at 10.0 20.0)
            )
        )
        """
    ).parse()

    labels = schematic.hierarchical_labels()

    assert labels == [
        HierarchicalLabel(
            text="MOTOR_UART",
            x=100.0,
            y=50.0,
            rotation=90.0,
            shape="input",
        ),
        HierarchicalLabel(
            text="RESET",
            x=10.0,
            y=20.0,
            rotation=None,
            shape="output",
        ),
    ]

def test_find_hierarchical_label_connection_to_wire():
    label = HierarchicalLabel(
        text="MOTOR_UART",
        x=100.0,
        y=50.0,
        shape="input",
    )

    wire = WireSegment(
        x1=90.0,
        y1=50.0,
        x2=110.0,
        y2=50.0,
    )

    connections = find_hierarchical_label_connections(
        [label],
        [],
        [wire],
    )

    assert connections == [(label, 0)]