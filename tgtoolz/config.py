from dataclasses import dataclass
from typing import Optional

import toml

PYPROJECT_FILE = "pyproject.toml"


@dataclass
class I18NConfig:
    localization_file_path: str
    output_file_path: str
    get_language_code_node_path: str
    get_language_code_node_import: str = ""
    get_language_code_node: str = ""

    def __post_init__(self):
        parts = self.get_language_code_node_path.split(".")
        self.get_language_code_node_import = f"from {'.'.join(self.get_language_code_node_path.split('.')[0:-1])} import {parts[-1]}"

        self.get_language_code_node = parts[-1]

    @classmethod
    def read_from_pyproject(cls) -> Optional["I18NConfig"]:
        try:
            config = toml.load(PYPROJECT_FILE)
            config_i18n = config.get("tool", {}).get("tgtoolz", {}).get("i18n", {})
            if not config_i18n:
                return

            return cls(
                localization_file_path=config_i18n["localization_file"],
                output_file_path=config_i18n["output_file"],
                get_language_code_node_path=config_i18n.get(
                    "get_language_code_node_path",
                    "tgtoolz.i18n.nodes.LanguageCodeFromUserSourceNode",
                ),
            )
        except (FileNotFoundError, toml.TomlDecodeError, KeyError):
            return
