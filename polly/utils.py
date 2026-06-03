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


def interactive_os_selection(config) -> Optional[str]:
    """
    Show interactive OS selection menu.

    Args:
        config: Configuration instance

    Returns:
        Selected OS value or None if cancelled
    """
    from .config import detect_os, normalize_os

    current_os = config.get("os", "auto")
    detected_os = detect_os()

    # OS options
    os_options = [
        {"code": "auto", "name": "Auto-detect", "name_pt": "Auto-detectar"},
        {"code": "linux", "name": "Linux", "name_pt": "Linux"},
        {"code": "darwin", "name": "macOS", "name_pt": "macOS"},
        {"code": "windows", "name": "Windows", "name_pt": "Windows"},
    ]

    print_info(f"{get_text('msg.os_selection')}\n")

    # Show detected OS
    detected_display = "macOS" if detected_os == "darwin" else detected_os.title()
    console.print(f"  [dim]Detected: {detected_display}[/dim]\n")

    # Display numbered list
    for idx, os_opt in enumerate(os_options, 1):
        code = os_opt["code"]
        # Normalize current_os for comparison
        normalized_current = current_os
        if current_os == "macos":
            normalized_current = "darwin"

        is_current = " ✓" if code == normalized_current else ""

        # Use appropriate name based on language
        current_lang = config.get_effective_language()
        name = os_opt["name_pt"] if current_lang == "pt" else os_opt["name"]

        # Show detected OS hint for auto
        if code == "auto":
            name = f"{name} ({detected_display})"

        console.print(f"  [cyan]{idx}.[/cyan] [bold]{name:25}[/bold][green]{is_current}[/green]")

    print()

    # Get user input
    try:
        user_input = input(f"Select OS (1-{len(os_options)}, or 'cancel'): ").strip()

        if user_input.lower() in ['cancel', 'quit', 'exit', 'q', '']:
            print_info(get_text("msg.cancelled"))
            return None

        # Try parsing as number
        if user_input.isdigit():
            idx = int(user_input)
            if 1 <= idx <= len(os_options):
                return os_options[idx - 1]["code"]
            else:
                print_error(f"{get_text('msg.invalid_selection')} 1-{len(os_options)}")
                return None

        # Try as OS name (exact or partial match, case-insensitive)
        user_lower = user_input.lower()

        # Handle macos alias
        if user_lower in ["macos", "mac", "osx"]:
            return "darwin"

        # Exact match
        os_codes = [opt["code"] for opt in os_options]
        if user_lower in os_codes:
            return user_lower

        # Partial match
        matches = [opt["code"] for opt in os_options if user_lower in opt["name"].lower()]
        if len(matches) == 1:
            print_info(f"{get_text('msg.auto_selected')} {matches[0]}")
            return matches[0]
        elif len(matches) > 1:
            print_error(f"{get_text('msg.ambiguous_input')} {', '.join(matches)}")
            return None
        else:
            print_error(f"{get_text('msg.unknown_os')} {user_input}")
            return None

    except KeyboardInterrupt:
        print("\n")
        print_info(get_text("msg.cancelled"))
        return None
    except Exception as e:
        print_error(f"{get_text('label.error')} {str(e)}")
        return None


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
    from .config import AVAILABLE_MODELS, fetch_text_models

    current_model = config.get("default_model")
    models = fetch_text_models()

    print_info(f"{get_text('msg.available_models')}\n")

    for idx, model in enumerate(models, 1):
        name = model.get("name", "unknown")
        description = model.get("description", "")
        flags = ""
        if model.get("reasoning"):
            flags += " [reasoning]"
        is_default = " ✓" if name == current_model else ""
        console.print(f"  [cyan]{idx:>2}.[/cyan] [bold]{name:<25}[/bold] {description}{flags}[green]{is_default}[/green]")

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


