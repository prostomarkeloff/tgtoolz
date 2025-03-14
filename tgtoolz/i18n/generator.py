import os

from dataclasses import dataclass

from tgtoolz.config import I18NConfig
from tgtoolz.i18n.impl import (
    enrich_class_methods_arguments_with_plurals_and_genders,
    generate_final_code,
    parse_into_i18n_classes,
    parse_locales_from_text,
)


@dataclass
class I18NGenerator:
    config: I18NConfig

    def load_locales(self):
        with open(self.config.localization_file_path, "r", encoding="utf-8") as file:
            return parse_locales_from_text(file.read())

    def generate_i18n_class(self):
        classes = parse_into_i18n_classes(self.load_locales())
        for class_ in classes:
            enrich_class_methods_arguments_with_plurals_and_genders(class_)

        code = generate_final_code(classes)
        code = code.replace(
            "{GET_LANGUAGE_CODE_NODE}",
            self.config.get_language_code_node,
        )
        code = code.replace(
            "{GET_LANGUAGE_CODE_NODE_IMPORT}",
            self.config.get_language_code_node_import,
        )

        os.makedirs(os.path.dirname(self.config.output_file_path), exist_ok=True)
        with open(self.config.output_file_path, "w", encoding="utf-8") as f:
            f.write(code)
