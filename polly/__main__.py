"""
Main entry point for Polly
"""

import sys
import json
import random
from pathlib import Path
from .cli import create_parser, validate_args, get_mode_from_args
from .help_formatter import print_help
from .api import PollinationsAPI
from .config import get_config, AVAILABLE_MODELS
from .prompts import get_prompt, get_available_modes
from .utils import (
    print_response, print_error, print_info, print_success,
    print_code, read_stdin, read_file, stream_response,
    show_spinner, truncate_context
)
from .i18n import get_text


def handle_config_commands(args):
    """Handle configuration-related commands"""
    config = get_config()

    if args.list_models:
        print_info(f"{get_text('msg.available_models')}\n")

        # Try to fetch models dynamically from API
        try:
            # Create API instance (use direct API if flag is set)
            use_direct = getattr(args, 'direct_api', False)
            api_temp = PollinationsAPI(use_direct_api=use_direct)
            models = api_temp.get_available_models(use_cache=True)

            for model in models:
                name = model.get("name", "unknown")
                description = model.get("description", "")
                default = " (default)" if name == config.get("default_model") else ""

                # Filter out placeholder/unknown descriptions
                # Show description only if it's valid (not empty, not same as name, not containing "unknown")
                if description and description != name and "unknown" not in description.lower():
                    print(f"  • {name:15} - {description}{default}")
                else:
                    # Just show the model name when description is not available
                    print(f"  • {name}{default}")
        except Exception as e:
            # Fallback to hardcoded models if API fetch fails
            print(f"  ({get_text('msg.cached_models')})\n")
            for model, description in AVAILABLE_MODELS.items():
                default = " (default)" if model == config.get("default_model") else ""
                print(f"  • {model:15} - {description}{default}")

        return True

    if args.list_modes:
        print_info(f"{get_text('msg.available_modes')}\n")
        for mode, description in get_available_modes().items():
            print(f"  • {mode:18} - {description}")
        return True

    if args.set_default_model:
        config.set("default_model", args.set_default_model)
        if config.save_config():
            print_success(f"{get_text('msg.model_set')} {args.set_default_model}")
        else:
            print_error(get_text("msg.config_failed"))
        return True

    if args.reset_config:
        config.reset_to_defaults()
        print_success(get_text("msg.config_reset"))
        return True

    if args.set_language:
        config.set("language", args.set_language)
        if config.save_config():
            print_success(f"{get_text('msg.language_set')} {args.set_language}")
        else:
            print_error(get_text("msg.config_failed"))
        return True

    if args.set_os:
        from .config import normalize_os
        try:
            # Normalize the OS value (handles case-insensitive input)
            normalized_os = normalize_os(args.set_os)
            config.set("os", normalized_os)
            if config.save_config():
                # Display normalized value and show user-friendly format
                display_os = "macos" if normalized_os == "darwin" else normalized_os
                print_success(f"{get_text('msg.os_set')} {display_os}")
            else:
                print_error(get_text("msg.config_failed"))
        except ValueError as e:
            print_error(str(e))
        return True

    if args.show_os:
        from .config import detect_os
        detected_os = detect_os()
        configured_os = config.get("os", "auto")
        effective_os = config.get_effective_os()

        # Normalize darwin to macos for display
        display_detected = "macos" if detected_os == "darwin" else detected_os
        display_effective = "macos" if effective_os == "darwin" else effective_os
        display_configured = "macos" if configured_os == "darwin" else configured_os

        print_info(f"{get_text('msg.os_detected')} {display_detected}")
        print_info(f"{get_text('msg.os_current')} {display_configured}")
        if configured_os == "auto":
            print_info(f"  → Effective: {display_effective}")
        return True

    if args.config:
        config_file = config.config_file
        if config_file.exists():
            print_info(f"{get_text('msg.config_file')} {config_file}")
            print(f"\n{get_text('msg.current_config')}:")
            for key, value in config.config.items():
                print(f"  {key}: {value}")
        else:
            print_info(f"{get_text('msg.no_config')} {config_file}")
            config.save_config()
        return True
    
    return False


def handle_interactive_mode(api: PollinationsAPI, args):
    """Handle interactive chat mode"""
    print_info(f"{get_text('msg.interactive_help')}\n")

    config = get_config()
    model = args.model or config.get("default_model")
    temperature = args.temperature if args.temperature is not None else config.get("temperature")
    language = getattr(args, 'prompt_language', None) or config.get_effective_language()
    os_type = config.get_effective_os()

    # Initialize conversation with system message
    system_prompt, _ = get_prompt("interactive", language=language, os_type=os_type)
    messages = [{"role": "system", "content": system_prompt}]

    print(f"[Model: {model}, Temperature: {temperature}]\n")

    while True:
        try:
            # Get user input
            user_input = input(f"{get_text('msg.you')} ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print_info(get_text("msg.goodbye"))
                break

            if user_input.lower() == "clear":
                messages = [{"role": "system", "content": system_prompt}]
                print_success(get_text("msg.context_cleared"))
                continue

            # Add user message
            messages.append({"role": "user", "content": user_input})

            # Truncate context if needed (Pollinations has small context window)
            messages = truncate_context(messages, max_chars=5000)

            # Get response
            print(f"\n{get_text('msg.polly')} ", end="")

            if args.stream:
                response = api.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    stream=True
                )
                assistant_message = ""
                for chunk in response:
                    print(chunk, end="", flush=True)
                    assistant_message += chunk
                print("\n")
            else:
                with show_spinner(get_text("msg.thinking")):
                    response = api.chat_completion(
                        messages=messages,
                        model=model,
                        temperature=temperature,
                        stream=False
                    )
                print_response(response, format_markdown=not args.no_markdown)
                assistant_message = response

            # Add assistant response to history
            messages.append({"role": "assistant", "content": assistant_message})

        except KeyboardInterrupt:
            print("\n")
            print_info(get_text("msg.goodbye"))
            break
        except Exception as e:
            print_error(str(e))


