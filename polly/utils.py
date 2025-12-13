"""
Utility functions for Polly
"""

import sys
import platform
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from .i18n import get_text

# Configure console with legacy_windows=False to enable better Unicode support on Windows
# This helps with emoji display while maintaining compatibility
console = Console(legacy_windows=False)


def print_response(text: str, format_markdown: bool = True):
    """
    Print AI response with formatting

    Args:
        text: The text to print
        format_markdown: Whether to render as markdown
    """
    if format_markdown:
        try:
            md = Markdown(text)
            console.print(md)
        except UnicodeEncodeError:
            # Windows console encoding issue - print with ASCII-safe fallback
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            print(safe_text)
            print(f"\n{get_text('msg.unicode_warning')}" if 'msg.unicode_warning' in dir() else "\nNote: Some characters couldn't be displayed due to console encoding.")
        except Exception:
            # Fallback to plain text if markdown parsing fails
            try:
                console.print(text)
            except UnicodeEncodeError:
                safe_text = text.encode('ascii', errors='replace').decode('ascii')
                print(safe_text)
    else:
        try:
            console.print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            print(safe_text)


def print_error(message: str):
    """Print error message in red"""
    try:
        console.print(f"[bold red]{get_text('label.error')}[/bold red] {message}")
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        safe_message = message.encode('ascii', errors='replace').decode('ascii')
        print(f"Error: {safe_message}")


def print_info(message: str):
    """Print info message in blue"""
    try:
        console.print(f"[bold blue]{get_text('label.info')}[/bold blue] {message}")
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        safe_message = message.encode('ascii', errors='replace').decode('ascii')
        print(f"Info: {safe_message}")


def print_success(message: str):
    """Print success message in green"""
    console.print(f"[bold green]{get_text('label.success')}[/bold green] {message}")


def print_warning(message: str):
    """Print warning message in yellow"""
    console.print(f"[bold yellow]{get_text('label.warning')}[/bold yellow] {message}")


