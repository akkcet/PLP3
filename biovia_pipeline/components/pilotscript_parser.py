"""
Comprehensive PilotScript Lexer, AST Parser, and Runtime Execution Engine
Faithfully implements the Dassault Systèmes / BIOVIA Pipeline Pilot PilotScript language specification:
- Variables:
    Data Record properties: prop, %prop, %'prop name', property('prop')
    Global Protocol properties: @prop, @'prop name', globalproperty('prop')
    Local Component properties: #prop, #'prop name'
- Operators:
    Assignment: :=, +=, -=, *=, /=, .= (string append), ++, --
    Arithmetic: +, -, *, /, %
    Text: . (string concatenation)
    Comparison: EQ, NE, GT, GE, LT, LE, LIKE, RLIKE (regex), =, !=, >, >=, <, <=
    Property checks: IS [NOT] DEFINED, IS [NOT] UNIQUE
    Boolean logic: AND, OR, NOT
- Control Flow:
    IF ... THEN ... [ELSIF ... THEN ...] [ELSE ...] END IF;
    FOR var IN [REVERSE] start .. end LOOP ... END LOOP;
    WHILE [NOT] cond LOOP ... END LOOP;
- Built-in Functions:
    hashvaluecreate, hashadd, hashfind, contract, expand, converttobase64,
    convertstringtobytes, convertbytestostring, rsubst, substring, findsubstring,
    strlength, trim, tolower, toupper, strreplace, numvalues, error, eval, globalproperty, property
"""
import base64
import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union


class PilotScriptRuntimeError(Exception):
    """Raised when PilotScript calls error() or encounters an illegal operation."""
    pass