def handle_standard_query(api: PollinationsAPI, args, content: str, mode: str):
    """Handle standard (non-interactive) queries"""
    config = get_config()
    model = args.model or config.get("default_model")
    temperature = args.temperature if args.temperature is not None else config.get("temperature")
    language = getattr(args, 'prompt_language', None) or config.get_effective_language()
    os_type = config.get_effective_os()

    # Generate random seed for motivational mode to get different responses
    seed = random.randint(1, 1000000) if mode == "motivational" else None

    # Get prompt based on mode
    if mode == "translate":
        # Get target language from either -t or -tf
        target_lang = args.translate if args.translate else args.translate_file[0]
        system_prompt, user_prompt = get_prompt(mode, content, language=language, target_language=target_lang, os_type=os_type)
    elif mode == "command":
        # Command mode - check for number of versions
        # Support both -cN format and legacy --command-versions
        num_versions = 1
        if args.command and args.command > 1:
            num_versions = args.command
        elif hasattr(args, 'command_versions') and args.command_versions > 1:
            num_versions = args.command_versions

        if num_versions > 1:
            system_prompt, user_prompt = get_prompt(mode, content, language=language, num_versions=num_versions, os_type=os_type)
        else:
            system_prompt, user_prompt = get_prompt(mode, content, language=language, os_type=os_type)
    else:
        system_prompt, user_prompt = get_prompt(mode, content, language=language, os_type=os_type)
    
    # Prepare messages for chat completion
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        if args.stream:
            response = api.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                seed=seed,
                stream=True
            )
            result = ""
            for chunk in response:
                print(chunk, end="", flush=True)
                result += chunk
            print()
        else:
            with show_spinner("Thinking..."):
                result = api.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    seed=seed,
                    stream=False
                )
            
            # Special formatting for command mode
            if mode == "command":
                print_code(result.strip(), language="bash")
            else:
                print_response(result, format_markdown=not args.no_markdown)
        
        # Save to file if requested
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print_success(f"{get_text('msg.response_saved')} {args.output}")
            except Exception as e:
                print_error(f"{get_text('msg.failed_save')} {str(e)}")

        # Save as PDF if requested
        if args.pdf:
            from .pdf_handler import write_pdf
            title = f"Polly - {mode.title()} Mode" if mode else "Polly Output"
            if write_pdf(result, args.pdf, title=title):
                pass  # Success message printed by write_pdf
            else:
                print_error(get_text("msg.failed_pdf"))
        
        # JSON output
        if args.json:
            output = {
                "model": model,
                "temperature": temperature,
                "mode": mode,
                "response": result
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print_error(str(e))
        sys.exit(1)


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle help
    if hasattr(args, 'help') and args.help:
        print_help()
        return
    
    # Validate arguments
    error = validate_args(args)
    if error:
        print_error(error)
        sys.exit(1)
    
    # Handle config commands
    if handle_config_commands(args):
        return

    # Initialize API (with direct API flag if specified)
    use_direct_api = getattr(args, 'direct_api', False)
    api = PollinationsAPI(use_direct_api=use_direct_api)
    
    # Handle interactive mode
    if args.interactive:
        handle_interactive_mode(api, args)
        return
    
    # Determine mode
    mode = get_mode_from_args(args)
    
    # Get content from various sources
    content = None
    
    # Motivational mode doesn't need content
    if args.motivational:
        content = ""  # Empty content, prompt is self-contained
    
    # From file (explain, debug, or refactor mode)
    elif args.explain:
        try:
            content = read_file(args.explain)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)
    
    # Debug mode with file
    elif args.debug and args.debug != True:
        try:
            content = read_file(args.debug)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)
    
    # Refactor mode with file
    elif args.refactor and args.refactor != True:
        try:
            content = read_file(args.refactor)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)
    
    # Translate file mode
    elif args.translate_file:
        try:
            content = read_file(args.translate_file[1])  # Second arg is the file
        except Exception as e:
            print_error(str(e))
            sys.exit(1)
    
    # From stdin (piped input)
    elif not sys.stdin.isatty():
        content = read_stdin()
    
    # From prompt argument
    elif args.prompt:
        content = " ".join(args.prompt)
    
    # Check if content is required (motivational mode doesn't need it)
    if not content and not args.motivational:
        print_error(get_text("msg.no_input"))
        sys.exit(1)
    
    # Handle the query
    handle_standard_query(api, args, content, mode)


if __name__ == "__main__":
    main()
