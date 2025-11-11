# Changelog

All notable changes to Polly will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Multiple command versions**: `-c3` generates 3 different command versions
- **File support for debug/refactor**: `-d file.py` and `-r file.py` now work directly
- **Translate file mode**: `-tf LANG FILE` to translate file contents
- **Motivational mode**: `-x` for funny demotivational phrases with random seed
- **Version shortcut**: `-v` as alias for `--version`
- **Language configuration**: `--set-language` to set default prompt language
- **Multilingual prompts**: Support for Portuguese and English prompts
- **Improved error handling**: Helpful error messages with model suggestions
- **AUR packaging**: PKGBUILD and .SRCINFO for Arch/Manjaro/BigLinux
- **Enhanced help**: Rich-formatted help with examples and tips

### Changed
- Removed `--max-tokens` flag (not supported by Pollinations API)
- Improved `-d` and `-r` to accept optional file arguments
- Updated all documentation (README.md, README.pt-BR.md)
- Better validation for file inputs

### Fixed
- Fixed `-d` and `-r` not reading files directly
- Fixed translate mode not working with files
- Fixed prompt validation for modes with file inputs

### Planned
- Unit tests coverage
- Bash/Zsh completion scripts
- Man page
- Conversation history
- Response caching
- Plugin system

## [0.1.0] - 2025-01-09

### Added
- Initial release of Polly
- Multiple AI models support (Gemini, OpenAI, DeepSeek, Mistral, Qwen Coder)
- Multiple operation modes:
  - Default mode for general questions
  - Explain mode (-e) for file/content explanation
  - Command mode (-c) for bash command generation
  - Command explain mode (-ce) for commands with explanations
  - Debug mode (-d) for error analysis
  - Refactor mode (-r) for code improvements
  - Translate mode (-t) for text translation
  - Interactive mode (-i) for chat with context
- Configuration system with YAML file (~/.config/polly/config.yaml)
- Model selection (--model flag)
- Temperature control (--temperature flag)
- Streaming support (--stream flag)
- Output to file (--output flag)
- JSON output format (--json flag)
- Pipe support for stdin/stdout
- Beautiful terminal output with Rich library
- Markdown rendering
- Syntax highlighting for code
- Comprehensive documentation:
  - README.md
  - QUICKSTART.md
  - INSTALL.md
  - CONTRIBUTING.md
  - PROJECT_SUMMARY.md
- Example test scripts
- Makefile for common tasks
- GitHub Actions workflow
- MIT License
- Python 3.8+ support

### Technical Details
- Built with Python
- Uses Pollinations.ai free API
- Referrer: interzonesec.com
- Dependencies: requests, rich, pyyaml
- Modular architecture
- Type hints
- Comprehensive error handling
- PEP 8 compliant

[Unreleased]: https://github.com/rafabez/polly/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rafabez/polly/releases/tag/v0.1.0
