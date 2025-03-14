import re
from dataclasses import dataclass
from typing import Callable


@dataclass
class PluralForms:
    singular: str
    plural: str
    dual: str | None


@dataclass
class GenderForms:
    male: str
    female: str
    other: str | None


class Text:
    pass


@dataclass
class PlainText(Text):
    text: str


@dataclass
class FunctionCall(Text):
    name: str
    args: list[str]
    alias: str | None = None


class LanguageProcessor:
    def __init__(self):
        self.transform_mapping: dict[str, Callable[[FunctionCall], str]] = {
            "bold": self.transform_bold,
            "link": self.transform_link,
            "plural": self.transform_plural,
            "gender": self.transform_gender,
            "italic": self.transform_italic,
        }

        self._counter: int = 0
        self.plural_mappings: dict[str, PluralForms] = {}
        self.gender_mappings: dict[str, GenderForms] = {}

    def transform_bold(self, fc: FunctionCall) -> str:
        if len(fc.args) != 1:
            raise ValueError("Bold requires exactly 1 argument")
        return f"<b>{fc.args[0]}</b>"

    def transform_italic(self, fc: FunctionCall) -> str:
        if len(fc.args) != 1:
            raise ValueError("Italic requires exactly 1 argument")
        return f"<i>{fc.args[0]}</i>"

    def transform_link(self, fc: FunctionCall) -> str:
        if len(fc.args) != 2:
            raise ValueError("Link requires exactly 2 arguments")
        return f'<a href="{fc.args[1]}">{fc.args[0]}</a>'

    def transform_gender(self, fc: FunctionCall) -> str:
        if len(fc.args) not in (2, 3):
            raise ValueError("Gender requires 2 or 3 arguments")
        if fc.alias:
            key = fc.alias
        else:
            key = f"gender{self._counter}"
            self._counter += 1
        gender_data = GenderForms(
            male=fc.args[0],
            female=fc.args[1],
            other=fc.args[2] if len(fc.args) == 3 else None,
        )
        self.gender_mappings[key] = gender_data
        return f"{{{key}}}"

    def transform_plural(self, fc: FunctionCall) -> str:
        if len(fc.args) not in (2, 3):
            raise ValueError("Plural requires 2 or 3 arguments")
        if fc.alias:
            key = fc.alias
        else:
            key = f"plural{self._counter}"
            self._counter += 1
        plural_data = PluralForms(
            singular=fc.args[0],
            plural=fc.args[1],
            dual=fc.args[2] if len(fc.args) == 3 else None,
        )
        self.plural_mappings[key] = plural_data
        return f"{{{key}}}"

    def parse_and_render(self, text: str) -> str:
        elements: list[Text] = []
        pos = 0
        func_pattern = re.compile(
            r"@([a-zA-Z_]\w*)\(\s*(.*?)\)(?:\s+as\s+([a-zA-Z_]\w+))?"
        )
        for match in func_pattern.finditer(text):
            start, end = match.span()
            if start > pos:
                elements.append(PlainText(text[pos:start]))
            func_name = match.group(1)
            arg_string = match.group(2)
            alias = match.group(3)
            args = self._parse_arguments(arg_string)
            elements.append(FunctionCall(name=func_name, args=args, alias=alias))
            pos = end
        if pos < len(text):
            elements.append(PlainText(text[pos:]))
        result = ""
        for element in elements:
            if isinstance(element, PlainText):
                result += element.text
            elif isinstance(element, FunctionCall):
                try:
                    func_enum = element.name.lower()
                except ValueError:
                    result += f"@{element.name}({', '.join(element.args)})"
                    continue
                if func_enum in self.transform_mapping:
                    result += self.transform_mapping[func_enum](element)
                else:
                    result += f"@{element.name}({', '.join(element.args)})"
        result = self._strip_types_in_curly(result)
        return result

    def _parse_arguments(self, arg_string: str) -> list[str]:
        args: list[str] = []
        arg_pattern = re.compile(
            r'\s*(?:"((?:\\.|[^"\\])*)"|'  # Quoted string (group 1)
            r"(\{\s*([^}:]+)(?::[^}]+)?\s*\})|"  # Curly-braced token (group 2 full, group 3 token name)
            r"([^,]+))\s*(?:,|$)"  # Bare token (group 4)
        )
        for match in arg_pattern.finditer(arg_string):
            if match.group(1) is not None:
                args.append(match.group(1))
            elif match.group(2) is not None:
                token = match.group(3)
                args.append("{" + token + "}")
            elif match.group(4) is not None:
                args.append(match.group(4))
        return args

    def _strip_types_in_curly(self, text: str) -> str:
        return re.sub(r"\{([^}:]+):[^}]+\}", r"{\1}", text)
