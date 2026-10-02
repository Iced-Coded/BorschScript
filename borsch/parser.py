import re
from .errors import BorschSyntaxError

class Token:
    def __init__(self, kind, value, line):
        self.kind = kind      # 'OPEN_TAG', 'CLOSE_TAG', 'SELF_CLOSE_TAG'
        self.value = value    # Tag name (e.g. 'змінна', 'якщо')
        self.line = line
        self.attrs = {}       # Dictionary of attributes
        self.content = ""     # Inner text content

class BorschTranspiler:
    def __init__(self):
        # Map BorschScript tags to Python code generation rules
        self.tag_handlers = {
            "змінна": self._handle_variable,
            "друк": self._handle_print,
            "якщо": self._handle_if,
            "інакше": self._handle_else,
            "поки": self._handle_while,
            "функція": self._handle_function,
            "повернути": self._handle_return,
            "викликати": self._handle_call
        }

    def transpile(self, brsh_code: str) -> str:
        tokens = self._tokenize(brsh_code)
        python_code = self._generate_python(tokens)
        return python_code

    def _tokenize(self, code: str):
        tokens = []
        # Matches tags like: <tag attr="val">Content</tag> OR <tag attr="val" />
        tag_pattern = re.compile(
            r'<\s*(?P<close>/)?\s*(?P<tag>[\w\'-]+)(?P<attrs>[^/>]*)(?P<self_close>/)?\s*>'
        )
        
        pos = 0
        line_num = 1
        
        for match in tag_pattern.finditer(code):
            start, end = match.span()
            line_num += code[pos:start].count('\n')
            
            is_close = bool(match.group('close'))
            is_self_close = bool(match.group('self_close'))
            tag_name = match.group('tag').lower()
            raw_attrs = match.group('attrs')
            
            # Parse attributes (handles both "val" and 'val', plus ім'я/назва)
            attrs = {}
            attr_pattern = re.compile(r'([\w\'-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')')
            for attr_match in attr_pattern.finditer(raw_attrs):
                key = attr_match.group(1).replace("ім'я", "назва").replace("імʼя", "назва")
                val = attr_match.group(2) if attr_match.group(2) is not None else attr_match.group(3)
                attrs[key] = val

            token = Token(
                kind='CLOSE' if is_close else ('SELF_CLOSE' if is_self_close else 'OPEN'),
                value=tag_name,
                line=line_num
            )
            token.attrs = attrs

            # Capture text content between the previous position and this tag
            if not is_close:
                pos_next = match.end()
                # Find matching closing tag or next tag to extract text content
                next_tag = tag_pattern.search(code, pos_next)
                if next_tag:
                    raw_content = code[pos_next:next_tag.start()]
                    token.content = raw_content.strip()

            tokens.append(token)
            pos = end

        return tokens

    def _generate_python(self, tokens) -> str:
        python_lines = []
        indent_level = 0

        for token in tokens:
            prefix = "    " * indent_level

            if token.kind == 'CLOSE':
                # Dedent when closing a block tag
                if token.value in ["якщо", "інакше", "поки", "функція"]:
                    indent_level = max(0, indent_level - 1)
                continue

            if token.value not in self.tag_handlers:
                raise BorschSyntaxError(f"Рядок {token.line}: Невідомий тег <{token.value}>")

            handler = self.tag_handlers[token.value]
            line_code, increases_indent = handler(token, prefix)
            
            python_lines.append(line_code)
            if increases_indent:
                indent_level += 1

        return "\n".join(python_lines) + "\n"

    # --- TAG HANDLERS ---

    def _handle_variable(self, token, prefix):
        name = token.attrs.get("назва") or token.attrs.get("назва")
        val = token.content if token.content else "None"
        return f"{prefix}{name} = {val}", False

    def _handle_print(self, token, prefix):
        return f"{prefix}print({token.content})", False

    def _handle_if(self, token, prefix):
        cond = token.attrs.get("умова", "True")
        return f"{prefix}if {cond}:", True

    def _handle_else(self, token, prefix):
        # Dedicated handler for <інакше>
        return f"{prefix}else:", True

    def _handle_while(self, token, prefix):
        cond = token.attrs.get("умова", "True")
        return f"{prefix}while {cond}:", True

    def _handle_function(self, token, prefix):
        name = token.attrs.get("назва")
        args = token.attrs.get("аргументи", "")
        return f"{prefix}def {name}({args}):", True

    def _handle_return(self, token, prefix):
        val = token.content if token.content else "None"
        return f"{prefix}return {val}", False

    def _handle_call(self, token, prefix):
        name = token.attrs.get("назва")
        args = token.attrs.get("аргументи", "")
        return f"{prefix}{name}({args})", False