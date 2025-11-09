# 🌸 Polly - AI Assistant for Linux Terminal

> 🇧🇷 **[Leia em Português](README.pt-BR.md)** | 🇺🇸 English

**Polly** is a powerful command-line AI assistant for Linux, powered by [Pollinations.ai](https://pollinations.ai). Get instant answers, command suggestions, code explanations, and more—all from your terminal.

## ✨ Features

- 🚀 **Fast & Free** - Powered by Pollinations.ai's free API
- 🎯 **Multiple Modes** - Explain, command generation, debugging, refactoring, and more
- 🤖 **Multiple AI Models** - Choose from Gemini, OpenAI, DeepSeek, Qwen Coder, and more
- 💬 **Interactive Chat** - Conversational mode with context awareness
- 🎨 **Beautiful Output** - Markdown rendering and syntax highlighting
- ⚡ **Streaming Support** - Real-time responses
- 🔧 **Configurable** - Customize default model, temperature, and more
- 📝 **Pipe Support** - Works with stdin/stdout for scripting

## 📦 Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/rafabez/polly.git
cd polly

# Install in development mode
pip install -e .

# Or install directly
pip install .
```

### System-wide Installation

```bash
# Install for current user
pip install --user .

# Or install system-wide (requires sudo)
sudo pip install .
```

## 🚀 Quick Start

### Basic Usage

```bash
# Ask a question
polly "What is recursion?"

# Get a Linux command
polly -c "list all files modified today"

# Get 3 different command versions
polly -c3 "compress directory"

# Explain a file
polly -e script.sh

# Debug a file
polly -d api.py

# Debug with pipe
cat error.log | polly -d

# Refactor code
polly -r code.py

# Translate file
polly -tf english documento.txt

# Get a funny demotivational phrase
polly -x

# Interactive mode
polly -i
```

### Available Modes

| Flag | Mode | Description |
|------|------|-------------|
| `-e, --explain` | Explain | Explain file content or piped input |
| `-c, --command` | Command | Get Linux/bash command (no explanation) |
| `-ce, --command-explain` | Command + Explain | Get command with explanations |
| `-d, --debug` | Debug | Analyze and debug code/errors |
| `-r, --refactor` | Refactor | Get code improvement suggestions |
| `-t, --translate` | Translate | Translate text to another language |
| `-i, --interactive` | Interactive | Start chat mode with context |

### Model Selection

```bash
# Use specific model
polly --model gemini "Explain quantum computing"

# List available models
polly --list-models

# Set default model
polly --set-default-model openai-large
```

### Available Models

- **gemini** - Gemini 2.5 Flash Lite (default, best context window)
- **openai** - OpenAI GPT-5 Nano (fast)
- **openai-large** - OpenAI GPT-4.1 (most capable)
- **deepseek** - DeepSeek V3.1 (advanced reasoning)
- **qwen-coder** - Qwen 2.5 Coder 32B (specialized for code)
- **mistral** - Mistral Small 3.2 24B (balanced)
- **gemini-search** - Gemini with Google Search

### Advanced Options

```bash
# Control creativity (0.0-3.0)
polly --temperature 1.5 "Write a creative poem"

# Enable streaming
polly -s "Tell me a long story"

# Save output to file
polly -o response.txt "Explain Docker"

# JSON output
polly --json "What is Linux?"

# Pipe from other commands
cat script.py | polly -d "Find bugs in this code"
echo "Hello world" | polly -t "Portuguese"
```

## 🎯 Usage Examples

### Command Generation

```bash
# Get just the command
$ polly -c "find all Python files larger than 1MB"
find . -name "*.py" -size +1M

# Get command with explanation
$ polly -ce "compress all logs older than 30 days"
find /var/log -name "*.log" -mtime +30 -exec gzip {} \;

Explanation:
- find /var/log: Search in log directory
- -name "*.log": Match log files
- -mtime +30: Modified more than 30 days ago
- -exec gzip {} \;: Compress each file found
```

### Code Explanation

```bash
# Explain a script
$ polly -e deploy.sh

# Explain piped code
$ cat complex_function.py | polly -e
```

### Debugging

```bash
# Debug error logs
$ cat error.log | polly -d

# Debug code directly
$ polly -d "$(cat buggy_script.sh)"
```

### Interactive Mode

```bash
$ polly -i
Interactive mode - Type 'exit' or 'quit' to end, 'clear' to reset context

[Model: gemini, Temperature: 0.7]

You: How do I list running processes?
Polly: You can use the `ps` command...

You: What about filtering by name?
Polly: You can use `ps aux | grep process_name`...

You: exit
Info: Goodbye!
```

### Translation

```bash
$ polly -t Portuguese "Hello, how are you?"
Olá, como você está?

$ echo "Good morning" | polly -t Spanish
Buenos días
```

## ⚙️ Configuration

Polly stores configuration in `~/.config/polly/config.yaml`

```bash
# View current configuration
polly --config

# Set default model
polly --set-default-model gemini

# Set default language for prompts
polly --set-language pt

# Reset to defaults
polly --reset-config

# Check version
polly -v
```

### Configuration File Example

```yaml
default_model: gemini
temperature: 0.7
max_tokens: 2000
stream: false
referrer: deepentest.com
```

## 🔧 Development

### Project Structure

```
polly/
├── polly/
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # Main entry point
│   ├── api.py            # Pollinations API client
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── prompts.py        # Prompt templates
│   └── utils.py          # Utility functions
├── tests/                # Test suite
├── setup.py              # Setup script
├── pyproject.toml        # Modern Python packaging
├── requirements.txt      # Dependencies
├── README.md             # This file
└── LICENSE               # MIT License
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 📝 Requirements

- Python 3.8 or higher
- Linux operating system
- Internet connection (for API calls)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by [Pollinations.ai](https://pollinations.ai) - Free AI API
- Built for the Linux community
- Special thanks to the BigLinux team

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/rafabez/polly/issues) page to report bugs or request features.

## 📚 Additional Resources

- [Pollinations.ai API Documentation](https://github.com/pollinations/pollinations/blob/main/APIDOCS.md)
- [Available Models](https://text.pollinations.ai/models)

---

Made with ❤️ for the Linux community
