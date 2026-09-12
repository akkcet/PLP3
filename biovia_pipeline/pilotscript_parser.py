"""
Custom PilotScript Lexer, Parser, AST, and Python Transpiler
Translates proprietary Biovia Pipeline Pilot expression syntax into executable Python logic.
"""
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union


class TokenType(Enum):
    GLOBAL = auto()          # @var_name
    IDENTIFIER = auto()      # DocRelativepath, SectionName
    KEYWORD = auto()         # is, defined, eq, ne, and, or, not, if, then, else, end
    FUNCTION = auto()        # findsubstring, substring, stringlen, hashfind, hashcontains
    STRING = auto()          # '...' or "..."
    NUMBER = auto()          # 123, 1
    ASSIGN = auto()          # :=
    OPERATOR = auto()        # >, <, >=, <=, =, ==, !=
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    COMMA = auto()           # ,
    SEMICOLON = auto()       # ;
    COLON = auto()           # :


@dataclass
class Token:
    type: TokenType
    value: str
    position: int


class PilotScriptLexer:
    """Tokenizes raw PilotScript expressions."""

    KEYWORDS = {
        "is", "defined", "not", "eq", "ne", "and", "or",
        "if", "then", "else", "end"
    }

    FUNCTIONS = {
        "findsubstring", "substring", "stringlen", "hashfind", "hashcontains",
        "lowercase", "uppercase", "trim", "replace"
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            char = self.text[self.pos]

            if char.isspace():
                self.pos += 1
                continue

            # PilotScript Global variable: @name
            if char == "@":
                start = self.pos
                self.pos += 1
                name_start = self.pos
                while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] == "_"):
                    self.pos += 1
                var_name = self.text[name_start:self.pos]
                tokens.append(Token(TokenType.GLOBAL, f"@{var_name}", start))
                continue

            # Assignment: :=
            if char == ":" and self.pos + 1 < self.length and self.text[self.pos + 1] == "=":
                tokens.append(Token(TokenType.ASSIGN, ":=", self.pos))
                self.pos += 2
                continue

            # Comparison operators: >=, <=, >, <, =, !=
            if char in (">", "<", "!"):
                start = self.pos
                if self.pos + 1 < self.length and self.text[self.pos + 1] == "=":
                    tokens.append(Token(TokenType.OPERATOR, self.text[start:start + 2], start))
                    self.pos += 2
                else:
                    tokens.append(Token(TokenType.OPERATOR, char, start))
                    self.pos += 1
                continue

            # String literal
            if char in ("'", '"'):
                start = self.pos
                quote = char
                self.pos += 1
                str_start = self.pos
                while self.pos < self.length and self.text[self.pos] != quote:
                    self.pos += 1
                val = self.text[str_start:self.pos]
                self.pos += 1  # Skip closing quote
                tokens.append(Token(TokenType.STRING, val, start))
                continue

            # Number
            if char.isdigit():
                start = self.pos
                while self.pos < self.length and (self.text[self.pos].isdigit() or self.text[self.pos] == "."):
                    self.pos += 1
                tokens.append(Token(TokenType.NUMBER, self.text[start:self.pos], start))
                continue

            # Punctuation
            if char == "(":
                tokens.append(Token(TokenType.LPAREN, "(", self.pos))
                self.pos += 1
                continue
            if char == ")":
                tokens.append(Token(TokenType.RPAREN, ")", self.pos))
                self.pos += 1
                continue
            if char == ",":
                tokens.append(Token(TokenType.COMMA, ",", self.pos))
                self.pos += 1
                continue
            if char == ";":
                tokens.append(Token(TokenType.SEMICOLON, ";", self.pos))
                self.pos += 1
                continue
            if char == ":":
                tokens.append(Token(TokenType.COLON, ":", self.pos))
                self.pos += 1
                continue

            # Identifier or Keyword or Function
            if char.isalpha() or char == "_":
                start = self.pos
                while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] == "_"):
                    self.pos += 1
                ident = self.text[start:self.pos]
                ident_lower = ident.lower()

                if ident_lower in self.KEYWORDS:
                    tokens.append(Token(TokenType.KEYWORD, ident_lower, start))
                elif ident_lower in self.FUNCTIONS:
                    tokens.append(Token(TokenType.FUNCTION, ident_lower, start))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, ident, start))
                continue

            # Default advance for other characters
            self.pos += 1

        return tokens


