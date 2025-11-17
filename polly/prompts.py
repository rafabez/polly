"""
Prompt templates for different Polly modes
"""

# OS-specific shell names mapping
OS_SHELL_NAMES = {
    "Linux": "Linux/bash",
    "Darwin": "macOS/bash/zsh",  # Darwin is the system name for macOS
    "Windows": "Windows/PowerShell/CMD"
}

PROMPTS_EN = {
    "explain": {
        "system": "You are a clear and concise technical explainer. Break down complex topics into simple terms.",
        "template": "Explain the following content in a clear and understandable way:\n\n{content}"
    },
    
    "command": {
        "system": "You are a {shell_name} command expert. Provide ONLY the command needed, without any explanation or additional text.",
        "template": "Provide {num_versions} {versions_text} of {shell_name} command to accomplish the following task. Respond with ONLY {the_commands}, without explanations:\n\n{content}"
    },
    
    "command_explain": {
        "system": "You are a {shell_name} instructor. Provide the command and brief explanations of what each part does.",
        "template": "Provide the {shell_name} command to accomplish the following task, followed by a brief explanation of the command and its flags:\n\n{content}"
    },
    
    "debug": {
        "system": "You are a debugging expert. Analyze errors and code issues, then provide clear solutions.",
        "template": "Analyze the following code or error and explain the problem and how to fix it:\n\n{content}"
    },
    
    "refactor": {
        "system": "You are a code quality expert. Suggest improvements while maintaining functionality.",
        "template": "Suggest improvements and refactoring for the following code:\n\n{content}"
    },
    
    "translate": {
        "system": "You are a professional translator. Provide accurate translations while preserving meaning and tone.",
        "template": "Translate the following text to {target_language}:\n\n{content}"
    },
    
    "interactive": {
        "system": "You are Polly, a helpful AI assistant. Be concise, accurate, and friendly. Help with commands, explanations, coding, and general questions.",
        "template": None  # No template needed for interactive mode
    },
    
    "default": {
        "system": "You are Polly, a helpful AI assistant. Provide clear, accurate, and concise responses.",
        "template": "{content}"
    },
    
    "motivational": {
        "system": "You are a generator of comic and ironic demotivational phrases. Be creative, funny, and sarcastic.",
        "template": "Create a random comic, funny, and ironic demotivational phrase and tell me only the phrase, without prefix or suggestions afterwards"
    }
}

PROMPTS_PT = {
    "explain": {
        "system": "Você é um explicador técnico claro e conciso. Divida tópicos complexos em termos simples. Responda sempre em português.",
        "template": "Explique o seguinte conteúdo de forma clara e compreensível:\n\n{content}"
    },
    
    "command": {
        "system": "Você é um especialista em comandos {shell_name}. Forneça APENAS o comando necessário, sem explicações ou texto adicional.",
        "template": "Forneça {num_versions} {versions_text} de comando {shell_name} para realizar a seguinte tarefa. Responda APENAS com {os_comandos}, sem explicações:\n\n{content}"
    },
    
    "command_explain": {
        "system": "Você é um instrutor de {shell_name}. Forneça o comando e explicações breves sobre o que cada parte faz. Responda sempre em português.",
        "template": "Forneça o comando {shell_name} para realizar a seguinte tarefa, seguido de uma breve explicação do comando e suas flags:\n\n{content}"
    },
    
    "debug": {
        "system": "Você é um especialista em debugging. Analise erros e problemas de código, então forneça soluções claras. Responda sempre em português.",
        "template": "Analise o seguinte código ou erro e explique o problema e como corrigi-lo:\n\n{content}"
    },
    
    "refactor": {
        "system": "Você é um especialista em qualidade de código. Sugira melhorias mantendo a funcionalidade. Responda sempre em português.",
        "template": "Sugira melhorias e refatoração para o seguinte código:\n\n{content}"
    },
    
    "translate": {
        "system": "Você é um tradutor profissional. Forneça traduções precisas preservando significado e tom.",
        "template": "Traduza o seguinte texto para {target_language}:\n\n{content}"
    },
    
    "interactive": {
        "system": "Você é Polly, um assistente de IA útil. Seja conciso, preciso e amigável. Ajude com comandos, explicações, programação e perguntas gerais. Responda sempre em português.",
        "template": None
    },
    
    "default": {
        "system": "Você é Polly, um assistente de IA útil. Forneça respostas claras, precisas e concisas. Responda sempre em português.",
        "template": "{content}"
    },
    
    "motivational": {
        "system": "Você é um gerador de frases desmotivacionais cômicas e irônicas. Seja criativo, engraçado e sarcástico.",
        "template": "Crie uma frase desmotivacional aleatória cômica e engraçada e irônica e me diga apenas a frase, sem prefixo nem sugestões depois"
    }
}

# Map of available languages
AVAILABLE_LANGUAGES = {
    "en": PROMPTS_EN,
    "pt": PROMPTS_PT,
    "pt-br": PROMPTS_PT,
    "portuguese": PROMPTS_PT,
    "english": PROMPTS_EN
}


def get_prompt(mode: str, content: str = "", language: str = "pt", os_type: str = "linux", **kwargs) -> tuple:
    """
    Get system prompt and formatted user prompt for a given mode

    Args:
        mode: The prompt mode (explain, command, debug, etc.)
        content: The user's content/question
        language: Language for prompts (pt, en, pt-br, portuguese, english)
        os_type: Operating system type (linux, darwin, macos, windows) - default is linux
        **kwargs: Additional template variables (e.g., num_versions for command mode)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Get prompts for the specified language, default to Portuguese
    lang_key = language.lower()
    prompts = AVAILABLE_LANGUAGES.get(lang_key, PROMPTS_PT)

    # Normalize OS type to match OS_SHELL_NAMES keys
    # Convert lowercase to capitalized, and macos to Darwin
    os_normalized = os_type.lower()
    if os_normalized == "macos":
        os_normalized = "darwin"
    os_key = os_normalized.capitalize()

    # Get shell name based on OS type
    shell_name = OS_SHELL_NAMES.get(os_key, "Linux/bash")
    kwargs["shell_name"] = shell_name

    prompt_config = prompts.get(mode, prompts["default"])

    # Format system prompt with shell_name if it contains the placeholder
    system_prompt = prompt_config["system"]
    if "{shell_name}" in system_prompt:
        system_prompt = system_prompt.format(shell_name=shell_name)

    # Handle command mode with multiple versions
    if mode == "command":
        num = kwargs.get("num_versions", 1)
        kwargs["num_versions"] = num
        if lang_key in ["pt", "pt-br", "portuguese"]:
            kwargs["versions_text"] = "versão" if num == 1 else "versões diferentes"
            kwargs["os_comandos"] = "o comando" if num == 1 else "os comandos (um por linha)"
        else:
            kwargs["versions_text"] = "version" if num == 1 else "different versions"
            kwargs["the_commands"] = "the command" if num == 1 else "the commands (one per line)"

    if prompt_config["template"]:
        user_prompt = prompt_config["template"].format(content=content, **kwargs)
    else:
        user_prompt = content

    return system_prompt, user_prompt


def get_available_modes() -> dict:
    """Get all available prompt modes with descriptions"""
    return {
        "explain": "Explain content clearly and concisely",
        "command": "Get OS-specific command (command only)",
        "command_explain": "Get OS-specific command with explanations",
        "debug": "Debug code or analyze errors",
        "refactor": "Get code improvement suggestions",
        "translate": "Translate text to another language",
        "interactive": "Interactive chat mode",
        "motivational": "Get a demotivational phrase (funny and ironic)",
        "default": "General purpose assistant"
    }
