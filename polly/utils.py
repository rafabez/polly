"""
Utility functions for Polly
"""

import sys
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from .i18n import get_text

console = Console()


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
        except Exception:
            # Fallback to plain text if markdown parsing fails
            console.print(text)
    else:
        console.print(text)


def print_error(message: str):
    """Print error message in red"""
    console.print(f"[bold red]{get_text('label.error')}[/bold red] {message}")


def print_info(message: str):
    """Print info message in blue"""
    console.print(f"[bold blue]{get_text('label.info')}[/bold blue] {message}")


def print_success(message: str):
    """Print success message in green"""
    console.print(f"[bold green]{get_text('label.success')}[/bold green] {message}")


def print_code(code: str, language: str = "bash"):
    """Print code with syntax highlighting"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=False)
    console.print(syntax)


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
