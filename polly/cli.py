"""
Command-line interface for Polly
"""

import argparse
import sys
from typing import Optional
from .config import get_config, AVAILABLE_MODELS
from .prompts import get_available_modes
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    
    parser = argparse.ArgumentParser(
        prog="polly",
        description="Polly - AI Assistant for Linux Terminal (Powered by Pollinations.ai)",
        add_help=False,  # Disable default help to use custom
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional argument for prompt
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Your question or prompt (optional if using -e, -c, -d, etc.)"
    )
    
    # Mode flags
    mode_group = parser.add_argument_group("modes")
    mode_group.add_argument(
        "-e", "--explain",
        metavar="FILE",
        help="Explain the content of a file or piped input"
    )
    mode_group.add_argument(
        "-c", "--command",
        nargs="?",
        const=1,
        type=int,
        metavar="N",
        help="Get Linux/bash command (add number for multiple versions: -c3)"
    )
    mode_group.add_argument(
        "-ce", "--command-explain",
        action="store_true",
        help="Get Linux/bash command with explanations"
    )
    mode_group.add_argument(
        "-d", "--debug",
        nargs="?",
        const=True,
        metavar="FILE",
        help="Debug code or analyze errors (optionally from file)"
    )
    mode_group.add_argument(
        "-r", "--refactor",
        nargs="?",
        const=True,
        metavar="FILE",
        help="Get code improvement suggestions (optionally from file)"
    )
    mode_group.add_argument(
        "-x", "--motivational",
        action="store_true",
        help="Get a demotivational phrase (funny and ironic)"
    )
    mode_group.add_argument(
        "-t", "--translate",
        metavar="LANG",
        help="Translate text to specified language"
    )
    mode_group.add_argument(
        "-tf", "--translate-file",
        nargs=2,
        metavar=("LANG", "FILE"),
        help="Translate file content to specified language"
    )
    mode_group.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive chat mode"
    )
    
    # Model and parameters
    params_group = parser.add_argument_group("parameters")
    params_group.add_argument(
        "-m", "--model",
        choices=list(AVAILABLE_MODELS.keys()),
        help="Select AI model (default: gemini)"
    )
    params_group.add_argument(
        "--temperature",
        type=float,
        metavar="T",
        help="Control creativity 0.0-3.0 (default: 0.7)"
    )
    params_group.add_argument(
        "-s", "--stream",
        action="store_true",
        help="Enable streaming response"
    )
    params_group.add_argument(
        "-l", "--prompt-language",
        choices=["pt", "en", "pt-br", "portuguese", "english"],
        help="Language for prompts (default: pt - Portuguese)"
    )
    
    # Output options
    output_group = parser.add_argument_group("output")
    output_group.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Save response to file"
    )
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    output_group.add_argument(
        "--no-markdown",
        action="store_true",
        help="Disable markdown formatting"
    )
    
    # Configuration
    config_group = parser.add_argument_group("configuration")
    config_group.add_argument(
        "--config",
        action="store_true",
        help="Open configuration file"
    )
    config_group.add_argument(
        "--set-default-model",
        metavar="MODEL",
        choices=list(AVAILABLE_MODELS.keys()),
        help="Set default model"
    )
    config_group.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset configuration to defaults"
    )
    config_group.add_argument(
        "--set-language",
        metavar="LANG",
        choices=["pt", "en", "pt-br", "portuguese", "english"],
        help="Set default prompt language"
    )
    
    # Info
    info_group = parser.add_argument_group("information")
    info_group.add_argument(
        "--list-models",
        action="store_true",
        help="List available AI models"
    )
    info_group.add_argument(
        "--list-modes",
        action="store_true",
        help="List available prompt modes"
    )
    info_group.add_argument(
        "-v", "--version",
        action="version",
        version=f"Polly v{__version__}",
        help="Show version number"
    )
    info_group.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help message"
    )
    
    return parser


def validate_args(args) -> Optional[str]:
    """
    Validate argument combinations
    
    Returns:
        Error message if validation fails, None otherwise
    """
    # Count active modes
    modes = [
        args.explain,
        args.command,
        args.command_explain,
        args.debug,
        args.refactor,
        args.translate,
        args.translate_file,
        args.interactive
    ]
    active_modes = sum(1 for m in modes if m)
    
    if active_modes > 1:
        return "Error: Only one mode can be active at a time"
    
    # Check if prompt is needed
    needs_prompt = not (
        args.interactive or
        args.motivational or
        args.config or
        args.list_models or
        args.list_modes or
        args.reset_config or
        args.set_default_model or
        args.set_language
    )
    
    if needs_prompt and not args.prompt and not args.explain:
        # Check if debug, refactor, or translate-file mode has a file
        if (args.debug and args.debug != True) or (args.refactor and args.refactor != True) or args.translate_file:
            # Has file, no need for prompt
            pass
        # Check if stdin has data
        elif sys.stdin.isatty():
            return "Error: No prompt provided. Use 'polly --help' for usage information."
    
    # Validate temperature
    if args.temperature is not None:
        if args.temperature < 0.0 or args.temperature > 3.0:
            return "Error: Temperature must be between 0.0 and 3.0"
    
    return None


def get_mode_from_args(args) -> str:
    """Determine which mode is active from arguments"""
    if args.explain:
        return "explain"
    elif args.command:
        return "command"
    elif args.command_explain:
        return "command_explain"
    elif args.debug:
        return "debug"
    elif args.refactor:
        return "refactor"
    elif args.translate:
        return "translate"
    elif args.translate_file:
        return "translate"
    elif args.interactive:
        return "interactive"
    elif args.motivational:
        return "motivational"
    else:
        return "default"
