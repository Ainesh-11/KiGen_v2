from pathlib import Path

from kigen.schematic import KiCadSchematic


SCHEMATIC = (
    Path(__file__).parent.parent
    / "examples"
    / "KiGenTest.kicad_sch"
)


def test_library_symbols():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.library_symbols()

    assert len(symbols) == 3


def test_library_symbol_names():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.library_symbols()

    names = {symbol.name for symbol in symbols}

    assert names == {
        "Device:R",
        "power:+5V",
        "power:GND",
    }

def test_resistor_library_properties():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.library_symbols()

    resistor = next(
        symbol
        for symbol in symbols
        if symbol.name == "Device:R"
    )

    assert resistor.properties["Reference"] == "R"
    assert resistor.properties["Value"] == "R"
    assert resistor.properties["Description"] == "Resistor"
    
def test_resistor_library_pins():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.library_symbols()

    resistor = next(
        symbol
        for symbol in symbols
        if symbol.name == "Device:R"
    )

    assert len(resistor.pins) == 2

    pin1 = next(
        pin
        for pin in resistor.pins
        if pin.number == "1"
    )

    assert pin1.name == "~"
    assert pin1.electrical_type == "passive"
    assert pin1.graphic_style == "line"
    assert pin1.x == 0.0
    assert pin1.y == 3.81
    assert pin1.rotation == 270.0
    assert pin1.length == 1.27

    pin2 = next(
        pin
        for pin in resistor.pins
        if pin.number == "2"
    )

    assert pin2.y == -3.81
    assert pin2.rotation == 90.0

def test_get_library_symbol():
    schematic = KiCadSchematic.load(SCHEMATIC)

    resistor = schematic.get_library_symbol("Device:R")

    assert resistor is not None
    assert resistor.name == "Device:R"
    assert len(resistor.pins) == 2
    
def test_get_unknown_library_symbol():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbol = schematic.get_library_symbol("DoesNotExist")

    assert symbol is None