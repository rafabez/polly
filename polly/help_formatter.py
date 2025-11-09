"""
Custom help formatter using Rich for beautiful output
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()


def print_help():
    """Print beautiful help message using Rich"""
    
    # Header
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🌸 Polly - AI Assistant for Linux Terminal 🌸[/bold cyan]\n"
        "[dim]Powered by Pollinations.ai[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    # Usage
    console.print("[bold yellow]USAGE[/bold yellow]")
    console.print("  [cyan]polly[/cyan] [OPTIONS] [PROMPT]")
    console.print()
    
    # Modes
    console.print("[bold yellow]MODES[/bold yellow]")
    modes_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    modes_table.add_column(style="cyan", width=25)
    modes_table.add_column(style="white")
    
    modes_table.add_row("-e, --explain FILE", "Explica conteúdo de arquivo")
    modes_table.add_row("-c[N], --command [N]", "Gera comando bash (use -c3 para 3 versões)")
    modes_table.add_row("-ce, --command-explain", "Gera comando com explicações")
    modes_table.add_row("-d, --debug [FILE]", "Analisa erros e debugga código")
    modes_table.add_row("-r, --refactor [FILE]", "Sugere melhorias de código")
    modes_table.add_row("-t, --translate LANG", "Traduz texto para idioma")
    modes_table.add_row("-tf LANG FILE", "Traduz arquivo para idioma")
    modes_table.add_row("-i, --interactive", "Modo chat interativo")
    modes_table.add_row("-x, --motivational", "Frase desmotivacional engraçada 😄")
    
    console.print(modes_table)
    console.print()
    
    # Parameters
    console.print("[bold yellow]PARÂMETROS[/bold yellow]")
    params_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    params_table.add_column(style="green", width=25)
    params_table.add_column(style="white")
    
    params_table.add_row("-m, --model MODEL", "Seleciona modelo de IA")
    params_table.add_row("--temperature T", "Criatividade 0.0-3.0 (padrão: 0.7)")
    params_table.add_row("-s, --stream", "Resposta em tempo real")
    params_table.add_row("-l, --prompt-language", "Idioma dos prompts (pt/en)")
    
    console.print(params_table)
    console.print()
    
    # Output
    console.print("[bold yellow]SAÍDA[/bold yellow]")
    output_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    output_table.add_column(style="magenta", width=25)
    output_table.add_column(style="white")
    
    output_table.add_row("-o, --output FILE", "Salva resposta em arquivo")
    output_table.add_row("--json", "Saída em formato JSON")
    output_table.add_row("--no-markdown", "Desabilita formatação markdown")
    
    console.print(output_table)
    console.print()
    
    # Configuration
    console.print("[bold yellow]CONFIGURAÇÃO[/bold yellow]")
    config_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    config_table.add_column(style="blue", width=25)
    config_table.add_column(style="white")
    
    config_table.add_row("--config", "Ver/editar configuração")
    config_table.add_row("--set-default-model", "Define modelo padrão")
    config_table.add_row("--set-language LANG", "Define idioma padrão")
    config_table.add_row("--reset-config", "Reseta configuração")
    
    console.print(config_table)
    console.print()
    
    # Info
    console.print("[bold yellow]INFORMAÇÃO[/bold yellow]")
    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    info_table.add_column(style="yellow", width=25)
    info_table.add_column(style="white")
    
    info_table.add_row("--list-models", "Lista modelos disponíveis")
    info_table.add_row("--list-modes", "Lista modos disponíveis")
    info_table.add_row("-v, --version", "Mostra versão")
    info_table.add_row("-h, --help", "Mostra esta ajuda")
    
    console.print(info_table)
    console.print()
    
    # Examples
    console.print("[bold yellow]EXEMPLOS[/bold yellow]")
    examples = [
        ("Pergunta simples", "polly 'O que é recursão?'"),
        ("Comando bash", "polly -c 'listar arquivos grandes'"),
        ("Explicar arquivo", "polly -e script.sh"),
        ("Debug arquivo", "polly -d api.py"),
        ("Refactor arquivo", "polly -r code.py"),
        ("Explicar com pipe", "cat api.py | polly"),
        ("Modo interativo", "polly -i"),
        ("Frase engraçada", "polly -x"),
        ("Modelo específico", "polly --model deepseek 'Explique Docker'"),
    ]
    
    for desc, cmd in examples:
        console.print(f"  [dim]{desc}:[/dim]")
        console.print(f"    [green]{cmd}[/green]")
    
    console.print()
    
    # Usage notes
    console.print("[bold yellow]💡 DICAS[/bold yellow]")
    console.print("  [dim]• Para explicar conteúdo via pipe, use:[/dim]")
    console.print("    [green]cat arquivo.py | polly[/green]  [dim](sem -e)[/dim]")
    console.print()
    console.print("  [dim]• O flag -e é apenas para arquivos:[/dim]")
    console.print("    [green]polly -e arquivo.py[/green]")
    console.print()
    console.print("  [dim]• Para outros modos com pipe, use a flag:[/dim]")
    console.print("    [green]cat error.log | polly -d[/green]")
    console.print("    [green]cat code.py | polly -r[/green]")
    console.print()
    console.print("  [dim]• Se um modelo estiver fora do ar, tente outro:[/dim]")
    console.print("    [green]polly --model gemini 'sua pergunta'[/green]")
    console.print("    [green]polly --model openai 'sua pergunta'[/green]")
    console.print()
