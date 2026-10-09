from pathlib import Path

from kigen.schematic import KiCadSchematic


SCHEMATIC = (
    Path(__file__).parent.parent
    / "examples"
    / "KiGenTest.kicad_sch"
)


def test_placed_symbols():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.placed_symbols()

    assert len(symbols) == 3


def test_resistor_symbol():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.placed_symbols()

    resistor = next(
        symbol
        for symbol in symbols
        if symbol.lib_id == "Device:R"
    )

    assert resistor.reference == "R1"
    assert resistor.value == "10k"

    assert resistor.x == 128.27
    assert resistor.y == 109.22
    assert resistor.rotation == 0.0


def test_power_symbols():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.placed_symbols()

    power_symbols = [
        symbol
        for symbol in symbols
        if symbol.lib_id in {"power:+5V", "power:GND"}
    ]

    assert len(power_symbols) == 2

def test_resolve_library_symbol():
    schematic = KiCadSchematic.load(SCHEMATIC)

    symbols = schematic.placed_symbols()

    resistor = next(
        symbol
        for symbol in symbols
        if symbol.lib_id == "Device:R"
    )

    library_symbol = resistor.resolve_library_symbol(schematic)

    assert library_symbol is not None
    assert library_symbol.name == "Device:R"
    assert len(library_symbol.pins) == 2