import typer
from tgtoolz.config import I18NConfig
from tgtoolz.i18n.generator import I18NGenerator

app = typer.Typer()
i18n_app = typer.Typer()


@i18n_app.command("refresh")
def i18n_refresh(
    localization_file: str = typer.Option(
        None, "--localization-file", "-l", help="Path to localization JSON file"
    ),
    output_file: str = typer.Option(
        None, "--output-file", "-o", help="Path to output Python module"
    ),
    get_language_code_node_path: str = typer.Option(
        "tgtoolz.i18n.lang_code_node.LanguageCodeFromUserSourceNode", "--language-code-node-path", "-lc", help="Path to the language code node"
    ),
):
    if localization_file and output_file and get_language_code_node_path:
        config = I18NConfig(
            localization_file_path=localization_file,
            output_file_path=output_file,
            get_language_code_node_path=get_language_code_node_path,
        )
    else:
        config = I18NConfig.read_from_pyproject()
    if not config:
        typer.echo(
            "😔 Sorry, I can't refresh your i18n, because of lacking the configuration"
        )  # TODO
        return
    generator = I18NGenerator(config=config)
    generator.generate_i18n_class()
    typer.echo("✅ I18N module has been refreshed.")


app.add_typer(i18n_app, name="i18n")

if __name__ == "__main__":
    app()
