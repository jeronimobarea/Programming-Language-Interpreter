from typing import List, cast, Any, Type
from unittest import TestCase

from src.lexer.lexer import Lexer
from src.parser.ast import (
    Program,
    VarStatement,
    Integer,
    ReturnStatement,
    Expression,
    Identifier,
    ExpressionStatement,
)
from src.parser.parser import Parser


class ParserTest(TestCase):

    def test_parse_program(self) -> None:
        source: str = 'var x = 5;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)

        program: Program = parser.parse_program()

        self.assertIsNotNone(program)
        self.assertIsInstance(program, Program)

    def test_var_statements(self) -> None:
        source: str = '''
        var x = 5;
        var y = 10;
        var foo = 20;
        '''
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)

        program: Program = parser.parse_program()

        self.assertEqual(len(program.statements), 3)

        for statement in program.statements:
            self.assertEqual(statement.token_literal(), 'var')
            self.assertIsInstance(statement, VarStatement)

    def test_names_in_let_statements(self) -> None:
        source: str = '''
        var x = 5;
        var y = 10;
        var foo = 20;
        '''
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)

        program: Program = parser.parse_program()

        names: List[str] = []
        for statement in program.statements:
            statement = cast(VarStatement, statement)
            assert statement.name
            names.append(statement.name.value)

        expected_names: List[str] = ['x', 'y', 'foo']

        self.assertEqual(names, expected_names)

    def test_parse_errors(self) -> None:
        source: str = 'var x 5;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)

        parser.parse_program()

        self.assertEqual(len(parser.errors), 1)

    def test_return_statement(self) -> None:
        source: str = '''
        return 5;
        return foo;
        '''

        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)

        program: Program = parser.parse_program()

        self.assertEqual(len(program.statements), 2)

        for statement in program.statements:
            self.assertEqual(statement.token_literal(), 'return')
            self.assertIsInstance(statement, ReturnStatement)

    def test_identifier_expression(self) -> None:
        source: str = 'foobar;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)

        program: Program = parser.parse_program()

        self._test_program_statements(parser, program)

        expression_statement = cast(ExpressionStatement, program.statements[0])

        assert expression_statement.expression
        self._test_literal_expression(expression_statement.expression, 'foobar')

    def test_integer_expressions(self) -> None:
        source: str = '5;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)

        program: Program = parser.parse_program()

        self._test_program_statements(parser, program)

        expression_statement = cast(ExpressionStatement, program.statements[0])

        assert expression_statement.expression
        self._test_literal_expression(expression_statement.expression, 5)

    def _test_program_statements(self,
                                 parser: Parser,
                                 program: Program,
                                 expected_statement_count: int = 1) -> None:
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), expected_statement_count)
        self.assertIsInstance(program.statements[0], ExpressionStatement)

    def _test_literal_expression(self,
                                 expression: Expression,
                                 expected_value: Any) -> None:
        value_type: Type = type(expected_value)
        if value_type == str:
            self._test_identifier(expression, expected_value)
        elif value_type == int:
            self._test_integer(expression, expected_value)
        else:
            self.fail(f'Unhandled type of expression. Got = {value_type}')

    def _test_identifier(self,
                         expression: Expression,
                         expected_value: str) -> None:
        self.assertIsInstance(expression, Identifier)

        identifier = cast(Identifier, expression)
        self.assertEqual(identifier.value, expected_value)
        self.assertEqual(identifier.token.literal, expected_value)

    def _test_integer(self,
                      expression: Expression,
                      expected_value: int) -> None:
        self.assertIsInstance(expression, Integer)

        integer = cast(Integer, expression)
        self.assertEqual(integer.value, expected_value)
        self.assertEqual(integer.token.literal, str(expected_value))
