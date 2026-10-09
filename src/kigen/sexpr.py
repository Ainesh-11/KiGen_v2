from dataclasses import dataclass
from typing import Union


@dataclass
class Atom:
    value: str


@dataclass
class ListNode:
    items: list["Node"]


Node = Union[Atom, ListNode]


class SExprParser:
    def __init__(self, text: str):
        self.text = text
        self.position = 0

    def parse(self) -> Node:
        self._skip_whitespace()

        node = self._parse_node()

        self._skip_whitespace()

        if self.position != len(self.text):
            raise ValueError(
                f"Unexpected data at position {self.position}"
            )

        return node

    def _parse_node(self) -> Node:
        self._skip_whitespace()

        if self.position >= len(self.text):
            raise ValueError("Unexpected end of input")

        char = self.text[self.position]

        if char == "(":
            return self._parse_list()

        if char == '"':
            return Atom(self._parse_quoted_atom())

        return Atom(self._parse_atom())

    def _parse_list(self) -> ListNode:
        self.position += 1  # consume '('

        items: list[Node] = []

        while True:
            self._skip_whitespace()

            if self.position >= len(self.text):
                raise ValueError("Unclosed list")

            if self.text[self.position] == ")":
                self.position += 1  # consume ')'
                return ListNode(items)

            items.append(self._parse_node())

    def _parse_atom(self) -> str:
        start = self.position

        while self.position < len(self.text):
            char = self.text[self.position]

            if char.isspace() or char in "()":
                break

            self.position += 1

        return self.text[start:self.position]

    def _parse_quoted_atom(self) -> str:
        self.position += 1  # consume opening '"'

        result: list[str] = []

        while self.position < len(self.text):
            char = self.text[self.position]

            if char == '"':
                self.position += 1  # consume closing '"'
                return "".join(result)

            if char == "\\":
                self.position += 1

                if self.position >= len(self.text):
                    raise ValueError("Unterminated escape sequence")

                escaped = self.text[self.position]

                escape_map = {
                    '"': '"',
                    "\\": "\\",
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                }

                result.append(escape_map.get(escaped, escaped))
                self.position += 1
                continue

            result.append(char)
            self.position += 1

        raise ValueError("Unterminated quoted string")

    def _skip_whitespace(self) -> None:
        while (
            self.position < len(self.text)
            and self.text[self.position].isspace()
        ):
            self.position += 1