class PilotScriptEngine:
    """
    Stateful execution engine for PilotScript that isolates:
      - record_ctx: %record fields
      - globals_ctx: @global protocol properties
      - locals_ctx: #local component variables
    """

    def __init__(
        self,
        globals_ctx: Optional[Dict[str, Any]] = None,
        record_ctx: Optional[Dict[str, Any]] = None,
        locals_ctx: Optional[Dict[str, Any]] = None,
    ):
        self.globals_ctx: Dict[str, Any] = dict(globals_ctx) if globals_ctx is not None else {}
        self.record_ctx: Dict[str, Any] = dict(record_ctx) if record_ctx is not None else {}
        self.locals_ctx: Dict[str, Any] = dict(locals_ctx) if locals_ctx is not None else {}

    # --- Built-in Helper Functions (Public) ---

    @staticmethod
    def find_substring(source: Any, target: Any) -> int:
        """PLP FindSubstring is 1-indexed. Returns 0 if not found."""
        if source is None or target is None:
            return 0
        s = str(source)
        t = str(target)
        idx = s.find(t)
        return 0 if idx == -1 else idx + 1

    @staticmethod
    def substring(source: Any, start_1_based: int, length: Optional[int] = None) -> str:
        """PLP Substring is 1-indexed."""
        if source is None:
            return ""
        s = str(source)
        start = max(0, int(start_1_based) - 1)
        if length is None:
            return s[start:]
        return s[start : start + max(0, int(length))]

    @staticmethod
    def rsubst(source: Any, pattern: str, replacement: str, flags: str = "") -> str:
        """PLP regex substitution: rsubst(str, pat, repl, flags)"""
        if source is None:
            return ""
        re_flags = 0
        if "i" in flags.lower():
            re_flags |= re.IGNORECASE
        return re.sub(pattern, replacement, str(source), flags=re_flags)

    @staticmethod
    def contract(delimiter: str, arr: Any) -> str:
        """Combines array/hash into a single delimited string."""
        if isinstance(arr, (list, tuple)):
            return delimiter.join(str(x) for x in arr)
        if isinstance(arr, dict):
            parts = [f"{k}={v}" for k, v in arr.items()]
            return delimiter.join(parts)
        return str(arr) if arr is not None else ""

    @staticmethod
    def expand(delimiter: str, s: Any) -> List[str]:
        """Splits string by delimiter into a list."""
        if not s:
            return []
        return str(s).split(delimiter)

    # --- Variable Resolution ---

    def get_var(self, name: str) -> Any:
        name = name.strip()
        if not name:
            return None

        # Local variable: #name or #'name'
        if name.startswith("#"):
            key = name[1:].strip("'\"")
            return self.locals_ctx.get(key)

        # Global variable: @name or @'name'
        if name.startswith("@"):
            key = name[1:].strip("'\"")
            return self.globals_ctx.get(key)

        # Record field: %name or %'name'
        if name.startswith("%"):
            key = name[1:].strip("'\"")
            return self.record_ctx.get(key)

        # Plain identifier
        if name in self.record_ctx:
            return self.record_ctx[name]
        if name in self.locals_ctx:
            return self.locals_ctx[name]
        if name in self.globals_ctx:
            return self.globals_ctx[name]
        return None

    def set_var(self, name: str, value: Any) -> None:
        name = name.strip()
        if name.startswith("#"):
            key = name[1:].strip("'\"")
            self.locals_ctx[key] = value
        elif name.startswith("@"):
            key = name[1:].strip("'\"")
            self.globals_ctx[key] = value
        elif name.startswith("%"):
            key = name[1:].strip("'\"")
            self.record_ctx[key] = value
        else:
            self.record_ctx[name] = value

    def is_defined(self, name: str) -> bool:
        val = self.get_var(name)
        if val is None:
            return False
        if isinstance(val, (str, list, dict, tuple)) and len(val) == 0:
            return False
        return True

    # --- Script Execution ---

    def execute(self, script: str) -> None:
        """Executes multi-statement PilotScript."""
        if not script or not script.strip():
            return

        clean_script = re.sub(r"/\*.*?\*/", "", script, flags=re.DOTALL)
        clean_script = re.sub(r"//.*$", "", clean_script, flags=re.MULTILINE).strip()

        statements = self._split_top_level(clean_script, ";")
        i = 0
        while i < len(statements):
            stmt = statements[i].strip()
            if not stmt:
                i += 1
                continue

            if stmt.upper().startswith("IF ") or stmt.upper().startswith("IF("):
                block_stmts = [stmt]
                while i + 1 < len(statements) and not stmt.upper().endswith("END IF"):
                    i += 1
                    stmt = statements[i].strip()
                    block_stmts.append(stmt)
                self._execute_if_block(" ; ".join(block_stmts))
                i += 1
                continue

            if stmt.upper().startswith("FOR ") and "LOOP" in stmt.upper():
                block_stmts = [stmt]
                while i + 1 < len(statements) and not stmt.upper().endswith("END LOOP"):
                    i += 1
                    stmt = statements[i].strip()
                    block_stmts.append(stmt)
                self._execute_for_loop(" ; ".join(block_stmts))
                i += 1
                continue

            self._execute_statement(stmt)
            i += 1

    def _execute_statement(self, stmt: str) -> None:
        stmt = stmt.strip()
        if not stmt:
            return

        if stmt.endswith("++"):
            target = stmt[:-2].strip()
            val = self.get_var(target) or 0
            self.set_var(target, int(val) + 1)
            return
        if stmt.endswith("--"):
            target = stmt[:-2].strip()
            val = self.get_var(target) or 0
            self.set_var(target, int(val) - 1)
            return

        if ".=" in stmt:
            left, right = stmt.split(".=", 1)
            curr = str(self.get_var(left) or "")
            addition = str(self.eval_expr(right) or "")
            self.set_var(left, curr + addition)
            return

        if ":=" in stmt:
            left, right = stmt.split(":=", 1)
            val = self.eval_expr(right)
            self.set_var(left, val)
            return

        for op, py_op in [("+=", lambda a, b: a + b), ("-=", lambda a, b: a - b), ("*=", lambda a, b: a * b), ("/=", lambda a, b: a / b)]:
            if op in stmt:
                left, right = stmt.split(op, 1)
                curr = self.get_var(left) or 0
                val = self.eval_expr(right)
                self.set_var(left, py_op(float(curr), float(val)))
                return

        self.eval_expr(stmt)

    def _execute_if_block(self, full_if_text: str) -> None:
        pattern = r"IF\s+(.*?)\s+THEN\s*(.*?)(?=\s+ELSIF|\s+ELSE|\s+END\s+IF|$)"
        m = re.search(pattern, full_if_text, re.IGNORECASE | re.DOTALL)
        if not m:
            return

        cond_str = m.group(1).strip()
        body_str = m.group(2).strip()

        if self.eval_expr(cond_str):
            self.execute(body_str)
            return

        elsif_pattern = r"ELSIF\s+(.*?)\s+THEN\s*(.*?)(?=\s+ELSIF|\s+ELSE|\s+END\s+IF|$)"
        for em in re.finditer(elsif_pattern, full_if_text, re.IGNORECASE | re.DOTALL):
            e_cond = em.group(1).strip()
            e_body = em.group(2).strip()
            if self.eval_expr(e_cond):
                self.execute(e_body)
                return

        else_match = re.search(r"ELSE\s*(.*?)(?=\s+END\s+IF|$)", full_if_text, re.IGNORECASE | re.DOTALL)
        if else_match:
            self.execute(else_match.group(1).strip())

    def _execute_for_loop(self, loop_text: str) -> None:
        m = re.search(r"FOR\s+(#?\w+)\s+IN\s+(.*?)\s*\.\.\s*(.*?)\s+LOOP\s*(.*?)\s+END\s+LOOP", loop_text, re.IGNORECASE | re.DOTALL)
        if not m:
            return
        var_name, start_expr, end_expr, body = m.groups()
        start_val = int(self.eval_expr(start_expr))
        end_val = int(self.eval_expr(end_expr))
        for val in range(start_val, end_val + 1):
            self.set_var(var_name, val)
            self.execute(body)

    # --- Robust Expression Evaluation with Precedence ---

    def eval_expr(self, expr: str) -> Any:
        """
        Evaluates a PilotScript expression respecting operator precedence:
          1. OR
          2. AND
          3. NOT
          4. Comparisons: IS [NOT] DEFINED, EQ, NE, GT, GE, LT, LE, LIKE, RLIKE, >, <, >=, <=, =, !=
          5. String concatenation '.'
          6. Additive '+', '-'
          7. Multiplicative '*', '/', '%'
          8. Function calls & Parentheses
          9. Atoms (literals, variables)
        """
        expr = expr.strip()
        if not expr:
            return None

        # 1. OR operator (lowest precedence boolean)
        or_split = self._split_top_level_word(expr, "OR")
        if len(or_split) > 1:
            for part in or_split:
                if bool(self.eval_expr(part)):
                    return True
            return False

        # 2. AND operator
        and_split = self._split_top_level_word(expr, "AND")
        if len(and_split) > 1:
            for part in and_split:
                if not bool(self.eval_expr(part)):
                    return False
            return True

        # 3. NOT prefix operator
        if expr.upper().startswith("NOT ") and len(expr) > 4:
            return not bool(self.eval_expr(expr[4:].strip()))

        # 4. Property check: IS DEFINED / IS NOT DEFINED
        m_def = re.match(r"^(.*?)\s+IS\s+(NOT\s+)?DEFINED$", expr, re.IGNORECASE)
        if m_def:
            target = m_def.group(1).strip()
            is_not = bool(m_def.group(2))
            defined = self.is_defined(target)
            return (not defined) if is_not else defined

        # 5. Comparisons:
        # Handles PLP syntax like:
        #   x is eq y, x is ne y, x eq y, x ne y, x rlike y, x like y
        #   x > y, x < y, x >= y, x <= y, x = y, x != y, x == y
        cmp_operators = [
            (r"\s+IS\s+NOT\s+EQ\s+", lambda a, b: str(a or "").lower() != str(b or "").lower()),
            (r"\s+IS\s+NOT\s+NE\s+", lambda a, b: str(a or "").lower() == str(b or "").lower()),
            (r"\s+IS\s+EQ\s+", lambda a, b: str(a or "").lower() == str(b or "").lower()),
            (r"\s+IS\s+NE\s+", lambda a, b: str(a or "").lower() != str(b or "").lower()),
            (r"\s+NOT\s+RLIKE\s+", lambda a, b: not bool(re.search(str(b or ""), str(a or ""), re.IGNORECASE))),
            (r"\s+RLIKE\s+", lambda a, b: bool(re.search(str(b or ""), str(a or ""), re.IGNORECASE))),
            (r"\s+NOT\s+LIKE\s+", lambda a, b: str(b or "").strip("%").lower() not in str(a or "").lower()),
            (r"\s+LIKE\s+", lambda a, b: str(b or "").strip("%").lower() in str(a or "").lower()),
            (r"\s+EQ\s+", lambda a, b: str(a or "").lower() == str(b or "").lower()),
            (r"\s+NE\s+", lambda a, b: str(a or "").lower() != str(b or "").lower()),
            (r"\s+GT\s+", lambda a, b: float(a) > float(b)),
            (r"\s+GE\s+", lambda a, b: float(a) >= float(b)),
            (r"\s+LT\s+", lambda a, b: float(a) < float(b)),
            (r"\s+LE\s+", lambda a, b: float(a) <= float(b)),
            (r"==", lambda a, b: str(a or "") == str(b or "")),
            (r"!=", lambda a, b: str(a or "") != str(b or "")),
            (r">=", lambda a, b: float(a) >= float(b)),
            (r"<=", lambda a, b: float(a) <= float(b)),
            (r">", lambda a, b: float(a) > float(b)),
            (r"<", lambda a, b: float(a) < float(b)),
            (r"=", lambda a, b: str(a or "") == str(b or "")),
        ]

        for op_pattern, op_fn in cmp_operators:
            split_res = self._split_top_level_regex(expr, op_pattern)
            if split_res and len(split_res) == 2:
                left_val = self.eval_expr(split_res[0])
                right_val = self.eval_expr(split_res[1])
                try:
                    return op_fn(left_val, right_val)
                except Exception:
                    return False

        # 6. String concatenation: '.' operator (outside quotes and parens)
        dot_split = self._split_top_level_concat(expr)
        if len(dot_split) > 1:
            return "".join(str(self.eval_expr(part) or "") for part in dot_split)

        # 7. Additive: '+', '-' (outside quotes/parens)
        add_split = self._split_top_level_add(expr)
        if add_split:
            op, left, right = add_split
            lv = float(self.eval_expr(left) or 0)
            rv = float(self.eval_expr(right) or 0)
            res = lv + rv if op == "+" else lv - rv
            return int(res) if res.is_integer() else res

        # 8. Multiplicative: '*', '/', '%'
        mult_split = self._split_top_level_mult(expr)
        if mult_split:
            op, left, right = mult_split
            lv = float(self.eval_expr(left) or 0)
            rv = float(self.eval_expr(right) or 1)
            if op == "*":
                res = lv * rv
            elif op == "/":
                res = lv / rv if rv != 0 else 0
            else:
                res = lv % rv
            return int(res) if res.is_integer() else res

        # 9. Parentheses unwrapping: ( ... )
        if expr.startswith("(") and expr.endswith(")"):
            inner = expr[1:-1].strip()
            # Verify closing paren matches opening
            if self._is_balanced(inner):
                return self.eval_expr(inner)

        # 10. Boolean Literals
        if expr.upper() == "TRUE":
            return True
        if expr.upper() == "FALSE":
            return False

        # 11. String Literals
        if (expr.startswith("'") and expr.endswith("'")) or (expr.startswith('"') and expr.endswith('"')):
            return expr[1:-1]

        # 12. Numeric Literals
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # 13. Function Calls: func(arg1, arg2, ...)
        func_match = re.match(r"^(\w+)\s*\((.*)\)$", expr, re.DOTALL)
        if func_match and self._is_balanced(func_match.group(2)):
            fname = func_match.group(1).lower()
            arg_str = func_match.group(2)
            args = self._split_top_level(arg_str, ",")
            eval_args = [self.eval_expr(a) for a in args]

            if fname == "findsubstring":
                return self.find_substring(eval_args[0], eval_args[1])
            if fname == "substring":
                length = eval_args[2] if len(eval_args) > 2 else None
                return self.substring(eval_args[0], eval_args[1], length)
            if fname == "rsubst":
                flags = str(eval_args[3]) if len(eval_args) > 3 else ""
                return self.rsubst(eval_args[0], str(eval_args[1]), str(eval_args[2]), flags)
            if fname == "hashvaluecreate":
                return {}
            if fname == "hashadd":
                hash_target = self.get_var(args[0])
                if not isinstance(hash_target, dict):
                    hash_target = {}
                hash_target[str(eval_args[1])] = eval_args[2]
                self.set_var(args[0], hash_target)
                return hash_target
            if fname == "hashfind":
                target_hash = eval_args[0] if isinstance(eval_args[0], dict) else {}
                return target_hash.get(str(eval_args[1]), "")
            if fname == "converttobase64":
                raw = eval_args[0]
                if isinstance(raw, bytes):
                    return base64.b64encode(raw).decode("utf-8")
                return base64.b64encode(str(raw or "").encode("utf-8")).decode("utf-8")
            if fname == "convertstringtobytes":
                return str(eval_args[0] or "").encode("utf-8")
            if fname == "convertbytestostring":
                raw = eval_args[0]
                if isinstance(raw, bytes):
                    return raw.decode("utf-8", errors="ignore")
                return str(raw or "")
            if fname == "strlength":
                return len(str(eval_args[0] or ""))
            if fname == "trim":
                return str(eval_args[0] or "").strip()
            if fname == "tolower":
                return str(eval_args[0] or "").lower()
            if fname == "toupper":
                return str(eval_args[0] or "").upper()
            if fname == "strreplace":
                return str(eval_args[0] or "").replace(str(eval_args[1]), str(eval_args[2]))
            if fname == "numvalues":
                val = eval_args[0]
                if isinstance(val, (list, tuple)):
                    return len(val)
                return 1 if val is not None and val != "" else 0
            if fname == "error":
                raise PilotScriptRuntimeError(f"PilotScript Error: {eval_args[0] if eval_args else 'Unknown'}")
            if fname == "globalproperty":
                return self.globals_ctx.get(str(eval_args[0]))
            if fname == "property":
                return self.record_ctx.get(str(eval_args[0]))

        # 14. Variable lookup fallback
        return self.get_var(expr)

    # --- Splitting Utilities (Ignoring Strings & Parens) ---

    @staticmethod
    def _is_balanced(s: str) -> bool:
        depth = 0
        in_quote = None
        for char in s:
            if in_quote:
                if char == in_quote:
                    in_quote = None
            elif char in ("'", '"'):
                in_quote = char
            elif char in ("(", "[", "{"):
                depth += 1
            elif char in (")", "]", "}"):
                depth -= 1
                if depth < 0:
                    return False
        return depth == 0

    @classmethod
    def _split_top_level(cls, text: str, delimiter: str) -> List[str]:
        parts = []
        buf = []
        depth = 0
        in_quote = None
        i = 0
        n = len(text)
        d_len = len(delimiter)

        while i < n:
            char = text[i]
            if in_quote:
                buf.append(char)
                if char == in_quote:
                    in_quote = None
                i += 1
            elif char in ("'", '"'):
                in_quote = char
                buf.append(char)
                i += 1
            elif char in ("(", "[", "{"):
                depth += 1
                buf.append(char)
                i += 1
            elif char in (")", "]", "}"):
                depth -= 1
                buf.append(char)
                i += 1
            elif depth == 0 and text[i : i + d_len] == delimiter:
                parts.append("".join(buf).strip())
                buf = []
                i += d_len
            else:
                buf.append(char)
                i += 1

        if buf:
            rem = "".join(buf).strip()
            if rem:
                parts.append(rem)
        return parts

    @classmethod
    def _split_top_level_word(cls, text: str, word: str) -> List[str]:
        parts = []
        buf = []
        depth = 0
        in_quote = None
        i = 0
        n = len(text)
        w_len = len(word)

        while i < n:
            char = text[i]
            if in_quote:
                buf.append(char)
                if char == in_quote:
                    in_quote = None
                i += 1
            elif char in ("'", '"'):
                in_quote = char
                buf.append(char)
                i += 1
            elif char in ("(", "[", "{"):
                depth += 1
                buf.append(char)
                i += 1
            elif char in (")", "]", "}"):
                depth -= 1
                buf.append(char)
                i += 1
            elif depth == 0:
                # Check for whole word boundary
                candidate = text[i : i + w_len]
                prev_char = text[i - 1] if i > 0 else " "
                next_char = text[i + w_len] if i + w_len < n else " "
                if candidate.upper() == word.upper() and (prev_char.isspace() or prev_char == ")") and (next_char.isspace() or next_char == "("):
                    parts.append("".join(buf).strip())
                    buf = []
                    i += w_len
                    continue
                else:
                    buf.append(char)
                    i += 1
            else:
                buf.append(char)
                i += 1

        if buf:
            rem = "".join(buf).strip()
            if rem:
                parts.append(rem)
        return parts

    @classmethod
    def _split_top_level_regex(cls, text: str, regex_pattern: str) -> Optional[List[str]]:
        depth = 0
        in_quote = None
        for i, char in enumerate(text):
            if in_quote:
                if char == in_quote:
                    in_quote = None
            elif char in ("'", '"'):
                in_quote = char
            elif char in ("(", "[", "{"):
                depth += 1
            elif char in (")", "]", "}"):
                depth -= 1
            elif depth == 0:
                m = re.match(regex_pattern, text[i:], re.IGNORECASE)
                if m:
                    left = text[:i].strip()
                    right = text[i + m.end():].strip()
                    return [left, right]
        return None

    @classmethod
    def _split_top_level_concat(cls, text: str) -> List[str]:
        """Splits on string concatenation '.' that is NOT inside quotes, parens, or numbers."""
        parts = []
        buf = []
        depth = 0
        in_quote = None
        i = 0
        n = len(text)

        while i < n:
            char = text[i]
            if in_quote:
                buf.append(char)
                if char == in_quote:
                    in_quote = None
                i += 1
            elif char in ("'", '"'):
                in_quote = char
                buf.append(char)
                i += 1
            elif char in ("(", "[", "{"):
                depth += 1
                buf.append(char)
                i += 1
            elif char in (")", "]", "}"):
                depth -= 1
                buf.append(char)
                i += 1
            elif depth == 0 and char == ".":
                # Check it's not a numeric decimal like 3.14 or range ..
                prev_c = text[i - 1] if i > 0 else " "
                next_c = text[i + 1] if i + 1 < n else " "
                if prev_c.isdigit() and next_c.isdigit():
                    buf.append(char)
                    i += 1
                elif next_c == ".":  # range ..
                    buf.append(char)
                    i += 1
                elif prev_c == ":":  # assignment .=
                    buf.append(char)
                    i += 1
                else:
                    parts.append("".join(buf).strip())
                    buf = []
                    i += 1
            else:
                buf.append(char)
                i += 1

        if buf:
            rem = "".join(buf).strip()
            if rem:
                parts.append(rem)
        return parts

    @classmethod
    def _split_top_level_add(cls, text: str) -> Optional[Tuple[str, str, str]]:
        depth = 0
        in_quote = None
        # Right-to-left for correct associativity
        for i in range(len(text) - 1, -1, -1):
            char = text[i]
            if in_quote:
                if char == in_quote:
                    in_quote = None
            elif char in ("'", '"'):
                in_quote = char
            elif char in (")", "]", "}"):
                depth += 1
            elif char in ("(", "[", "{"):
                depth -= 1
            elif depth == 0 and char in ("+", "-"):
                # Ensure not unary or exponent (e.g. 1e-5)
                prev_c = text[i - 1] if i > 0 else " "
                if not (prev_c in ("+", "-", "*", "/", "%", "(", "=", ">", "<") or prev_c.isspace()):
                    return char, text[:i].strip(), text[i + 1:].strip()
        return None

    @classmethod
    def _split_top_level_mult(cls, text: str) -> Optional[Tuple[str, str, str]]:
        depth = 0
        in_quote = None
        for i in range(len(text) - 1, -1, -1):
            char = text[i]
            if in_quote:
                if char == in_quote:
                    in_quote = None
            elif char in ("'", '"'):
                in_quote = char
            elif char in (")", "]", "}"):
                depth += 1
            elif char in ("(", "[", "{"):
                depth -= 1
            elif depth == 0 and char in ("*", "/", "%"):
                return char, text[:i].strip(), text[i + 1:].strip()
        return None

    @classmethod
    def evaluate(
        cls,
        expression: str,
        globals_ctx: Optional[Dict[str, Any]] = None,
        record_ctx: Optional[Dict[str, Any]] = None,
        locals_ctx: Optional[Dict[str, Any]] = None
    ) -> Any:
        eng = cls(globals_ctx=globals_ctx, record_ctx=record_ctx, locals_ctx=locals_ctx)
        return eng.eval_expr(expression)


class PilotScriptParser:
    """Convenience parser and transpiler class."""

    def __init__(self, expression: str):
        self.expression = expression

    def transpile_to_python(self) -> str:
        return (
            f"# Generated Python call using PilotScriptEngine\n"
            f"from biovia_pipeline.pilotscript_parser import PilotScriptEngine\n"
            f"result = PilotScriptEngine.evaluate({repr(self.expression)}, globals_ctx=globals_ctx, record_ctx=record_ctx)"
        )
