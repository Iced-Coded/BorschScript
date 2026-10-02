import re
from dataclasses import dataclass, field

from .errors import BorschSyntaxError


@dataclass
class ASTNode:
    tag: str
    attrs: dict[str, str]
    line: int
    content: str = ""
    children: list["ASTNode"] = field(default_factory=list)


class BorschTranspiler:
    BLOCK_TAGS = {"якщо", "інакше", "поки", "функція"}

    def __init__(self):
        self.tag_handlers = {
            "змінна": self._handle_variable,
            "друк": self._handle_print,
            "якщо": self._handle_if,
            "інакше": self._handle_else,
            "поки": self._handle_while,
            "функція": self._handle_function,
            "повернути": self._handle_return,
            "викликати": self._handle_call,
        }

    def transpile(self, brsh_code: str) -> str:
        return self._generate_python(self._parse_ast(brsh_code)).rstrip() + "\n"

    def _parse_ast(self, code: str) -> list[ASTNode]:
        tag_pattern = re.compile(
            r"""<\s*(?P<close>/)?\s*(?P<tag>[\w'-]+)
            (?P<attrs>(?:\s+[\w'-]+\s*=\s*(?:"[^"]*"|'[^']*'))*)
            \s*(?P<self_close>/)?\s*>""",
            re.VERBOSE,
        )
        roots: list[ASTNode] = []
        stack: list[ASTNode] = []
        position = 0

        for match in tag_pattern.finditer(code):
            text = code[position:match.start()].strip()
            if text and stack:
                stack[-1].content = self._join_text(stack[-1].content, text)

            tag = match.group("tag").lower()
            line = code.count("\n", 0, match.start()) + 1

            if match.group("close"):
                if not stack:
                    raise BorschSyntaxError(
                        f"Рядок {line}: Неочікуваний закриваючий тег </{tag}>"
                    )
                if stack[-1].tag != tag:
                    raise BorschSyntaxError(
                        f"Рядок {line}: Очікувався </{stack[-1].tag}>, "
                        f"але знайдено </{tag}>"
                    )
                node = stack.pop()
                if stack:
                    stack[-1].children.append(node)
                else:
                    roots.append(node)
            else:
                node = ASTNode(
                    tag=tag,
                    attrs=self._parse_attrs(match.group("attrs")),
                    line=line,
                )
                if match.group("self_close"):
                    if stack:
                        stack[-1].children.append(node)
                    else:
                        roots.append(node)
                else:
                    stack.append(node)

            position = match.end()

        trailing_text = code[position:].strip()
        if trailing_text and stack:
            stack[-1].content = self._join_text(stack[-1].content, trailing_text)

        if stack:
            node = stack[-1]
            raise BorschSyntaxError(f"Рядок {node.line}: Не закрито тег <{node.tag}>")

        return roots

    @staticmethod
    def _join_text(existing: str, new: str) -> str:
        return f"{existing} {new}".strip()

    @staticmethod
    def _parse_attrs(raw_attrs: str) -> dict[str, str]:
        attrs: dict[str, str] = {}
        attr_pattern = re.compile(r"""([\w'-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""")
        for match in attr_pattern.finditer(raw_attrs):
            key = match.group(1).replace("ім'я", "назва").replace("імʼя", "назва")
            value = match.group(2) if match.group(2) is not None else match.group(3)
            attrs[key] = value
        return attrs

    def _generate_python(self, nodes: list[ASTNode], indent_level: int = 0) -> str:
        lines: list[str] = []

        for node in nodes:
            if node.tag not in self.tag_handlers:
                raise BorschSyntaxError(
                    f"Рядок {node.line}: Невідомий тег <{node.tag}>"
                )

            prefix = "    " * indent_level
            line_code, increases_indent = self.tag_handlers[node.tag](
                node, prefix, indent_level
            )
            lines.append(line_code)

            if increases_indent:
                if node.children:
                    lines.append(self._generate_python(node.children, indent_level + 1))
                else:
                    lines.append(f"{prefix}    pass")

        return "\n".join(line for line in lines if line)

    def _handle_variable(self, node, prefix, indent_level):
        name = node.attrs.get("назва")
        if not name:
            raise BorschSyntaxError(f"Рядок {node.line}: Відсутній атрибут назва")

        if len(node.children) == 1 and node.children[0].tag == "викликати":
            value = self._handle_call_expr(node.children[0])
        else:
            value = node.content if node.content else "None"
        return f"{prefix}{name} = {value}", False

    def _handle_call_expr(self, node) -> str:
        name = node.attrs.get("назва")
        if not name:
            raise BorschSyntaxError(f"Рядок {node.line}: Відсутній атрибут назва")
        return f"{name}({node.attrs.get('аргументи', '')})"

    def _handle_call(self, node, prefix, indent_level):
        return f"{prefix}{self._handle_call_expr(node)}", False

    def _handle_print(self, node, prefix, indent_level):
        return f"{prefix}print({node.content})", False

    def _handle_if(self, node, prefix, indent_level):
        return f"{prefix}if {node.attrs.get('умова', 'True')}:", True

    def _handle_else(self, node, prefix, indent_level):
        return f"{prefix}else:", True

    def _handle_while(self, node, prefix, indent_level):
        return f"{prefix}while {node.attrs.get('умова', 'True')}:", True

    def _handle_function(self, node, prefix, indent_level):
        name = node.attrs.get("назва")
        if not name:
            raise BorschSyntaxError(f"Рядок {node.line}: Відсутній атрибут назва")
        return f"{prefix}def {name}({node.attrs.get('аргументи', '')}):", True

    def _handle_return(self, node, prefix, indent_level):
        return f"{prefix}return {node.content if node.content else 'None'}", False
