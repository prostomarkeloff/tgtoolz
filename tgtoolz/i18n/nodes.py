from telegrinder.node import ComposeError, UserSource, scalar_node


@scalar_node()
class LanguageCodeFromUserSourceNode:
    @classmethod
    def compose(cls, src: UserSource) -> str:
        return src.language_code.expect(ComposeError("User doesn't have language code"))
