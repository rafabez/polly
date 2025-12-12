# Contributing to Polly AI

Thank you for your interest in contributing to Polly AI! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/rafabez/polly.git
   cd polly
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux
   ```
4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

## 🔧 Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Test your changes**:
   ```bash
   # Test the CLI
   polly "test query"
   polly -i
   polly -c "test command"
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

## 📝 Code Style

- Follow [PEP 8](https://pep8.org/) Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Comment complex logic

## 🧪 Testing

Before submitting a PR, please test:

- Basic queries: `polly "test"`
- All modes: `-e`, `-c`, `-ce`, `-d`, `-r`, `-t`, `-i`
- Different models: `--model gemini`, `--model openai`, etc.
- Piping: `echo "test" | polly -e`
- Configuration: `--config`, `-M` / `--set-default-model`
- Error handling: invalid inputs, network errors, etc.

## 🎯 Areas for Contribution

### High Priority
- Add unit tests
- Improve error handling
- Add more prompt templates
- Optimize context truncation for interactive mode
- Add bash/zsh completion scripts

### Medium Priority
- Add more examples to README
- Improve documentation
- Add support for custom prompts
- Add history/logging feature
- Create man page

### Low Priority
- Add color themes
- Add plugin system
- Add voice output (if feasible in terminal)
- Add image analysis support

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Exact commands to reproduce the bug
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**:
   - OS and version
   - Python version
   - Polly version
   - Relevant configuration

## 💡 Feature Requests

When requesting features, please include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other ways to achieve the same goal
4. **Examples**: Example commands/usage

## 📋 Pull Request Guidelines

- **One feature per PR**: Keep PRs focused
- **Update documentation**: Update README if needed
- **Test thoroughly**: Ensure nothing breaks
- **Clear description**: Explain what and why
- **Reference issues**: Link related issues

## 🏗️ Project Structure

```
polly/
├── polly/
│   ├── __init__.py       # Package info
│   ├── __main__.py       # Entry point and main logic
│   ├── api.py            # Pollinations API client
│   ├── cli.py            # Argument parsing
│   ├── config.py         # Configuration management
│   ├── prompts.py        # Prompt templates
│   └── utils.py          # Helper functions
├── tests/                # Test suite (to be added)
├── setup.py              # Installation script
├── pyproject.toml        # Modern packaging config
└── requirements.txt      # Dependencies
```

## 📞 Communication

- **GitHub Issues**: For bugs and features
- **Pull Requests**: For code contributions
- **Discussions**: For questions and ideas

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Every contribution, no matter how small, helps make Polly better for everyone!
