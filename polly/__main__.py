"""
Main entry point for Polly
"""

import sys
import json
import random
from .cli import create_parser, validate_args, get_mode_from_args
from .help_formatter import print_help
from .api import PollinationsAPI
from .config import get_config, fetch_text_models, fetch_health_stats
from .prompts import get_prompt, get_available_modes
from . import memory, cache, system_context, executor, config_edit, agent
from .utils import (
    print_response, print_error, print_info, print_success, print_warning,
    print_code, read_stdin, read_file,
    show_spinner, truncate_context, interactive_model_selection,
    interactive_language_selection, interactive_temperature_selection,
    interactive_os_selection, run_first_time_setup, interactive_config_editor
)
from .i18n import get_text


def handle_config_commands(args):
    """Handle configuration-related commands"""
    config = get_config()

    if args.list_models:
        # Apply provider overrides if passed alongside -lm
        if getattr(args, "provider", None):
            config.set("provider_type", args.provider)
        if getattr(args, "base_url", None):
            config.set("provider_base_url", args.base_url)

        provider_type = config.get("provider_type", "pollinations")
        use_direct_api = getattr(args, 'direct_api', False)
        api_for_list = PollinationsAPI(use_direct_api=use_direct_api)

        if api_for_list.use_custom_provider:
            from .config import get_provider_base_url
            base = get_provider_base_url(config)
            print_info(f"Models from {provider_type} ({base}):\n")
            models = api_for_list.get_available_models()
            if not models:
                print_info(get_text("msg.provider_no_models", provider=provider_type))
                return True
            for m in models:
                name = m.get("name", "?")
                print(f"  • {name}")
            print(f"\n  {len(models)} models available. Use -m <name> to select.")
            return True

        print_info(f"{get_text('msg.available_models')}\n")

        models = fetch_text_models()
        health = fetch_health_stats()
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

            # Health badge from Tinybird data
            badge = ""
            h = health.get(name)
            if h:
                pct = h["success_pct"]
                p50 = h["p50_ms"]
                badge = f" {pct}% ~{p50}ms"

            print(f"  • {name:<25} {description}{flags}{badge}{is_default}")

        print(f"\n  {len(models)} models available. Use -m <name> to select.")
        return True

    if args.list_modes:
        print_info(f"{get_text('msg.available_modes')}\n")
        for mode, description in get_available_modes().items():
            print(f"  • {mode:18} - {description}")
        return True

    if args.forget:
        if memory.clear_session():
            print_success(get_text("msg.memory_cleared"))
        else:
            print_info(get_text("msg.memory_empty"))
        return True

    if args.context:
        ctx = memory.format_context()
        if ctx:
            print_info(get_text("msg.memory_header"))
            print()
            print(ctx)
            print(get_text("msg.memory_log_note", path=memory.history_path_str()))
        else:
            print_info(get_text("msg.memory_empty"))
        return True

    if args.revert:
        config_edit.revert_file(args.revert)
        return True

    if getattr(args, "enable_agent", False):
        config.set("agent_enabled", True)
        config.save_config()
        print_success(get_text("msg.agent_enabled"))
        return True

    if args.list_skills:
        from .skills import list_skills
        print_info(f"{get_text('msg.skills_header')}\n")
        lang = config.get_effective_language()
        for skill in list_skills():
            desc_key = "description_pt" if lang == "pt" else "description_en"
            desc = skill.get(desc_key) or skill.get("description_en", "")
            print(f"  • {skill['name']:<12} {desc}")
        return True

    if args.skill:
        from .skills import run_skill
        from . import system_context as _sc
        task = " ".join(args.prompt) if args.prompt else ""
        if not task:
            print_error(get_text("msg.no_input"))
            sys.exit(1)
        ctx = _sc.get_or_collect(config.get("system_context_ttl_hours", 24))
        cmds = run_skill(args.skill, task, ctx)
        if not cmds:
            print_info(get_text("msg.skill_not_found", name=args.skill))
            return True
        dry = getattr(args, "dry_run", False)
        if len(cmds) == 1:
            cmd_to_run = cmds[0]
        else:
            cmd_to_run = executor.pick_command(cmds)
        if cmd_to_run:
            print_code(cmd_to_run, language="bash")
            executor.execute(cmd_to_run, dry_run=dry)
        return True

    if args.rescan:
        ctx = system_context.collect()
        system_context.save(ctx)
        print_success(get_text("msg.system_rescanned"))
        print_info(get_text("msg.system_header"))
        print(system_context.summary(ctx))
        return True

    if args.show_system:
        ctx = system_context.get_or_collect(
            ttl_hours=config.get("system_context_ttl_hours", 24)
        )
        if ctx:
            print_info(get_text("msg.system_header"))
            print()
            for k, v in ctx.items():
                if k == "collected_at":
                    import datetime
                    ts = datetime.datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M")
                    print(f"  collected_at : {ts}")
                elif k == "tools" and isinstance(v, dict):
                    for tool, ver in v.items():
                        print(f"  {tool:<15}: {ver}")
                else:
                    print(f"  {k:<15}: {v}")
            print()
            print(f"  summary: {system_context.summary(ctx)}")
        else:
            print_info(get_text("msg.system_none"))
        return True

    if args.update:
        import subprocess
        import shutil
        repo = "git+https://github.com/rafabez/polly.git"
        manual_cmd = f"pip install --upgrade {repo}"
        print_info(get_text("msg.updating"))
        if shutil.which("pipx"):
            cmd = ["pipx", "install", repo, "--force"]
        else:
            print_info(get_text("msg.update_no_pipx", cmd=manual_cmd))
            return True
        try:
            result = subprocess.run(cmd, check=True)
            if result.returncode == 0:
                print_success(get_text("msg.update_done"))
            else:
                print_error(get_text("msg.update_failed"))
        except Exception as e:
            print_error(f"{get_text('msg.update_failed')} ({e})")
        return True

    if args.history:
        hist = memory.read_history()
        if hist:
            print(hist)
        else:
            print_info(get_text("msg.history_empty"))
        return True

    if args.history_clear:
        if memory.clear_history():
            print_success(get_text("msg.history_cleared"))
        else:
            print_info(get_text("msg.history_empty"))
        return True

    if args.purge:
        try:
            answer = input(get_text("msg.purge_confirm")).strip().lower()
        except KeyboardInterrupt:
            print()
            print_info(get_text("msg.purge_aborted"))
            return True
        if answer == "yes":
            result = memory.purge_all()
            summary = f"sessions={result['sessions']}, caches={result['cache_files']}, other={result['other']}"
            print_success(get_text("msg.purge_done", summary=summary))
        else:
            print_info(get_text("msg.purge_aborted"))
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
    elif mode in ("command", "execute"):
        # Command mode — also used by -X (execute) which implies command generation
        num_versions = 1
        if args.command and args.command > 1:
            num_versions = args.command
        elif hasattr(args, 'command_versions') and args.command_versions > 1:
            num_versions = args.command_versions

        if num_versions > 1:
            system_prompt, user_prompt = get_prompt("command", content, language=language, num_versions=num_versions, os_type=os_type)
        else:
            system_prompt, user_prompt = get_prompt("command", content, language=language, os_type=os_type)
    else:
        system_prompt, user_prompt = get_prompt(mode, content, language=language, os_type=os_type)

    # System context: prepend machine facts to system prompt for relevant modes.
    _sys_ctx_modes = {"default", "command", "command_explain", "debug", "refactor"}
    if config.get("system_context_enabled", True) and mode in _sys_ctx_modes:
        try:
            ctx = system_context.get_or_collect(
                ttl_hours=config.get("system_context_ttl_hours", 24)
            )
            ctx_summary = system_context.summary(ctx)
            if ctx_summary:
                system_prompt = f"[System: {ctx_summary}]\n\n{system_prompt}"
        except Exception:
            pass  # best-effort — never block the main flow

    # Conversation memory: carry context from previous invocations (all modes
    # except motivational, and unless --no-memory was passed for this query).
    use_memory = (
        config.get("memory_enabled", True)
        and not getattr(args, "no_memory", False)
        and mode != "motivational"
    )
    # History is already bounded on save (turns + chars). The current user_prompt
    # is the user's actual request (may include a whole file via -e/-d) and must
    # NEVER be truncated/dropped — so we only cap the injected history, never the
    # current prompt.
    history = memory.load_context() if use_memory else []
    if history:
        history = truncate_context(history, max_chars=config.get("memory_max_chars", 6000))

    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": user_prompt})

    # Disable streaming when stdout is not a TTY (e.g. polly "..." | cat).
    # Streaming to a pipe hangs because nothing flushes the buffer on Windows.
    effective_stream = args.stream and sys.stdout.isatty()

    # Response cache: check before calling the API.
    # Only applies when temperature <= cache_max_temperature (creative queries skip).
    use_cache = (
        cache.is_enabled(args)
        and not effective_stream
        and temperature <= config.get("cache_max_temperature", 0.0)
        and mode != "motivational"
    )
    cache_key = None
    if use_cache:
        cache_key = cache._cache_key(model, mode, temperature, system_prompt, user_prompt)
        cached = cache.get(cache_key, ttl_minutes=int(config.get("cache_ttl_minutes", 60)))
        if cached is not None:
            if mode == "command":
                print_code(cached.strip(), language="bash")
            else:
                print_response(cached, format_markdown=not args.no_markdown)
            if use_memory and cached.strip():
                memory.save_turn(content, cached)
                memory.append_history(model, mode, content, cached)
            return

    try:
        if effective_stream:
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
            spinner_ctx = show_spinner("Thinking...") if sys.stdout.isatty() else None
            if spinner_ctx:
                spinner_ctx.__enter__()
            try:
                result = api.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    seed=seed,
                    stream=False
                )
            finally:
                if spinner_ctx:
                    spinner_ctx.__exit__(None, None, None)

            # Special formatting for command mode
            if mode in ("command", "execute"):
                print_code(result.strip(), language="bash")
            else:
                print_response(result, format_markdown=not args.no_markdown)

            # Execute-with-confirmation: -X flag or mode == "execute"
            should_execute = (
                getattr(args, "execute", False)
                and config.get("execute_enabled", True)
                and mode in ("command", "execute")
            )
            if should_execute:
                dry = getattr(args, "dry_run", False)
                # Extract commands: prefer backtick/code-fenced blocks, else non-empty lines
                import re as _re
                code_blocks = _re.findall(r"```(?:\w+)?\n?(.*?)```", result, _re.DOTALL)
                if code_blocks:
                    cmds = [c.strip() for block in code_blocks for c in block.splitlines() if c.strip() and not c.strip().startswith("#")]
                else:
                    cmds = [c.strip() for c in result.strip().splitlines() if c.strip() and not c.strip().startswith(("#", "-", "*", ">", "`"))]
                if len(cmds) > 1:
                    cmd_to_run = executor.pick_command(cmds)
                else:
                    cmd_to_run = cmds[0] if cmds else result.strip()
                if cmd_to_run:
                    executor.execute(cmd_to_run, dry_run=dry)

        # Persist this exchange to memory + history log
        if use_memory and result and result.strip():
            memory.save_turn(content, result)
            memory.append_history(model, mode, content, result)

        # Write to response cache if enabled
        if use_cache and cache_key and result and result.strip():
            cache.put(cache_key, result)

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
        args.delete_profile or
        args.context or
        args.forget or
        args.history or
        args.history_clear or
        args.purge or
        args.update or
        getattr(args, "rescan", False) or
        getattr(args, "show_system", False) or
        bool(getattr(args, "revert", None)) or
        getattr(args, "list_skills", False) or
        getattr(args, "enable_agent", False)
    )

    if config.is_first_run and not is_config_command:
        run_first_time_setup(config)

    # Handle config commands
    if handle_config_commands(args):
        return

    # Apply per-invocation provider overrides before creating the API client
    if getattr(args, "provider", None):
        config.set("provider_type", args.provider)
    if getattr(args, "base_url", None):
        config.set("provider_base_url", args.base_url)
    if getattr(args, "api_key", None):
        config.set("provider_api_key", args.api_key)

    # Initialize API (with direct API flag if specified)
    use_direct_api = getattr(args, 'direct_api', False)
    api = PollinationsAPI(use_direct_api=use_direct_api)

    # Handle --agent / -A
    if getattr(args, "agent", False):
        goal = " ".join(args.prompt) if args.prompt else ""
        if not goal:
            print_error(get_text("msg.no_input"))
            sys.exit(1)
        agent.run(
            api,
            goal,
            dry_run=getattr(args, "dry_run", False),
            no_markdown=getattr(args, "no_markdown", False),
        )
        return

    # Handle --edit FILE "instruction"
    if getattr(args, "edit", None):
        instruction = " ".join(args.prompt) if args.prompt else ""
        if not instruction:
            print_error(get_text("msg.no_input"))
            sys.exit(1)
        dry = getattr(args, "dry_run", False)
        config_edit.edit_file(api, args.edit, instruction, dry_run=dry)
        return

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
    elif args.debug and not args.debug:
        try:
            content = read_file(args.debug)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)

    # Refactor mode with file
    elif args.refactor and not args.refactor:
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
