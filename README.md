<div align="center">

![Polly Banner](images/01_parrot_wallpaper.png)

# 🦜 Polly - Your Free AI Terminal Companion

### The Cross-Platform AI Assistant That Just Works. Everywhere.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](https://github.com/rafabez/polly)
[![Powered by Pollinations.ai](https://img.shields.io/badge/Powered%20by-Pollinations.ai-green)](https://pollinations.ai)
[![Free API](https://img.shields.io/badge/API-100%25%20Free-brightgreen)](https://pollinations.ai)

**[English](#english)** | **[Português](README.pt-BR.md)**

</div>

---

## 🚀 Why Polly?

**Polly** is your intelligent terminal assistant that breaks all barriers:

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🌍 **True Cross-Platform** | Native support for **Linux**, **macOS**, AND **Windows** - with OS-specific command generation! |
| 🔓 **Zero Setup Required** | No API keys, no accounts, no credit cards. Just install and go! |
| 🔒 **Privacy First** | Powered by [Pollinations.ai](https://pollinations.ai) - no tracking, no data collection |
| 💰 **100% Free Forever** | Unlimited queries, unlimited models, unlimited awesome |
| ⚡ **Lightning Fast** | Real-time streaming responses, multiple AI models to choose from |
| 🎨 **Beautiful Output** | Markdown rendering, syntax highlighting, and clean terminal UI |
| 🤖 **8 Powerful Modes** | From command generation to debugging, translation to refactoring |
| 🌐 **Multilingual** | Built-in English & Portuguese support, translate to any language |
| 📄 **PDF Magic** | Read PDF inputs AND generate PDF outputs |
| 💬 **Interactive Chat** | Context-aware conversations with your AI assistant |

---

## 📦 Installation

### Quick Install with pipx (Recommended)

**pipx** ensures Polly runs in its own isolated environment without conflicts:

```bash
# Install pipx (if you don't have it)
# Linux (Debian/Ubuntu)
sudo apt install pipx

# Linux (Arch/Manjaro)
sudo pacman -S python-pipx

# macOS
brew install pipx

# Windows (PowerShell as Administrator)
python -m pip install --user pipx
python -m pipx ensurepath

# Configure pipx path (first time only)
pipx ensurepath

# Restart your terminal, then install Polly
pipx install git+https://github.com/rafabez/polly.git

# Test it out!
polly --version
polly Hello, Polly!
```

### Alternative: Install with pip

```bash
# Using pip (simpler, but may conflict with other packages)
pip install git+https://github.com/rafabez/polly.git

# Or clone and install locally
git clone https://github.com/rafabez/polly.git
cd polly
pip install .
```

### For Developers

```bash
# Clone and install in editable mode
git clone https://github.com/rafabez/polly.git
cd polly
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

---

## 🎯 Quick Start

### Basic Queries

```bash
# Ask anything
polly What is machine learning?

# Get help with terminal tasks
polly How do I check disk space?

# Code explanations
polly Explain what Docker does
```

### Cross-Platform Command Generation

Polly **automatically detects your OS** and generates appropriate commands:

```bash
# On Linux - generates bash/Linux commands
polly -c find large files
# Output: find . -type f -size +100M

# On macOS - generates macOS/zsh commands
polly -c show hidden files
# Output: defaults write com.apple.finder AppleShowAllFiles YES

# On Windows - generates PowerShell/CMD commands
polly -c list running processes
# Output: Get-Process | Where-Object {$_.Responding -eq $true}
```

**Get multiple command versions:**

```bash
# Get 3 different ways to accomplish the same task
polly -c --command-versions 3 "compress a directory"

# Or use the shorthand
polly -c3 search for text in files
```

### File Operations

```bash
# Explain a script
polly -e deploy.sh

# Debug problematic code
polly -d buggy_script.py

# Get refactoring suggestions
polly -r legacy_code.js

# Read and explain PDFs
polly -e documentation.pdf

# Translate a file
polly -tf spanish readme.txt
```

### Pipe Like a Pro

```bash
# Debug error logs
cat error.log | polly -d

# Translate piped content
echo "Hello world" | polly -t portuguese

# Analyze code from stdin
git diff | polly -e
```

---

## 🎪 All Modes Explained

### 1️⃣ Explain Mode (`-e, --explain`)

Understand files, code, or concepts in plain language.

```bash
# Explain a shell script
polly -e setup.sh

# Explain a Python module
polly -e src/api_client.py

# Explain a PDF document
polly -e technical_whitepaper.pdf

# Explain piped content
cat complex_algorithm.py | polly -e
```

### 2️⃣ Command Mode (`-c, --command`)

Generate OS-specific commands instantly.

```bash
# Single command
polly -c find Python files modified today

# Multiple versions (3 different approaches)
polly -c3 kill process by name

# With explanation
polly -ce backup directory to remote server
```

**Platform Examples:**

| Platform | Query | Output |
|----------|-------|--------|
| **Linux** | `polly -c monitor CPU usage` | `top -bn1 \| grep "Cpu(s)"` |
| **macOS** | `polly -c monitor CPU usage` | `top -l 1 \| grep "CPU usage"` |
| **Windows** | `polly -c monitor CPU usage` | `Get-Counter '\Processor(_Total)\% Processor Time'` |

### 3️⃣ Debug Mode (`-d, --debug`)

Analyze errors, find bugs, get solutions.

```bash
# Debug a file
polly -d failing_test.py

# Debug error logs
polly -d error_trace.log

# Debug piped errors
python script.py 2>&1 | polly -d

# Debug from clipboard
polly -d TypeError: cannot concatenate 'str' and 'int'
```

### 4️⃣ Refactor Mode (`-r, --refactor`)

Improve code quality and structure.

```bash
# Get refactoring suggestions
polly -r messy_code.js

# Refactor with pipe
cat old_script.sh | polly -r

# Specific improvement request
polly -r legacy.py "Make this code more Pythonic"
```

### 5️⃣ Translate Mode (`-t, --translate`)

Translate text or entire files to any language.

```bash
# Translate text
polly -t spanish Good morning, how are you?

# Translate file
polly -tf french README.md

# Translate piped content
echo "Hello world" | polly -t japanese

# Save translation
polly -tf german docs.txt -o docs_de.txt
```

### 6️⃣ Interactive Mode (`-i, --interactive`)

Have a conversation with context awareness.

```bash
polly -i
```

```
Interactive mode - Type 'exit' or 'quit' to end, 'clear' to reset context

[Model: openai-large, Temperature: 0.7]

You: How do I list files in Linux?
Polly: You can use the `ls` command. For detailed info, use `ls -la`

You: What about sorting by date?
Polly: Add the -t flag: `ls -lat`. This sorts by modification time.

You: exit
Info: Goodbye!
```

### 7️⃣ Motivational Mode (`-x, --motivational`)

Get hilariously ironic demotivational quotes.

```bash
polly -x
# "Success is just failure that hasn't happened yet."

polly -x
# "Every expert was once a beginner who refused to give up... maybe you should."
```

### 8️⃣ Default Mode (No Flags)

General-purpose AI assistant.

```bash
# Ask anything
polly Explain quantum entanglement

# Get advice
polly Best practices for API design

# Problem solving
polly My server is running slow, what should I check?
```

---

## ⚙️ Configuration

### View Configuration

```bash
# Show current config
polly --config

# Output:
# Config file: /home/user/.config/polly/config.yaml
#
# Current configuration:
#   default_model: openai-large
#   temperature: 0.7
#   stream: false
#   language: pt
#   use_backend: true
```

### Configuration Options

Polly stores settings in `~/.config/polly/config.yaml`:

```yaml
# Default AI model
default_model: openai-large

# Creativity level (0.0 = focused, 3.0 = creative)
temperature: 0.7

# Enable streaming responses
stream: false

# Default prompt language (en, pt, pt-br)
language: pt

# Use proxy backend (recommended)
use_backend: true

# Referrer for API requests
referrer: interzonesec.com
```

### Model Selection

Polly supports multiple AI models with different strengths:

```bash
# List available models
polly --list-models

# Use a specific model
polly --model gemini Fast query
polly --model openai-large "Complex reasoning"
polly --model qwen-coder "Code generation"

# Set default model
polly --set-default-model openai-large
```

**Available Models:**

| Model | Best For | Notes |
|-------|----------|-------|
| **openai-large** | General tasks, complex reasoning | Default - most capable |
| **mistral** | Balanced performance | Fast and reliable |
| **deepseek** | Advanced reasoning | Great for complex problems |
| **qwen-coder** | Code generation & analysis | Specialized for developers |
| **openai** | Speed | Fast but limited (temp=1.0 only) |
| **gemini** | General tasks | Fast (may be unstable) |
| **gemini-search** | Research queries | Gemini + Google Search |

### Language Settings

```bash
# Set prompt language to English
polly --set-language en

# Set to Portuguese
polly --set-language pt

# Use language for single query
polly -l en Generate a report
```

### Temperature Control

Control creativity vs. precision:

```bash
# Precise, focused responses (good for commands/debugging)
polly --temperature 0.3 -c "backup database"

# Balanced (default)
polly --temperature 0.7 "Explain Docker"

# Creative, varied responses (good for writing/brainstorming)
polly --temperature 1.5 "Write a creative function name"
```

### Reset Configuration

```bash
# Reset to defaults
polly --reset-config
```

---

## 💎 Advanced Features

### Streaming Responses

Get responses in real-time:

```bash
polly -s Write a long explanation of neural networks
```

### Output Options

```bash
# Save to text file
polly Explain Git -o git_guide.txt

# Save as PDF
polly Python best practices --pdf python_guide.pdf

# JSON output (for scripting)
polly --json What is DevOps?
```

### PDF Operations

```bash
# Read and explain PDF
polly -e technical_manual.pdf

# Debug code from PDF
polly -d code_review.pdf

# Generate PDF output
polly Docker tutorial --pdf docker_tutorial.pdf

# Combined: Read PDF and output PDF
polly -e input.pdf --pdf output_summary.pdf
```

### Direct API Mode

Bypass proxy backend and use Pollinations.ai directly:

```bash
polly --direct-api "Your query here"
```

### Pipeline Integration

Polly works seamlessly in Unix pipelines:

```bash
# Debug test failures
pytest 2>&1 | polly -d

# Translate Git commits
git log --oneline -5 | polly -t spanish

# Explain complex commands
history | tail -1 | polly -e

# Refactor code from version control
git show HEAD:old_file.py | polly -r
```

---

## 🖥️ Cross-Platform Examples

### Linux

```bash
# System commands
polly -c show disk usage by directory
polly -c find processes using port 8080

# Package management
polly -c update all packages Ubuntu
polly -c install nginx Arch Linux

# File operations
polly -c find duplicate files
polly -c batch rename files
```

### macOS

```bash
# macOS specific
polly -c show all files in Finder
polly -c flush DNS cache

# Homebrew
polly -c install Python with Homebrew
polly -c update all brew packages

# System info
polly -c check battery health
polly -c show connected wifi networks
```

### Windows

```bash
# PowerShell commands
polly -c list installed programs
polly -c check network connections

# File operations
polly -c find files larger than 1GB
polly -c copy folder with progress

# System management
polly -c restart Windows service
polly -c check Windows version
```

---

## 📊 Web Dashboard (Optional)

Polly includes an optional web dashboard for visual interaction and history tracking:

### Features
- Visual interface for all Polly features
- Query history and search
- Model comparison
- Syntax highlighting for code
- Export conversations

### Access
The dashboard is a separate component. Check the `dashboard/` directory for setup instructions.

> **Note:** The dashboard is optional. The CLI is fully functional without it!

---

## 🎓 Pro Tips

### 1. Combine Modes

```bash
# Get command and save to file
polly -c backup postgres database -o backup_script.sh

# Explain and save as PDF
polly -e complex_script.sh --pdf explanation.pdf

# Interactive mode with different model
polly -i --model deepseek
```

### 2. Use Aliases

Add to your `.bashrc`, `.zshrc`, or PowerShell profile:

```bash
# Quick debug
alias pdebug='polly -d'

# Quick explain
alias pexplain='polly -e'

# Quick command
alias pcmd='polly -c'

# Interactive with favorite model
alias pask='polly -i --model openai-large'
```

### 3. Script Integration

```bash
#!/bin/bash
# auto_debug.sh - Automatically debug failing scripts

# Run command and capture errors
output=$(./my_script.sh 2>&1)
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "Script failed! Asking Polly for help..."
    echo "$output" | polly -d
fi
```

### 4. Git Hooks

```bash
# .git/hooks/commit-msg - Auto-improve commit messages
#!/bin/bash
commit_msg=$(cat "$1")
improved=$(echo "$commit_msg" | polly Improve this commit message)
echo "$improved" > "$1"
```

### 5. Workflow Examples

```bash
# Full code review workflow
git diff | polly -e > review.txt
git diff | polly -d >> review.txt
git diff | polly -r >> review.txt

# Learning new commands
polly -ce extract tar.gz file | tee cheatsheet.txt

# Multi-language documentation
polly -e README.md -o README_explained.txt
polly -tf spanish README.md -o README_es.md
polly -tf french README.md -o README_fr.md
```

---

## 🤝 Contributing

We love contributions! Here's how you can help:

### Types of Contributions

- 🐛 **Bug Reports** - Found an issue? Let us know!
- ✨ **Feature Requests** - Have an idea? We want to hear it!
- 📝 **Documentation** - Improve guides, add examples
- 🌍 **Translations** - Add support for more languages
- 🔧 **Code** - Fix bugs, add features, improve performance

### Getting Started

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/polly.git
   cd polly
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   ```bash
   # Install in development mode
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e .

   # Make your changes and test
   polly --version
   ```

4. **Run tests** (if available)
   ```bash
   pytest tests/
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Go to GitHub and create a PR
   - Describe your changes
   - Link any related issues

### Code Style

- Follow PEP 8 for Python code
- Add docstrings to functions
- Keep functions focused and modular
- Test cross-platform compatibility when possible

### Adding New Features

**Want to add a new mode?**

1. Add prompt template to `polly/prompts.py`
2. Add CLI argument to `polly/cli.py`
3. Add mode detection to `get_mode_from_args()`
4. Update help text in `polly/help_formatter.py`
5. Add documentation to README
6. Test on multiple platforms if possible

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Copyright (c) 2025 Interzone (Rafael Beznos)

Permission is granted to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software. See LICENSE for details.
```

---

## 🙏 Acknowledgments

### Powered By

- **[Pollinations.ai](https://pollinations.ai)** - Free AI API that makes Polly possible
- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal formatting
- **[Requests](https://requests.readthedocs.io/)** - HTTP for Humans
- **[PyYAML](https://pyyaml.org/)** - YAML parser
- **[PyPDF](https://github.com/py-pdf/pypdf)** - PDF reading
- **[ReportLab](https://www.reportlab.com/)** - PDF generation

### Built For

The developer community, terminal enthusiasts, and anyone who believes in:
- **Free and open software**
- **Privacy by default**
- **Command-line power**
- **Cross-platform compatibility**

---

## 🐛 Bug Reports & Feature Requests

Found a bug? Have an idea? We want to hear from you!

- **GitHub Issues**: [github.com/rafabez/polly/issues](https://github.com/rafabez/polly/issues)
- **Discussions**: [github.com/rafabez/polly/discussions](https://github.com/rafabez/polly/discussions)

### Reporting Bugs

Please include:
- Your operating system (Linux, macOS, Windows + version)
- Python version (`python --version`)
- Polly version (`polly --version`)
- Command that caused the issue
- Full error message
- Expected vs. actual behavior

### Feature Requests

We're especially interested in:
- New AI modes (code review, test generation, etc.)
- Integration ideas (IDE plugins, Git tools, etc.)
- Platform-specific enhancements
- Workflow automation suggestions

---

## 📚 Additional Resources

### Documentation
- [Pollinations.ai API Docs](https://github.com/pollinations/pollinations/blob/main/APIDOCS.md)
- [Available Models](https://text.pollinations.ai/models)
- [Rich Documentation](https://rich.readthedocs.io/)

### Community
- **Star this repo** to show support!
- **Watch** for updates
- **Fork** to contribute
- **Share** with your developer friends

### Related Projects
Looking for more AI CLI tools?
- [aichat](https://github.com/sigoden/aichat) - Multi-provider AI chat
- [shell-gpt](https://github.com/TheR1D/shell_gpt) - OpenAI-powered shell
- [ai-cli](https://github.com/abhagsain/ai-cli) - GPT-3 in your terminal

---

## 🎉 What's Next?

Polly is constantly evolving! Here's what we're working on:

### Upcoming Features
- 🔌 Plugin system for custom modes
- 📊 Enhanced dashboard with statistics
- 🎨 Custom themes and color schemes
- 🔄 Auto-update functionality
- 💾 Local model support
- 🌐 More language translations
- 📱 Mobile companion app
- 🤖 Custom AI model training

### Stay Updated
Watch this repository for updates, or run:
```bash
polly --check-updates  # Coming soon!
```

---

<div align="center">

### Made with ❤️ by the Open Source Community

**If Polly helps you, consider giving it a ⭐ on GitHub!**

[⬆ Back to Top](#-polly---your-free-ai-terminal-companion)

---

*Polly - Because your terminal deserves an AI assistant that just works.*

**Free. Private. Cross-Platform. Forever.**

</div>
