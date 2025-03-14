from dataclasses import dataclass
import json
import re
import typing

from typing import Any
from tgtoolz.i18n.constants import I18N_BASE_CODE
from tgtoolz.i18n.lang_parser import GenderForms, LanguageProcessor, PluralForms

# {
#     "ClassName": {
#         "MethodName": {
#             "ru": ["Привет", "Привки"],
#             "en": "Hi"
#         }
#     }
# }


def remove_none(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: remove_none(v) for k, v in data.items() if v is not None}  # type: ignore
    elif isinstance(data, list):
        return [remove_none(item) for item in data if item is not None]  # type: ignore
    else:
        return data


def custom_default(o: Any) -> Any:
    if hasattr(o, "__dataclass_fields__"):
        return remove_none(o.__dict__)
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


type I18NClassName = str
type I18NMethodName = str
type I18NMethodsInClass = dict[I18NMethodName, dict[LocaleName, TranslationUnparsed]]
type LocaleName = str  # "ru", "en", etc
type TranslationUnparsed = str | list[str]
type LocalesJson = dict[I18NClassName, I18NMethodsInClass]

type ArgumentName = str
type ArgumentType = str


@dataclass
class I18NTranslationMethod:
    arguments: dict[ArgumentName, ArgumentType]

    method_name: str


@dataclass
class Translation:
    text: list[str]

    plural_mapping: dict[str, PluralForms]
    gender_mapping: dict[str, GenderForms]


@dataclass
class I18NTranslationClass:
    class_name: str
    methods: list[I18NTranslationMethod]

    translations: dict[I18NMethodName, dict[LocaleName, Translation]]


def parse_locales_from_text(text: str) -> LocalesJson:
    exc = RuntimeError("Your i18n locales JSON is empty")

    locales = json.loads(text)
    if not isinstance(locales, dict):
        raise exc

    locales = typing.cast(LocalesJson, locales)

    if not len(locales):
        raise exc

    return locales


def parse_arguments(translation: str) -> dict[ArgumentName, ArgumentType]:
    pattern = r"\{(\w+):([^}]+)\}"
    matches = re.findall(pattern, translation)
    return {key: value for key, value in matches}


def parse_i18n_methods(methods: I18NMethodsInClass) -> list[I18NTranslationMethod]:
    parsed_methods: list[I18NTranslationMethod] = []

    for method_name, translations_locales in methods.items():
        first_locale_translation = translations_locales.get(
            list(translations_locales.keys())[0]
        )
        if first_locale_translation is None:
            raise ValueError("Method doesn't have any translation")
        if isinstance(first_locale_translation, list):
            first_locale_translation = first_locale_translation[0]

        arguments = parse_arguments(first_locale_translation)
        new_method = I18NTranslationMethod(method_name=method_name, arguments=arguments)
        parsed_methods.append(new_method)

    return parsed_methods


def parse_i18n_translations(
    methods: I18NMethodsInClass,
) -> dict[I18NMethodName, dict[LocaleName, Translation]]:
    translations: dict[I18NMethodName, dict[LocaleName, Translation]] = {}
    for method_name, translations_locales in methods.items():
        translations[method_name] = {}
        for locale_name, translation_unparsed in translations_locales.items():
            processor = LanguageProcessor()

            text: list[str] = []
            if isinstance(translation_unparsed, str):
                translation_unparsed = [translation_unparsed]
            for unparsed in translation_unparsed:
                text.append(processor.parse_and_render(unparsed))

            translations[method_name][locale_name] = Translation(
                text=text,
                plural_mapping=processor.plural_mappings,
                gender_mapping=processor.gender_mappings,
            )

    return translations


def parse_into_i18n_classes(locales: LocalesJson) -> list[I18NTranslationClass]:
    classes: list[I18NTranslationClass] = []

    for class_name, methods in locales.items():
        new_class = I18NTranslationClass(
            class_name=class_name,
            methods=parse_i18n_methods(methods),
            translations=parse_i18n_translations(methods),
        )
        classes.append(new_class)

    return classes


def enrich_class_methods_arguments_with_plurals_and_genders(
    i18n_class: I18NTranslationClass,
):
    for method in i18n_class.methods:
        first_locale_translation = i18n_class.translations[method.method_name].get(
            list(i18n_class.translations[method.method_name].keys())[0]
        )
        assert first_locale_translation

        for plural_key in first_locale_translation.plural_mapping.keys():
            method.arguments[plural_key] = (
                'Literal["plural", "singular", "dual"] | Plurality'
            )

        for gender_key in first_locale_translation.gender_mapping.keys():
            method.arguments[gender_key] = 'Literal["male", "female", "other"] | Gender'


def generate_methods_code(methods: list[I18NTranslationMethod]) -> str:
    code = ""
    for method in methods:
        formatted_args_types = ", ".join(
            [f"{arg_name}: {arg_t}" for arg_name, arg_t in method.arguments.items()]
        )
        formatted_args_values = ", ".join(
            [f"{arg_name}={arg_name}" for arg_name in method.arguments.keys()]
        )
        code += f"    def {method.method_name}(self, {formatted_args_types}) -> str:\n"
        code += f"""        return self._get(_key="{method.method_name}", {formatted_args_values})"""
        code += "\n\n"

    return code


def generate_class_code(class_: I18NTranslationClass) -> str:
    import json

    methods_code = generate_methods_code(class_.methods)

    code = f"""
class {class_.class_name}(I18NBase):
    _translations = {json.dumps(class_.translations, indent=4, ensure_ascii=False, default=custom_default)}

    def __init__(self, lang_code: str):
        super().__init__(lang_code)

{methods_code}
    """
    return code


def generate_final_code(classes: list[I18NTranslationClass]) -> str:
    classes_code = ""
    for class_ in classes:
        classes_code += generate_class_code(class_)

    code = f"""{I18N_BASE_CODE}

    {classes_code}
    """

    return code
