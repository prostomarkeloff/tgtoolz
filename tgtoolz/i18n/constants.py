I18N_BASE_CODE = """# AUTOGENERATED FILE - DO NOT EDIT MANUALLY (tgtoolz)

from telegrinder.node import scalar_node

import typing
{GET_LANGUAGE_CODE_NODE_IMPORT}

@scalar_node()
class I18NBase:
    def __init__(self, lang_code: str):
        self.lang_code = lang_code

    def get(self, key: str, translations: dict[str, dict[str, str]], **kwargs: typing.Any) -> str:
        entry = translations.get(key, {{}})
        text = entry.get(self.lang_code, key)
        return text.format(**kwargs) if kwargs else text

    @classmethod
    def compose(cls, lang_code: {GET_LANGUAGE_CODE_NODE}) -> typing.Self:
        return cls(lang_code=lang_code)

"""