def interactive_config_editor(config) -> bool:
    """
    Interactive configuration editor menu.

    Args:
        config: Configuration instance

    Returns:
        True if changes were made, False otherwise
    """
    from rich.panel import Panel
    from rich.table import Table

    changes_made = False

    while True:
        console.print()
        console.print(Panel(
            "[bold cyan]Configuration Editor[/bold cyan]\n"
            "[dim]Current configuration settings[/dim]",
            border_style="cyan"
        ))
        console.print()

        # Display current configuration in a table
        config_table = Table(show_header=True, box=None, padding=(0, 2))
        config_table.add_column("Setting", style="cyan", width=20)
        config_table.add_column("Value", style="green")

        config_table.add_row("1. Model", config.get("default_model"))
        config_table.add_row("2. Language", config.get("language"))
        config_table.add_row("3. Temperature", str(config.get("temperature")))
        config_table.add_row("4. OS", config.get("os"))
        config_table.add_row("5. Stream", str(config.get("stream")))

        console.print(config_table)
        console.print()
        console.print("[dim]Options: [cyan]1-5[/cyan] to edit, [cyan]s[/cyan] to save, [cyan]q[/cyan] to quit[/dim]")
        console.print()

        try:
            choice = input("Select option: ").strip().lower()

            if choice in ['q', 'quit', 'exit']:
                if changes_made:
                    save_prompt = input("Save changes before exiting? (y/N): ").strip().lower()
                    if save_prompt in ['y', 'yes', 's', 'sim']:
                        if config.save_config():
                            print_success(get_text("msg.config_saved"))
                        else:
                            print_error(get_text("msg.config_failed"))
                return changes_made

            if choice in ['s', 'save']:
                if config.save_config():
                    print_success(get_text("msg.config_saved"))
                    changes_made = False
                else:
                    print_error(get_text("msg.config_failed"))
                continue

            # Edit model
            if choice == '1':
                console.print()
                selected_model = interactive_model_selection(config)
                if selected_model:
                    config.set("default_model", selected_model)
                    changes_made = True
                    print_success(f"{get_text('msg.model_set')} {selected_model}")

            # Edit language
            elif choice == '2':
                console.print()
                selected_lang = interactive_language_selection(config)
                if selected_lang:
                    config.set("language", selected_lang)
                    changes_made = True
                    print_success(f"{get_text('msg.language_set')} {selected_lang}")

            # Edit temperature
            elif choice == '3':
                console.print()
                selected_temp = interactive_temperature_selection(config)
                if selected_temp is not None:
                    config.set("temperature", selected_temp)
                    changes_made = True
                    print_success(f"{get_text('msg.temperature_set')} {selected_temp}")

            # Edit OS
            elif choice == '4':
                console.print()
                selected_os = interactive_os_selection(config)
                if selected_os:
                    config.set("os", selected_os)
                    changes_made = True
                    display_os = "macos" if selected_os == "darwin" else selected_os
                    print_success(f"{get_text('msg.os_set')} {display_os}")

            # Edit stream
            elif choice == '5':
                current_stream = config.get("stream", False)
                new_stream = not current_stream
                config.set("stream", new_stream)
                changes_made = True
                print_success(f"Stream set to: {new_stream}")

            else:
                print_error(get_text("msg.invalid_selection"))

        except KeyboardInterrupt:
            print("\n")
            if changes_made:
                save_prompt = input("Save changes before exiting? (y/N): ").strip().lower()
                if save_prompt in ['y', 'yes', 's', 'sim']:
                    if config.save_config():
                        print_success(get_text("msg.config_saved"))
                    else:
                        print_error(get_text("msg.config_failed"))
            return changes_made


def run_first_time_setup(config) -> bool:
    """
    Run first-time setup wizard for new users.

    Args:
        config: Configuration instance

    Returns:
        True if setup was completed, False if skipped
    """
    from rich.panel import Panel

    # Welcome message
    console.print()
    console.print(Panel(
        "[bold cyan]Welcome to Polly AI![/bold cyan]\n\n"
        "Let's set up your preferences.\n"
        "[dim]You can change these settings anytime with config commands.[/dim]",
        border_style="cyan",
        title="[bold]First-Time Setup[/bold]"
    ))
    console.print()

    # Ask if user wants to run setup
    try:
        response = input("Run setup wizard? (Y/n): ").strip().lower()
        if response in ['n', 'no']:
            print_info(get_text("msg.setup_skipped"))
            # Save default config
            config.save_config()
            return False
    except KeyboardInterrupt:
        print("\n")
        print_info(get_text("msg.setup_skipped"))
        config.save_config()
        return False

    console.print()
    console.print("[bold yellow]Step 1/3:[/bold yellow] Select your preferred language")
    console.print()

    # Language selection
    selected_lang = interactive_language_selection(config)
    if selected_lang:
        config.set("language", selected_lang)

    console.print()
    console.print("[bold yellow]Step 2/3:[/bold yellow] Select your default AI model")
    console.print()

    # Model selection
    selected_model = interactive_model_selection(config)
    if selected_model:
        config.set("default_model", selected_model)

    console.print()
    console.print("[bold yellow]Step 3/3:[/bold yellow] Select temperature preset")
    console.print()

    # Temperature selection
    selected_temp = interactive_temperature_selection(config)
    if selected_temp is not None:
        config.set("temperature", selected_temp)

    # Save configuration
    if config.save_config():
        console.print()
        console.print(Panel(
            "[bold green]Setup complete![/bold green]\n\n"
            f"Model: [cyan]{config.get('default_model')}[/cyan]\n"
            f"Language: [cyan]{config.get('language')}[/cyan]\n"
            f"Temperature: [cyan]{config.get('temperature')}[/cyan]\n\n"
            "[dim]Use 'polly -h' to see all available options.[/dim]",
            border_style="green",
            title="[bold]Configuration Saved[/bold]"
        ))
        console.print()
        return True
    else:
        print_error(get_text("msg.config_failed"))
        return False
