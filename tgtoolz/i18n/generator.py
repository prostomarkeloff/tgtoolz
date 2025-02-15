import os
import json
import re
import copy

from dataclasses import dataclass

from tgtoolz.config import I18NConfig
from tgtoolz.i18n.constants import I18N_BASE_CODE


PARAM_PATTERN = re.compile(r"\{(\w+):(\w+)\}")


def extract_params(translation: str):
    return {match[0]: match[1] for match in PARAM_PATTERN.findall(translation)}


@dataclass
class I18NGenerator:
    config: I18NConfig

    def load_locals(self) -> dict[str, dict[str, dict[str, str]]]:
        with open(self.config.localization_file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def generate_i18n_class(self):
        translations = self.load_locals()

        code = copy.copy(I18N_BASE_CODE)
        print(code)
        code = code.format(
            GET_LANGUAGE_CODE_NODE=self.config.get_language_code_node,
            GET_LANGUAGE_CODE_NODE_IMPORT=self.config.get_language_code_node_import,
        )

        for category, items in translations.items():
            class_name = list(category)
            class_name[0] = class_name[0].capitalize()
            class_name = "".join(class_name)

            code += f"\n\nclass {class_name}(I18NBase):\n"
            code += f"    _translations = {json.dumps(items, indent=4)}\n"

            code += f"""
    def __init__(self, lang_code: str):
        super().__init__(lang_code)
    """

            for key, entry in items.items():
                sample_translation = entry.get("en", "")
                if sample_translation:
                    sample_translation = (
                        f"Sample translation: {sample_translation} (en)"
                    )

                params = extract_params(sample_translation)

                param_list = ", ".join(
                    f"{param}: {ptype}" for param, ptype in params.items()
                )
                param_list = f", {param_list}" if param_list else ""

                method_code = f"""
    def {key}(self{param_list}) -> str:
        \"\"\"
        {sample_translation}
        \"\"\"
        return self.get("{key}", self._translations, {", ".join([f"{param}={param}" for param in params.keys()])})
    """
                code += method_code

        os.makedirs(os.path.dirname(self.config.output_file_path), exist_ok=True)
        with open(self.config.output_file_path, "w", encoding="utf-8") as f:
            f.write(code)
