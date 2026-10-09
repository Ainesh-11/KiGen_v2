from dataclasses import dataclass
from pathlib import Path
from kigen.hierarchical_labels import HierarchicalLabel
from kigen.sexpr import Atom, ListNode, SExprParser
from kigen.symbols import PlacedSymbol
from pathlib import Path

from kigen.sexpr import Atom, ListNode, SExprParser

from kigen.library import LibrarySymbol

@dataclass
class KiCadSchematic:
    source_path: Path | None = None
    version: str | None = None
    generator: str | None = None
    root: ListNode | None = None
    
    def __post_init__(self) -> None:
        if self.source_path is not None:
            self.source_path = Path(self.source_path)
            self._load_from_path(self.source_path)

    @classmethod
    def load(cls, path: str | Path) -> "KiCadSchematic":
        return cls(source_path=Path(path))

    def library_symbols(self) -> list[LibrarySymbol]:
        lib_symbols = self.get_section("lib_symbols")

        if lib_symbols is None:
            return []

        return [
            LibrarySymbol.from_sexpr(item)
            for item in lib_symbols.items[1:]
            if isinstance(item, ListNode)
        ]
        
    def hierarchical_labels(self) -> list[HierarchicalLabel]:
        from kigen.hierarchical_labels import parse_hierarchical_labels

        return parse_hierarchical_labels(self)    
    
    def get_library_symbol(
        self,
        lib_id: str,
    ) -> LibrarySymbol | None:
        for symbol in self.library_symbols():
            if symbol.name == lib_id:
                return symbol

        return None

    def _load_from_path(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        root = SExprParser(text).parse()

        if not isinstance(root, ListNode):
            raise ValueError("KiCad schematic root must be a list")

        if not root.items:
            raise ValueError("KiCad schematic is empty")

        first = root.items[0]

        if not isinstance(first, Atom) or first.value != "kicad_sch":
            raise ValueError("File is not a KiCad schematic")

        self.root = root
        self.version = self._find_atom_value("version")
        self.generator = self._find_atom_value("generator")

    

    def starts_with_kicad_sch(self) -> bool:
        if self.root is None or not self.root.items:
            return False

        first = self.root.items[0]

        return isinstance(first, Atom) and first.value == "kicad_sch"

    

    def size(self) -> int:
        if self.root is None:
            return 0

        return len(self.root.items)

    

    def top_level_sections(self) -> list[str]:
        if self.root is None:
            return []

        sections: list[str] = []

        for item in self.root.items[1:]:
            if not isinstance(item, ListNode):
                continue

            if not item.items:
                continue

            first = item.items[0]

            if isinstance(first, Atom):
                sections.append(first.value)

        return sections

    

    def has_section(self, name: str) -> bool:
        return name in self.top_level_sections()

    

    def get_section(self, name: str) -> ListNode | None:
        sections = self.get_sections(name)

        if not sections:
            return None

        return sections[0]

    
    
    def get_sections(self, name: str) -> list[ListNode]:
        if self.root is None:
            return []

        matches: list[ListNode] = []

        for item in self.root.items[1:]:
            if not isinstance(item, ListNode):
                continue

            if not item.items:
                continue

            first = item.items[0]

            if isinstance(first, Atom) and first.value == name:
                matches.append(item)

        return matches
    
    
    
    def placed_symbols(self) -> list[PlacedSymbol]:
        return [
            PlacedSymbol.from_sexpr(section)
            for section in self.get_sections("symbol")
        ]

    
    
    def _find_atom_value(self, name: str) -> str | None:
        section = self.get_section(name)

        if section is None:
            return None

        if len(section.items) < 2:
            return None

        value = section.items[1]

        if isinstance(value, Atom):
            return value.value

        return None
    
    
    
    
# Short alias for convenience.
Schematic = KiCadSchematic