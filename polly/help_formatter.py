"""
Custom help formatter using Rich for beautiful output
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from .i18n import get_text

# Configure console with legacy_windows=False to enable better Unicode support on Windows
console = Console(legacy_windows=False)


def print_help():
    """Print beautiful help message using Rich"""

    # Header
    console.print()
    console.print(Panel(
        f"[bold green]Polly[/bold green] - {get_text('help.title')}",
        border_style="green"
    ))
    console.print(Panel(
        f"[dim]{get_text('help.powered_by')}[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Usage
    console.print(f"[bold yellow]{get_text('help.usage')}[/bold yellow]")
    console.print("  [cyan]polly[/cyan] [OPTIONS] [PROMPT]")
    console.print()

    # Modes
    console.print(f"[bold yellow]{get_text('help.modes')}[/bold yellow]")
    modes_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    modes_table.add_column(style="cyan", width=25)
    modes_table.add_column(style="white")

    modes_table.add_row("-e, --explain FILE", get_text("mode.explain"))
    modes_table.add_row("-c[N], --command [N]", get_text("mode.command"))
    modes_table.add_row("-ce, --command-explain", get_text("mode.command_explain"))
    modes_table.add_row("-d, --debug [FILE]", get_text("mode.debug"))
    modes_table.add_row("-r, --refactor [FILE]", get_text("mode.refactor"))
    modes_table.add_row("-t, --translate LANG", get_text("mode.translate"))
    modes_table.add_row("-tf LANG FILE", get_text("mode.translate_file"))
    modes_table.add_row("-i, --interactive", get_text("mode.interactive"))
    modes_table.add_row("-x, --motivational", get_text("mode.motivational"))

    console.print(modes_table)
    console.print()

    # Parameters
    console.print(f"[bold yellow]{get_text('help.parameters')}[/bold yellow]")
    params_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    params_table.add_column(style="green", width=25)
    params_table.add_column(style="white")

    params_table.add_row("-m, --model MODEL", get_text("param.model"))
    params_table.add_row("--temperature T", get_text("param.temperature"))
    params_table.add_row("-s, --stream", get_text("param.stream"))
    params_table.add_row("-l, --prompt-language", get_text("param.language"))
    params_table.add_row("--direct-api", get_text("param.direct_api"))

    console.print(params_table)
    console.print()

    # Output
    console.print(f"[bold yellow]{get_text('help.output')}[/bold yellow]")
    output_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    output_table.add_column(style="magenta", width=25)
    output_table.add_column(style="white")

    output_table.add_row("-o, --output FILE", get_text("output.file"))
    output_table.add_row("--pdf FILE", get_text("output.pdf"))
    output_table.add_row("--json", get_text("output.json"))
    output_table.add_row("--no-markdown", get_text("output.no_markdown"))

    console.print(output_table)
    console.print()

    # Configuration
    console.print(f"[bold yellow]{get_text('help.configuration')}[/bold yellow]")
    config_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    config_table.add_column(style="blue", width=25)
    config_table.add_column(style="white")

    config_table.add_row("--config", get_text("config.view"))
    config_table.add_row("--set-default-model", get_text("config.set_model"))
    config_table.add_row("--set-language LANG", get_text("config.set_language"))
    config_table.add_row("--set-os OS", get_text("config.set_os"))
    config_table.add_row("--show-os", get_text("config.show_os"))
    config_table.add_row("--reset-config", get_text("config.reset"))

    console.print(config_table)
    console.print()

    # Info
    console.print(f"[bold yellow]{get_text('help.information')}[/bold yellow]")
    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    info_table.add_column(style="yellow", width=25)
    info_table.add_column(style="white")

    info_table.add_row("--list-models", get_text("info.list_models"))
    info_table.add_row("--list-modes", get_text("info.list_modes"))
    info_table.add_row("-v, --version", get_text("info.version"))
    info_table.add_row("-h, --help", get_text("info.help"))

    console.print(info_table)
    console.print()

    # Examples
    console.print(f"[bold yellow]{get_text('help.examples')}[/bold yellow]")
    examples = [
        (get_text("example.basic"), "polly 'O que é recursão?'"),
        (get_text("example.command"), "polly -c 'listar arquivos grandes'"),
        (get_text("example.explain"), "polly -e script.sh"),
        (get_text("example.explain"), "polly -e documento.pdf"),
        (get_text("example.debug"), "polly -d api.py"),
        (get_text("example.explain"), "polly -r code.py"),
        (get_text("example.explain"), "polly 'Explique Docker' --pdf output.pdf"),
        (get_text("example.explain"), "cat api.py | polly"),
        (get_text("example.explain"), "polly -i"),
        (get_text("example.explain"), "polly -x"),
        (get_text("example.model"), "polly --model deepseek 'Explique Docker'"),
    ]

    for desc, cmd in examples:
        console.print(f"  [dim]{desc}:[/dim]")
        console.print(f"    [green]{cmd}[/green]")

    console.print()

    # Usage notes
    console.print(f"[bold yellow][i]{get_text('help.tips')}[/i][/bold yellow]")
    console.print(f"  [dim]• {get_text('tip.pipe')}[/dim]")
    console.print("    [green]cat arquivo.py | polly[/green]  [dim](sem -e)[/dim]")
    console.print()
    console.print(f"  [dim]• {get_text('tip.file_only')}[/dim]")
    console.print("    [green]polly -e arquivo.py[/green]")
    console.print()
    console.print(f"  [dim]• {get_text('tip.model_down')}[/dim]")
    console.print("    [green]polly --model gemini 'sua pergunta'[/green]")
    console.print("    [green]polly --model openai 'sua pergunta'[/green]")
    console.print()
    console.print(f"  [dim]• {get_text('tip.pdf_support')}[/dim]")
    console.print("    [green]polly -e relatorio.pdf[/green]  [dim](ler PDF)[/dim]")
    console.print("    [green]polly 'resumo' --pdf saida.pdf[/green]  [dim](gerar PDF)[/dim]")
    console.print()
