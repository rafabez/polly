"""
Internationalization (i18n) module for Polly
Supports English and Portuguese
"""

from typing import Dict

# Translation dictionaries
TRANSLATIONS = {
    "en": {
        # Help text
        "help.title": "Polly - Cross-Platform AI Terminal Assistant",
        "help.powered_by": "Powered by Pollinations.ai",
        "help.usage": "USAGE",
        "help.modes": "MODES",
        "help.parameters": "PARAMETERS",
        "help.output": "OUTPUT",
        "help.configuration": "CONFIGURATION",
        "help.information": "INFORMATION",
        "help.examples": "EXAMPLES",
        "help.tips": "TIPS",

        # Mode descriptions
        "mode.explain": "Explain file content",
        "mode.command": "Generate bash command (use -c3 for 3 versions)",
        "mode.command_explain": "Generate command with explanations",
        "mode.debug": "Analyze errors and debug code",
        "mode.refactor": "Suggest code improvements",
        "mode.translate": "Translate text to language",
        "mode.translate_file": "Translate file to language",
        "mode.interactive": "Interactive chat mode",
        "mode.motivational": "Funny demotivational phrase 😄",

        # Parameters
        "param.model": "Select AI model",
        "param.temperature": "Creativity 0.0-3.0 (default: 0.7)",
        "param.stream": "Enable streaming response",
        "param.language": "Language for prompts (default: pt - Portuguese)",
        "param.direct_api": "Use direct Pollinations API (bypass proxy backend)",

        # Output
        "output.file": "Save response to file",
        "output.pdf": "Save response as PDF file",
        "output.json": "Output in JSON format",
        "output.no_markdown": "Disable markdown formatting",

        # Configuration
        "config.view": "View/open configuration file",
        "config.set_model": "Set default model",
        "config.set_language": "Set default prompt language (en/pt)",
        "config.reset": "Reset to default configuration",

        # Information
        "info.list_models": "List available AI models",
        "info.list_modes": "List available prompt modes",
        "info.version": "Show version number",
        "info.help": "Show this help message",

        # Tips
        "tip.pipe": "To explain content via pipe, use:",
        "tip.file_only": "The -e flag is only for files",
        "tip.model_down": "If a model is down, try another",
        "tip.pdf_support": "PDF support (read and write)",

        # Examples
        "example.basic": "Basic question",
        "example.explain": "Explain code",
        "example.command": "Generate command",
        "example.debug": "Debug error",
        "example.model": "Use specific model",

        # Messages
        "msg.available_models": "Available AI Models:",
        "msg.cached_models": "Note: Using cached models - API unavailable",
        "msg.available_modes": "Available Modes:",
        "msg.model_set": "Default model set to:",
        "msg.config_failed": "Failed to save configuration",
        "msg.config_reset": "Configuration reset to defaults",
        "msg.language_set": "Default language set to:",
        "msg.config_file": "Configuration file:",
        "msg.current_config": "Current configuration:",
        "msg.no_config": "No configuration file found. Creating default at:",
        "msg.interactive_help": "Interactive mode - Type 'exit' or 'quit' to end, 'clear' to reset context",
        "msg.goodbye": "Goodbye!",
        "msg.context_cleared": "Context cleared",
        "msg.you": "You:",
        "msg.polly": "Polly:",
        "msg.response_saved": "Response saved to:",
        "msg.failed_save": "Failed to save output:",
        "msg.failed_pdf": "Failed to save PDF",
        "msg.no_input": "No input provided",
        "msg.thinking": "Thinking...",

        # Error messages (from api.py)
        "error.timeout": "Timeout: Model '{model}' took too long to respond.",
        "error.timeout_tip": "Try: polly --list-models to see other available models",
        "error.service_down": "Service temporarily unavailable.",
        "error.service_tip": "Try another model: polly --list-models",
        "error.rate_limit": "Rate limit exceeded.",
        "error.rate_limit_tip": "Wait a few seconds and try again.",
        "error.server_error": "Server error (model: {model}).",
        "error.server_tip": "Try another model: polly --list-models",
        "error.server_suggestion": "Suggestion: polly --model mistral <your question>",
        "error.http_error": "HTTP {status_code} error.",
        "error.http_tip": "Try another model: polly --list-models",
        "error.connection": "Connection error.",
        "error.connection_tip": "Check your internet connection.",
        "error.connection_direct": "Or try direct API: polly --direct-api <your question>",
        "error.request": "Request error: {error_msg}",
        "error.request_tip": "Try another model: polly --list-models",
        "error.invalid_response": "Invalid API response.",
        "error.model_unavailable": "Model '{model}' may be temporarily unavailable.",
        "error.model_suggestion": "Try: polly --model mistral <your question>",

        # Utility messages
        "label.error": "Error:",
        "label.info": "Info:",
        "label.warning": "Warning:",
        "label.success": "✓",

        # PDF messages
        "pdf.pypdf_missing": "pypdf not installed. Install with: pip install pypdf",
        "pdf.no_text": "No text could be extracted from PDF",
        "pdf.read_error": "Error reading PDF: {e}",
        "pdf.reportlab_missing": "reportlab not installed. Install with: pip install reportlab",
        "pdf.saved": "PDF saved to: {output_path}",
        "pdf.write_error": "Error writing PDF: {e}",

        # File errors
        "file.not_found": "File not found: {filepath}",
        "file.permission": "Permission denied: {filepath}",
        "file.encoding": "File encoding error. PDF files are supported with --explain, --debug, etc.",
        "file.read_error": "Error reading file: {str}",
        "file.interrupted": "Interrupted by user",

        # Config errors
        "config.load_error": "Could not load config file: {e}",
    },

    "pt": {
        # Help text
        "help.title": "Polly - Assistente de IA Cross-Platform para Terminal",
        "help.powered_by": "Powered by Pollinations.ai",
        "help.usage": "USO",
        "help.modes": "MODOS",
        "help.parameters": "PARÂMETROS",
        "help.output": "SAÍDA",
        "help.configuration": "CONFIGURAÇÃO",
        "help.information": "INFORMAÇÃO",
        "help.examples": "EXEMPLOS",
        "help.tips": "DICAS",

        # Mode descriptions
        "mode.explain": "Explica conteúdo de arquivo",
        "mode.command": "Gera comando bash (use -c3 para 3 versões)",
        "mode.command_explain": "Gera comando com explicações",
        "mode.debug": "Analisa erros e debugga código",
        "mode.refactor": "Sugere melhorias de código",
        "mode.translate": "Traduz texto para idioma",
        "mode.translate_file": "Traduz arquivo para idioma",
        "mode.interactive": "Modo chat interativo",
        "mode.motivational": "Frase desmotivacional engraçada 😄",

        # Parameters
        "param.model": "Seleciona modelo de IA",
        "param.temperature": "Criatividade 0.0-3.0 (padrão: 0.7)",
        "param.stream": "Habilita resposta em streaming",
        "param.language": "Idioma dos prompts (padrão: pt - Português)",
        "param.direct_api": "Usa API direta Pollinations (sem proxy backend)",

        # Output
        "output.file": "Salva resposta em arquivo",
        "output.pdf": "Salva resposta como arquivo PDF",
        "output.json": "Saída em formato JSON",
        "output.no_markdown": "Desabilita formatação markdown",

        # Configuration
        "config.view": "Ver/abrir arquivo de configuração",
        "config.set_model": "Define modelo padrão",
        "config.set_language": "Define idioma padrão dos prompts (en/pt)",
        "config.reset": "Reseta para configuração padrão",

        # Information
        "info.list_models": "Lista modelos de IA disponíveis",
        "info.list_modes": "Lista modos de prompt disponíveis",
        "info.version": "Mostra número da versão",
        "info.help": "Mostra esta mensagem de ajuda",

        # Tips
        "tip.pipe": "Para explicar conteúdo via pipe, use:",
        "tip.file_only": "O flag -e é apenas para arquivos",
        "tip.model_down": "Se um modelo estiver fora do ar, tente outro",
        "tip.pdf_support": "Suporte a PDF (leitura e escrita)",

        # Examples
        "example.basic": "Pergunta básica",
        "example.explain": "Explicar código",
        "example.command": "Gerar comando",
        "example.debug": "Debugar erro",
        "example.model": "Usar modelo específico",

        # Messages
        "msg.available_models": "Modelos de IA Disponíveis:",
        "msg.cached_models": "Nota: Usando modelos em cache - API indisponível",
        "msg.available_modes": "Modos Disponíveis:",
        "msg.model_set": "Modelo padrão definido para:",
        "msg.config_failed": "Falha ao salvar configuração",
        "msg.config_reset": "Configuração resetada para padrões",
        "msg.language_set": "Idioma padrão definido para:",
        "msg.config_file": "Arquivo de configuração:",
        "msg.current_config": "Configuração atual:",
        "msg.no_config": "Arquivo de configuração não encontrado. Criando padrão em:",
        "msg.interactive_help": "Modo interativo - Digite 'exit' ou 'quit' para sair, 'clear' para limpar contexto",
        "msg.goodbye": "Até logo!",
        "msg.context_cleared": "Contexto limpo",
        "msg.you": "Você:",
        "msg.polly": "Polly:",
        "msg.response_saved": "Resposta salva em:",
        "msg.failed_save": "Falha ao salvar saída:",
        "msg.failed_pdf": "Falha ao salvar PDF",
        "msg.no_input": "Nenhuma entrada fornecida",
        "msg.thinking": "Pensando...",

        # Error messages
        "error.timeout": "Timeout: O modelo '{model}' demorou muito para responder.",
        "error.timeout_tip": "Tente: polly --list-models para ver outros modelos disponíveis",
        "error.service_down": "Serviço temporariamente indisponível.",
        "error.service_tip": "Tente outro modelo: polly --list-models",
        "error.rate_limit": "Limite de requisições atingido.",
        "error.rate_limit_tip": "Aguarde alguns segundos e tente novamente.",
        "error.server_error": "Erro no servidor (modelo: {model}).",
        "error.server_tip": "Tente outro modelo: polly --list-models",
        "error.server_suggestion": "Sugestão: polly --model mistral <sua pergunta>",
        "error.http_error": "Erro HTTP {status_code}.",
        "error.http_tip": "Tente outro modelo: polly --list-models",
        "error.connection": "Erro de conexão.",
        "error.connection_tip": "Verifique sua conexão com a internet.",
        "error.connection_direct": "Ou tente com API direta: polly --direct-api <sua pergunta>",
        "error.request": "Erro na requisição: {error_msg}",
        "error.request_tip": "Tente outro modelo: polly --list-models",
        "error.invalid_response": "Resposta inválida da API.",
        "error.model_unavailable": "Modelo '{model}' pode estar temporariamente indisponível.",
        "error.model_suggestion": "Tente: polly --model mistral <sua pergunta>",

        # Utility messages
        "label.error": "Erro:",
        "label.info": "Info:",
        "label.warning": "Aviso:",
        "label.success": "✓",

        # PDF messages
        "pdf.pypdf_missing": "pypdf não instalado. Instale com: pip install pypdf",
        "pdf.no_text": "Nenhum texto pôde ser extraído do PDF",
        "pdf.read_error": "Erro ao ler PDF: {e}",
        "pdf.reportlab_missing": "reportlab não instalado. Instale com: pip install reportlab",
        "pdf.saved": "PDF salvo em: {output_path}",
        "pdf.write_error": "Erro ao escrever PDF: {e}",

        # File errors
        "file.not_found": "Arquivo não encontrado: {filepath}",
        "file.permission": "Permissão negada: {filepath}",
        "file.encoding": "Erro de codificação do arquivo. Arquivos PDF são suportados com --explain, --debug, etc.",
        "file.read_error": "Erro ao ler arquivo: {str}",
        "file.interrupted": "Interrompido pelo usuário",

        # Config errors
        "config.load_error": "Não foi possível carregar arquivo de configuração: {e}",
    }
}


def get_text(key: str, lang: str = None, **kwargs) -> str:
    """
    Get translated text for a given key.

    Args:
        key: Translation key (e.g., "error.timeout")
        lang: Language code ('en' or 'pt'). If None, uses config language.
        **kwargs: Format parameters for the translation string

    Returns:
        Translated and formatted string
    """
    # Import here to avoid circular dependency
    from .config import get_config

    # Determine language
    if lang is None:
        config = get_config()
        lang = config.get("language", "pt")

    # Normalize language code
    if lang in ["pt-br", "portuguese"]:
        lang = "pt"
    elif lang in ["english"]:
        lang = "en"

    # Default to English if language not supported
    if lang not in TRANSLATIONS:
        lang = "en"

    # Get translation
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))

    # Format with parameters
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # If format fails, return unformatted text

    return text


def t(key: str, **kwargs) -> str:
    """Shorthand for get_text()"""
    return get_text(key, **kwargs)
