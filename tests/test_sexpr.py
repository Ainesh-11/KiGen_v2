from kigen.sexpr import Atom, ListNode, SExprParser


def test_parse_simple_expression():
    node = SExprParser("(foo bar baz)").parse()

    assert isinstance(node, ListNode)
    assert len(node.items) == 3
    assert isinstance(node.items[0], Atom)
    assert node.items[0].value == "foo"
    assert node.items[1].value == "bar"
    assert node.items[2].value == "baz"


def test_parse_nested_expression():
    node = SExprParser(
        "(root (child value) (another (nested thing)))"
    ).parse()

    assert isinstance(node, ListNode)
    assert node.items[0].value == "root"

    child = node.items[1]

    assert isinstance(child, ListNode)
    assert child.items[0].value == "child"
    assert child.items[1].value == "value"


def test_parse_quoted_string():
    node = SExprParser(
        '(generator "eeschema")'
    ).parse()

    assert isinstance(node, ListNode)
    assert node.items[0].value == "generator"
    assert node.items[1].value == "eeschema"


def test_parse_quoted_string_with_spaces():
    node = SExprParser(
        '(comment "hello world")'
    ).parse()

    assert isinstance(node, ListNode)
    assert node.items[0].value == "comment"
    assert node.items[1].value == "hello world"


def test_parse_escaped_quotes():
    node = SExprParser(
        r'(text "hello \"KiGen\"")'
    ).parse()

    assert isinstance(node, ListNode)
    assert node.items[1].value == 'hello "KiGen"'


def test_parse_empty_string():
    node = SExprParser(
        '(value "")'
    ).parse()

    assert isinstance(node, ListNode)
    assert node.items[1].value == ""


def test_unterminated_string():
    try:
        SExprParser(
            '(generator "eeschema)'
        ).parse()
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "Unterminated quoted string" in str(error)