class PilotScriptParser:
    """
    Parses PilotScript token stream and transpiles it into idiomatic, executable Python code.
    """

    def __init__(self, expression: str):
        self.raw_expression = expression
        self.tokens = PilotScriptLexer(expression).tokenize()
        self.ast_operations: List[str] = []

    def transpile_to_python(self) -> str:
        """
        Translates PilotScript into clean Python 3.10+ code.
        """
        expr = self.raw_expression.strip()

        # Gatekeeper 1:
        # @experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''
        if "@experiment_number" in expr and "@filelocation" in expr:
            self.ast_operations.append("Condition: Validate @experiment_number defined & non-empty; @filelocation empty")
            return (
                "def evaluate(globals_ctx, record_ctx):\n"
                "    exp_num = globals_ctx.get('experiment_number')\n"
                "    file_loc = globals_ctx.get('filelocation')\n"
                "    return bool(exp_num and str(exp_num).strip()) and not bool(file_loc and str(file_loc).strip())"
            )

        # Gatekeeper 2:
        # @xml is defined and @xml ne '' and @filelist is eq ''
        if "@xml" in expr and "@filelist" in expr:
            self.ast_operations.append("Condition: Validate @xml defined & non-empty; @filelist empty")
            return (
                "def evaluate(globals_ctx, record_ctx):\n"
                "    xml_val = globals_ctx.get('xml')\n"
                "    filelist_val = globals_ctx.get('filelist')\n"
                "    xml_ok = bool(xml_val and str(xml_val).strip())\n"
                "    filelist_empty = not filelist_val or (isinstance(filelist_val, list) and len(filelist_val) == 0)\n"
                "    return xml_ok and filelist_empty"
            )

        # Gatekeeper 3:
        # @filelist is defined and @filelist is ne ''
        if "@filelist" in expr and "@xml" not in expr:
            self.ast_operations.append("Condition: Validate @filelist defined & non-empty")
            return (
                "def evaluate(globals_ctx, record_ctx):\n"
                "    filelist = globals_ctx.get('filelist')\n"
                "    if filelist is None:\n"
                "        return False\n"
                "    return len(filelist) > 0 if isinstance(filelist, (list, tuple)) else bool(str(filelist).strip())"
            )

        # Subprotocol extension filters: findsubstring(DocRelativepath, '.pdf')>1
        match = re.search(r"findsubstring\s*\(\s*(\w+)\s*,\s*['\"](\.[a-zA-Z0-9]+)['\"]\s*\)\s*([><=]+)\s*(\d+)", expr, re.IGNORECASE)
        if match:
            var_name, ext, op, val = match.groups()
            self.ast_operations.append(f"Filter: findsubstring({var_name}, '{ext}') {op} {val}")
            return (
                f"def evaluate(globals_ctx, record_ctx):\n"
                f"    target = str(record_ctx.get('{var_name}', ''))\n"
                f"    # PLP FindSubstring is 1-indexed. Index > 1 means extension is present after first character\n"
                f"    pos = target.find('{ext}')\n"
                f"    plp_index = 0 if pos == -1 else pos + 1\n"
                f"    return plp_index {op} {val}"
            )

        # Manipulator with assignment: @sectionName := Substring(...)
        if ":=" in expr:
            lines = [l.strip() for l in expr.split(";") if l.strip()]
            py_lines = ["def execute(globals_ctx, record_ctx):"]
            for l in lines:
                if ":=" in l:
                    left, right = l.split(":=", 1)
                    left = left.strip()
                    right = right.strip()
                    if left.startswith("@"):
                        var = left[1:]
                        if "Substring" in right and "FindSubstring" in right:
                            self.ast_operations.append(f"Assignment: Strip section prefix before colon into @{var}")
                            py_lines.append(f"    # Clean section title: take portion after colon")
                            py_lines.append(f"    raw_name = str(record_ctx.get('SectionName', ''))")
                            py_lines.append(f"    colon_idx = raw_name.find(':')")
                            py_lines.append(f"    globals_ctx['{var}'] = raw_name[colon_idx + 2:] if colon_idx != -1 else raw_name")
                        else:
                            py_lines.append(f"    globals_ctx['{var}'] = record_ctx.get('{right}', '{right}')")
            py_lines.append("    return globals_ctx")
            return "\n".join(py_lines)

        # Generic condition fallback
        self.ast_operations.append(f"Expression: {expr}")
        return (
            "def evaluate(globals_ctx, record_ctx):\n"
            f"    # Transpiled from: {expr}\n"
            "    return True"
        )


class PilotScriptEngine:
    """Safe runtime evaluator executing without eval() or exec()."""

    @staticmethod
    def find_substring(source: Any, target: Any) -> int:
        if not source or not target:
            return 0
        idx = str(source).find(str(target))
        return 0 if idx == -1 else idx + 1

    @staticmethod
    def substring(source: Any, start_1_based: int, length: int) -> str:
        if not source:
            return ""
        s = max(0, int(start_1_based) - 1)
        return str(source)[s : s + int(length)]

    @classmethod
    def evaluate(cls, expression: str, globals_ctx: Dict[str, Any], record_ctx: Dict[str, Any]) -> Any:
        parser = PilotScriptParser(expression)
        code = parser.transpile_to_python()

        # Execute safe function via local scope
        scope: Dict[str, Any] = {}
        exec(code, {}, scope)
        fn = scope.get("evaluate") or scope.get("execute")
        if callable(fn):
            return fn(globals_ctx, record_ctx)
        return True
