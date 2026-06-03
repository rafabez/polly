"""
Command-line interface for Polly
"""

import argparse
import sys
from typing import Optional
from .config import AVAILABLE_MODELS, fetch_text_models
from . import __version__


def _get_model_names() -> list:
    """Return canonical model names for argparse choices (cached, fast after first call)."""
    try:
        models = fetch_text_models()
        return [m["name"] for m in models]
    except Exception:
        return list(AVAILABLE_MODELS.keys())


class OptionalIntAction(argparse.Action):
    """Custom action to handle optional integer arguments like -c or -c3"""
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            # -c without value, use default of 1
            setattr(namespace, self.dest, 1)
        elif values.isdigit():
            # -c3 or -c 3 with a number, use the provided value
            setattr(namespace, self.dest, int(values))
        else:
            # Value is not a digit, treat as if -c was used without a number (default to 1)
            # This handles cases like "polly -c how do I..." where "how" would be consumed
            # Instead, we default to 1 and let "how" be part of the prompt
            setattr(namespace, self.dest, 1)
            # Put the non-integer value back into the prompt by prepending it
            if not hasattr(namespace, '_extra_prompt'):
                namespace._extra_prompt = []
            namespace._extra_prompt.append(values)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    model_names = _get_model_names()

    parser = argparse.ArgumentParser(
        prog="polly",
        description='Polly - Cross-Platform AI Terminal Assistant',
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
        const=None,
        action=OptionalIntAction,
        metavar="N",
        help="Get Linux/bash command (optionally specify N versions, e.g., -c3)"
    )
    mode_group.add_argument(
        "--command-versions",
        type=int,
        metavar="N",
        default=1,
        help="Number of command versions (deprecated: use -cN instead)"
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
        choices=model_names,
        help="Select AI model (use -lm to list all available models)"
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
    params_group.add_argument(
        "--direct-api",
        action="store_true",
        help="Use direct Pollinations API (bypass proxy backend)"
    )
    params_group.add_argument(
        "--no-memory",
        action="store_true",
        help="Don't use or update conversation memory for this query"
    )
    params_group.add_argument(
        "--cache",
        action="store_true",
        help="Enable response cache for this query (ignores response_cache_enabled)"
    )
    params_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable response cache for this query"
    )

    # Output options
    output_group = parser.add_argument_group("output")
    output_group.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Save response to file"
    )
    output_group.add_argument(
        "--pdf",
        metavar="FILE",
        help="Save response as PDF file"
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
        "-C", "--config",
        action="store_true",
        help="Interactive configuration editor"
    )
    config_group.add_argument(
        "-M", "--set-default-model",
        metavar="MODEL",
        nargs="?",
        const="__interactive__",
        choices=model_names + ["__interactive__"],
        help="Set default model (interactive if no model specified)"
    )
    config_group.add_argument(
        "-R", "--reset-config",
        action="store_true",
        help="Reset configuration to defaults"
    )
    config_group.add_argument(
        "-L", "--set-language",
        metavar="LANG",
        nargs="?",
        const="__interactive__",
        choices=["pt", "en", "pt-br", "portuguese", "english", "__interactive__"],
        help="Set default prompt language (interactive if no language specified)"
    )
    config_group.add_argument(
        "-T", "--set-temperature",
        metavar="PRESET",
        nargs="?",
        const="__interactive__",
        help="Set default temperature preset (interactive if no preset specified)"
    )
    config_group.add_argument(
        "-O", "--set-os",
        metavar="OS",
        nargs="?",
        const="__interactive__",
        help="Set default OS (interactive if no OS specified)"
    )
    config_group.add_argument(
        "--show-os",
        action="store_true",
        help="Display detected/configured OS"
    )
    config_group.add_argument(
        "--save-profile",
        metavar="NAME",
        help="Save current configuration as a named profile"
    )
    config_group.add_argument(
        "--load-profile",
        metavar="NAME",
        help="Load a named profile"
    )
    config_group.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all saved profiles"
    )
    config_group.add_argument(
        "--delete-profile",
        metavar="NAME",
        help="Delete a named profile"
    )

    # Info
    info_group = parser.add_argument_group("information")
    info_group.add_argument(
        "--context",
        action="store_true",
        help="Show the active conversation memory for this terminal"
    )
    info_group.add_argument(
        "--forget",
        action="store_true",
        help="Clear the conversation memory for this terminal"
    )
    info_group.add_argument(
        "--update",
        action="store_true",
        help="Update Polly to the latest version from GitHub"
    )
    info_group.add_argument(
        "--rescan",
        action="store_true",
        help="Rescan and refresh system context (OS, shell, tools)"
    )
    info_group.add_argument(
        "--show-system",
        action="store_true",
        help="Show detected system information"
    )
    info_group.add_argument(
        "--history",
        action="store_true",
        help="Print recent conversation history"
    )
    info_group.add_argument(
        "--history-clear",
        action="store_true",
        help="Clear the conversation history log"
    )
    info_group.add_argument(
        "--purge",
        action="store_true",
        help="Wipe ALL local Polly state (memory, history, caches)"
    )
    info_group.add_argument(
        "-lm", "--list-models",
        action="store_true",
        help="List available AI models"
    )
    info_group.add_argument(
        "-lmo", "--list-modes",
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


def parse_args(argv: Optional[list] = None):
    """Parse command-line arguments"""
    args = create_parser().parse_args(argv)

    # Handle extra prompt items that were consumed by optional arguments
    if hasattr(args, '_extra_prompt') and args._extra_prompt:
        # Prepend extra items to the prompt
        if args.prompt is None:
            args.prompt = []
        elif not isinstance(args.prompt, list):
            args.prompt = [args.prompt]

        # Split extra prompt items if they contain spaces (when passed as a single quoted string)
        extra_parts = []
        for item in args._extra_prompt:
            if ' ' in item:
                extra_parts.extend(item.split())
            else:
                extra_parts.append(item)

        args.prompt = extra_parts + list(args.prompt)
        delattr(args, '_extra_prompt')

    return args


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
        args.set_default_model is not None or
        args.set_language is not None or
        args.set_temperature is not None or
        args.set_os or
        args.show_os or
        args.save_profile or
        args.load_profile or
        args.list_profiles or
        args.delete_profile or
        args.context or
        args.forget or
        args.history or
        args.history_clear or
        args.purge or
        args.update or
        args.rescan or
        args.show_system
    )

    if needs_prompt and not args.prompt and not args.explain:
        # Check if debug, refactor, or translate-file mode has a file
        if (args.debug and not args.debug) or (args.refactor and not args.refactor) or args.translate_file:
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
