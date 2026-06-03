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
from .config import get_config, AVAILABLE_MODELS, fetch_text_models
from .prompts import get_prompt, get_available_modes
from .utils import (
    print_response, print_error, print_info, print_success, print_warning,
    print_code, read_stdin, read_file, stream_response,
    show_spinner, truncate_context, interactive_model_selection,
    interactive_language_selection, interactive_temperature_selection,
    interactive_os_selection, run_first_time_setup, interactive_config_editor
)
from .i18n import get_text


def handle_config_commands(args):
    """Handle configuration-related commands"""
    config = get_config()

    if args.list_models:
        print_info(f"{get_text('msg.available_models')}\n")

        models = fetch_text_models()
        default_model = config.get("default_model")

        for model in models:
            name = model.get("name", "unknown")
            description = model.get("description", "")
            flags = ""
            if model.get("reasoning"):
                flags += " [reasoning]"
            if model.get("is_specialized"):
                flags += " [specialized]"
            is_default = " (default)" if name == default_model else ""
            print(f"  • {name:<25} {description}{flags}{is_default}")

        print(f"\n  {len(models)} models available. Use -m <name> to select.")
        return True

    if args.list_modes:
        print_info(f"{get_text('msg.available_modes')}\n")
        for mode, description in get_available_modes().items():
            print(f"  • {mode:18} - {description}")
        return True

    if args.set_default_model is not None:
        # Interactive mode - show model selection menu
        if args.set_default_model == "__interactive__":
            selected_model = interactive_model_selection(config)
            if selected_model:
                config.set("default_model", selected_model)
                if config.save_config():
                    print_success(f"{get_text('msg.model_set')} {selected_model}")
                else:
                    print_error(get_text("msg.config_failed"))
            # If None, user cancelled - just return
        else:
            # Direct mode - set model directly
            config.set("default_model", args.set_default_model)
            if config.save_config():
                print_success(f"{get_text('msg.model_set')} {args.set_default_model}")
            else:
                print_error(get_text("msg.config_failed"))
        return True

    if args.reset_config:
        # Show warning and current config
        print_warning(get_text("msg.reset_warning"))
        print()
        print_info(get_text("msg.reset_current"))
        for key, value in config.config.items():
            print(f"  • {key}: {value}")
        print()

        # Ask for confirmation
        try:
            confirmation = input(get_text("msg.reset_confirm") + " ").strip().lower()
            if confirmation in ['y', 's', 'yes', 'sim']:
                config.reset_to_defaults()
                print_success(get_text("msg.config_reset"))
            else:
                print_info(get_text("msg.reset_aborted"))
        except KeyboardInterrupt:
            print("\n")
            print_info(get_text("msg.reset_aborted"))
        return True

    if args.set_language is not None:
        # Interactive mode - show language selection menu
        if args.set_language == "__interactive__":
            selected_lang = interactive_language_selection(config)
            if selected_lang:
                config.set("language", selected_lang)
                if config.save_config():
                    print_success(f"{get_text('msg.language_set')} {selected_lang}")
                else:
                    print_error(get_text("msg.config_failed"))
            # If None, user cancelled - just return
        else:
            # Direct mode - set language directly
            config.set("language", args.set_language)
            if config.save_config():
                print_success(f"{get_text('msg.language_set')} {args.set_language}")
            else:
                print_error(get_text("msg.config_failed"))
        return True

    if args.set_temperature is not None:
        # Interactive mode - show temperature preset selection menu
        if args.set_temperature == "__interactive__":
            selected_temp = interactive_temperature_selection(config)
            if selected_temp is not None:
                config.set("temperature", selected_temp)
                if config.save_config():
                    print_success(f"{get_text('msg.temperature_set')} {selected_temp}")
                else:
                    print_error(get_text("msg.config_failed"))
            # If None, user cancelled - just return
        else:
            # Direct mode - set temperature directly (preset name or numeric value)
            from .config import TEMPERATURE_PRESETS

            # Check if it's a preset name
            if args.set_temperature.lower() in TEMPERATURE_PRESETS:
                temp_value = TEMPERATURE_PRESETS[args.set_temperature.lower()]["value"]
                config.set("temperature", temp_value)
                if config.save_config():
                    print_success(f"{get_text('msg.temperature_set')} {temp_value} ({args.set_temperature})")
                else:
                    print_error(get_text("msg.config_failed"))
            else:
                # Try as numeric value
                try:
                    temp_value = float(args.set_temperature)
                    if 0.0 <= temp_value <= 3.0:
                        config.set("temperature", temp_value)
                        if config.save_config():
                            print_success(f"{get_text('msg.temperature_set')} {temp_value}")
                        else:
                            print_error(get_text("msg.config_failed"))
                    else:
                        print_error(f"{get_text('msg.invalid_temperature')} (0.0-3.0)")
                except ValueError:
                    print_error(f"{get_text('msg.unknown_preset')} {args.set_temperature}")
        return True

    if args.set_os is not None:
        from .config import normalize_os

        # Interactive mode - show OS selection menu
        if args.set_os == "__interactive__":
            selected_os = interactive_os_selection(config)
            if selected_os:
                config.set("os", selected_os)
                if config.save_config():
                    # Display normalized value and show user-friendly format
                    display_os = "macos" if selected_os == "darwin" else selected_os
                    print_success(f"{get_text('msg.os_set')} {display_os}")
                else:
                    print_error(get_text("msg.config_failed"))
            # If None, user cancelled - just return
        else:
            # Direct mode - set OS directly
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
            print_info(f"  -> Effective: {display_effective}")
        return True

    if args.config:
        # Launch interactive config editor
        interactive_config_editor(config)
        return True

    if args.save_profile:
        if config.save_profile(args.save_profile):
            print_success(f"{get_text('msg.profile_saved')} {args.save_profile}")
        else:
            print_error(get_text("msg.config_failed"))
        return True

    if args.load_profile:
        if config.load_profile(args.load_profile):
            print_success(f"{get_text('msg.profile_loaded')} {args.load_profile}")
        else:
            print_error(f"{get_text('msg.profile_not_found')} {args.load_profile}")
        return True

    if args.list_profiles:
        profiles = config.list_profiles()
        if profiles:
            print_info(f"{get_text('msg.available_profiles')}\n")
            for profile in profiles:
                print(f"  • {profile}")
        else:
            print_info(get_text("msg.no_profiles"))
        return True

    if args.delete_profile:
        if config.delete_profile(args.delete_profile):
            print_success(f"{get_text('msg.profile_deleted')} {args.delete_profile}")
        else:
            print_error(f"{get_text('msg.profile_not_found')} {args.delete_profile}")
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

    # Get config instance early to check first-run status
    config = get_config()

    # Run first-time setup wizard if this is the first run
    # Skip wizard if running config commands or help
    is_config_command = (
        args.config or
        args.list_models or
        args.list_modes or
        args.reset_config or
        args.set_default_model is not None or
        args.set_language is not None or
        args.set_temperature is not None or
        args.set_os is not None or
        args.show_os or
        args.save_profile or
        args.load_profile or
        args.list_profiles or
        args.delete_profile
    )

    if config.is_first_run and not is_config_command:
        run_first_time_setup(config)

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