def print_code(code: str, language: str = "bash"):
    """Print code with syntax highlighting"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=False)
    console.print(syntax)


def print_panel(content: str, title: str = "Polly", border_style: str = "blue"):
    """Print content in a panel"""
    panel = Panel(content, title=title, border_style=border_style)
    console.print(panel)


def read_stdin() -> Optional[str]:
    """Read input from stdin (for piping)"""
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return None


def read_file(filepath: str) -> str:
    """
    Read file contents (supports PDF files)
    
    Args:
        filepath: Path to the file
    
    Returns:
        File contents as string
    
    Raises:
        Exception if file cannot be read
    """
    from .pdf_handler import is_pdf_file, read_pdf
    
    # Check if it's a PDF file
    if is_pdf_file(filepath):
        content = read_pdf(filepath)
        if content is None:
            raise Exception(get_text("pdf.no_text"))
        return content

    # Regular text file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise Exception(get_text("file.not_found", filepath=filepath))
    except PermissionError:
        raise Exception(get_text("file.permission", filepath=filepath))
    except UnicodeDecodeError:
        raise Exception(get_text("file.encoding"))
    except Exception as e:
        raise Exception(get_text("file.read_error", str=str(e)))


def stream_response(generator, format_markdown: bool = True):
    """
    Stream response chunks to console

    Args:
        generator: Generator yielding response chunks
        format_markdown: Whether to format as markdown
    """
    accumulated = ""
    try:
        for chunk in generator:
            accumulated += chunk
            console.print(chunk, end="", markup=False)
        console.print()  # New line at the end
        return accumulated
    except KeyboardInterrupt:
        console.print(f"\n[yellow]{get_text('file.interrupted')}[/yellow]")
        return accumulated


def show_spinner(message: str = "Thinking..."):
    """
    Show a spinner with message
    
    Returns:
        Live context manager for spinner
    """
    spinner = Spinner("dots", text=message)
    return Live(spinner, console=console, transient=True)


def truncate_context(messages: list, max_chars: int = 5000) -> list:
    """
    Truncate conversation context to fit within limits
    Keeps system message and most recent messages
    
    Args:
        messages: List of message dicts
        max_chars: Maximum total characters
    
    Returns:
        Truncated message list
    """
    if not messages:
        return messages
    
    # Calculate current size
    total_chars = sum(len(msg.get("content", "")) for msg in messages)
    
    if total_chars <= max_chars:
        return messages
    
    # Keep system message if present
    system_msg = None
    user_messages = []
    
    for msg in messages:
        if msg.get("role") == "system":
            system_msg = msg
        else:
            user_messages.append(msg)
    
    # Keep most recent messages
    truncated = []
    if system_msg:
        truncated.append(system_msg)
        max_chars -= len(system_msg.get("content", ""))
    
    # Add messages from most recent backwards
    current_chars = 0
    for msg in reversed(user_messages):
        msg_chars = len(msg.get("content", ""))
        if current_chars + msg_chars <= max_chars:
            truncated.insert(1 if system_msg else 0, msg)
            current_chars += msg_chars
        else:
            break
    
    return truncated


def interactive_temperature_selection(config) -> Optional[float]:
    """
    Show interactive temperature preset selection menu.

    Args:
        config: Configuration instance

    Returns:
        Selected temperature value or None if cancelled
    """
    from .config import TEMPERATURE_PRESETS

    current_temp = config.get("temperature", 0.7)

    # Get current language for descriptions
    current_lang = config.get_effective_language()
    desc_key = "description_pt" if current_lang == "pt" else "description"

    print_info(f"{get_text('msg.temperature_presets')}\n")

    # Display numbered list
    presets = list(TEMPERATURE_PRESETS.items())
    for idx, (preset_name, preset_data) in enumerate(presets, 1):
        value = preset_data["value"]
        description = preset_data[desc_key]
        is_current = " ✓" if abs(value - current_temp) < 0.01 else ""

        console.print(f"  [cyan]{idx}.[/cyan] [bold]{preset_name.title():12}[/bold] ({value}) - {description}[green]{is_current}[/green]")

    # Add custom option
    console.print(f"  [cyan]{len(presets) + 1}.[/cyan] [bold]Custom[/bold]      (0.0-3.0) - {get_text('msg.custom_value')}")

    print()

    # Get user input
    try:
        user_input = input(f"Select preset (1-{len(presets) + 1}, or 'cancel'): ").strip()

        if user_input.lower() in ['cancel', 'quit', 'exit', 'q', '']:
            print_info(get_text("msg.cancelled"))
            return None

        # Try parsing as number
        if user_input.isdigit():
            idx = int(user_input)
            if 1 <= idx <= len(presets):
                preset_name = presets[idx - 1][0]
                return TEMPERATURE_PRESETS[preset_name]["value"]
            elif idx == len(presets) + 1:
                # Custom value
                try:
                    custom_input = input(f"{get_text('msg.enter_temperature')} (0.0-3.0): ").strip()
                    custom_value = float(custom_input)
                    if 0.0 <= custom_value <= 3.0:
                        return custom_value
                    else:
                        print_error(f"{get_text('msg.invalid_temperature')} (0.0-3.0)")
                        return None
                except ValueError:
                    print_error(get_text("msg.invalid_number"))
                    return None
            else:
                print_error(f"{get_text('msg.invalid_selection')} 1-{len(presets) + 1}")
                return None

        # Try as preset name (exact or partial match)
        preset_names = [name for name, _ in presets]
        if user_input.lower() in preset_names:
            return TEMPERATURE_PRESETS[user_input.lower()]["value"]

        # Partial match
        matches = [name for name in preset_names if user_input.lower() in name.lower()]
        if len(matches) == 1:
            print_info(f"{get_text('msg.auto_selected')} {matches[0]}")
            return TEMPERATURE_PRESETS[matches[0]]["value"]
        elif len(matches) > 1:
            print_error(f"{get_text('msg.ambiguous_input')} {', '.join(matches)}")
            return None
        else:
            # Try as direct numeric value
            try:
                value = float(user_input)
                if 0.0 <= value <= 3.0:
                    return value
                else:
                    print_error(f"{get_text('msg.invalid_temperature')} (0.0-3.0)")
                    return None
            except ValueError:
                print_error(f"{get_text('msg.unknown_preset')} {user_input}")
                return None

    except KeyboardInterrupt:
        print("\n")
        print_info(get_text("msg.cancelled"))
        return None
    except Exception as e:
        print_error(f"{get_text('label.error')} {str(e)}")
        return None


def interactive_language_selection(config) -> Optional[str]:
    """
    Show interactive language selection menu.

    Args:
        config: Configuration instance

    Returns:
        Selected language code or None if cancelled
    """
    from .config import detect_language

    current_lang = config.get("language", "auto")
    detected_lang = detect_language()

    # Language options
    languages = [
        {"code": "auto", "name": get_text("lang.auto", lang="en"), "name_pt": get_text("lang.auto", lang="pt")},
        {"code": "en", "name": "English", "name_pt": "Inglês"},
        {"code": "pt", "name": "Portuguese", "name_pt": "Português"},
    ]

    print_info(f"{get_text('msg.available_languages')}\n")

    # Show detected language
    if current_lang == "auto":
        detected_display = "English" if detected_lang == "en" else "Português"
        console.print(f"  [dim]Detected: {detected_display}[/dim]\n")

    # Display numbered list
    for idx, lang in enumerate(languages, 1):
        is_current = " ✓" if lang["code"] == current_lang else ""
        # Show name in both languages
        display_name = f"{lang['name']} / {lang['name_pt']}" if lang["code"] != "auto" else lang["name"]
        console.print(f"  [cyan]{idx}.[/cyan] [bold]{display_name}[/bold][green]{is_current}[/green]")

    print()

    # Get user input
    try:
        user_input = input(f"Select language (1-{len(languages)}, or 'cancel'): ").strip()

        if user_input.lower() in ['cancel', 'quit', 'exit', 'q', '']:
            print_info(get_text("msg.cancelled"))
            return None

        # Try parsing as number
        if user_input.isdigit():
            idx = int(user_input)
            if 1 <= idx <= len(languages):
                return languages[idx - 1]["code"]
            else:
                print_error(f"{get_text('msg.invalid_selection')} 1-{len(languages)}")
                return None

        # Try as language code (exact match)
        lang_codes = [lang["code"] for lang in languages]
        if user_input.lower() in lang_codes:
            return user_input.lower()

        # Try partial match
        matches = [lang["code"] for lang in languages if user_input.lower() in lang["name"].lower() or user_input.lower() in lang["name_pt"].lower()]
        if len(matches) == 1:
            print_info(f"{get_text('msg.auto_selected')} {matches[0]}")
            return matches[0]
        elif len(matches) > 1:
            print_error(f"{get_text('msg.ambiguous_input')} {', '.join(matches)}")
            return None
        else:
            print_error(f"{get_text('msg.unknown_language')} {user_input}")
            return None

    except KeyboardInterrupt:
        print("\n")
        print_info(get_text("msg.cancelled"))
        return None
    except Exception as e:
        print_error(f"{get_text('label.error')} {str(e)}")
        return None


def interactive_model_selection(config) -> Optional[str]:
    """
    Show interactive model selection menu.

    Args:
        config: Configuration instance

    Returns:
        Selected model name or None if cancelled
    """
    from .config import AVAILABLE_MODELS
    from .api import PollinationsAPI

    current_model = config.get("default_model")

    # Try to fetch dynamic models, fallback to hardcoded
    try:
        api = PollinationsAPI()
        models = api.get_available_models(use_cache=True)
    except:
        models = [{"name": k, "description": v} for k, v in AVAILABLE_MODELS.items()]

    print_info(f"{get_text('msg.available_models')}\n")

    # Display numbered list
    for idx, model in enumerate(models, 1):
        name = model.get("name", "unknown")
        description = model.get("description", "")
        is_default = " ✓" if name == current_model else ""

        # Format output
        if description and description != name and "unknown" not in description.lower():
            console.print(f"  [cyan]{idx}.[/cyan] [bold]{name:18}[/bold] - {description}[green]{is_default}[/green]")
        else:
            console.print(f"  [cyan]{idx}.[/cyan] [bold]{name}[/bold][green]{is_default}[/green]")

    print()

    # Get user input
    try:
        user_input = input(f"Select model (1-{len(models)}, model name, or 'cancel'): ").strip()

        if user_input.lower() in ['cancel', 'quit', 'exit', 'q', '']:
            print_info(get_text("msg.cancelled"))
            return None

        # Try parsing as number
        if user_input.isdigit():
            idx = int(user_input)
            if 1 <= idx <= len(models):
                return models[idx - 1]["name"]
            else:
                print_error(f"{get_text('msg.invalid_selection')} 1-{len(models)}")
                return None

        # Try as model name (exact or partial match)
        model_names = [m["name"] for m in models]

        # Exact match
        if user_input in model_names:
            return user_input

        # Partial match
        matches = [name for name in model_names if user_input.lower() in name.lower()]
        if len(matches) == 1:
            print_info(f"{get_text('msg.auto_selected')} {matches[0]}")
            return matches[0]
        elif len(matches) > 1:
            print_error(f"{get_text('msg.ambiguous_input')} {', '.join(matches)}")
            return None
        else:
            print_error(f"{get_text('msg.unknown_model')} {user_input}")
            return None

    except KeyboardInterrupt:
        print("\n")
        print_info(get_text("msg.cancelled"))
        return None
    except Exception as e:
        print_error(f"{get_text('label.error')} {str(e)}")
        return None
