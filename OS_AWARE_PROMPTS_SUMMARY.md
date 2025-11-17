# OS-Aware Prompts System - Implementation Summary

## Overview
Successfully updated Polly's prompts system to be OS-aware, allowing dynamic shell name adaptation based on the operating system (Linux, macOS, Windows).

## Changes Made

### 1. `/home/user/polly/polly/prompts.py`

#### Added OS Shell Names Mapping
```python
OS_SHELL_NAMES = {
    "Linux": "Linux/bash",
    "Darwin": "macOS/bash/zsh",  # Darwin is the system name for macOS
    "Windows": "Windows/PowerShell/CMD"
}
```

#### Updated `get_prompt()` Function
- Added `os_type` parameter with default value of `"Linux"` for backward compatibility
- Function signature:
  ```python
  def get_prompt(mode: str, content: str = "", language: str = "pt", os_type: str = "Linux", **kwargs) -> tuple:
  ```
- Automatically detects shell name from `OS_SHELL_NAMES` based on `os_type`
- Formats system prompts with the appropriate shell name
- Falls back to "Linux/bash" for unknown OS types

#### Updated Prompts (Both English and Portuguese)

**English (`PROMPTS_EN`):**
- `command` mode:
  - System: `"You are a {shell_name} command expert..."`
  - Template: `"Provide {num_versions} {versions_text} of {shell_name} command..."`

- `command_explain` mode:
  - System: `"You are a {shell_name} instructor..."`
  - Template: `"Provide the {shell_name} command to accomplish..."`

- `interactive` mode:
  - Updated to be more generic (removed "for Linux users")

**Portuguese (`PROMPTS_PT`):**
- `command` mode:
  - System: `"Você é um especialista em comandos {shell_name}..."`
  - Template: `"Forneça {num_versions} {versions_text} de comando {shell_name}..."`

- `command_explain` mode:
  - System: `"Você é um instrutor de {shell_name}..."`
  - Template: `"Forneça o comando {shell_name} para realizar..."`

- `interactive` mode:
  - Updated to be more generic (removed "para usuários Linux")

#### Updated `get_available_modes()` Function
- Changed descriptions for `command` and `command_explain` modes:
  - `"Get Linux/bash command"` → `"Get OS-specific command"`
  - `"Get Linux/bash command with explanations"` → `"Get OS-specific command with explanations"`

### 2. `/home/user/polly/polly/__main__.py`

#### Updated Interactive Mode
- Already had OS detection: `os_type = config.get_effective_os()`
- Updated to pass `os_type` to `get_prompt()`:
  ```python
  system_prompt, _ = get_prompt("interactive", language=language, os_type=os_type)
  ```

#### Standard Query Handling
- Already implemented with OS awareness:
  - Line 194: `os_type = config.get_effective_os()`
  - Lines 203, 206, 208: Pass `os_type` to all `get_prompt()` calls

## Features

### Dynamic Shell Name Injection
The system automatically injects the appropriate shell name based on OS:
- **Linux**: Commands use "Linux/bash" terminology
- **macOS**: Commands use "macOS/bash/zsh" terminology
- **Windows**: Commands use "Windows/PowerShell/CMD" terminology

### Backward Compatibility
- All existing code continues to work without modification
- Default `os_type="Linux"` ensures existing calls work as before
- Unknown OS types gracefully fall back to "Linux/bash"

### Language Support
- Works with both English (`en`) and Portuguese (`pt`, `pt-br`) prompts
- Shell names are injected consistently across all languages

## Testing

### Test Results
✅ All OS-aware functionality tests passed
✅ All backward compatibility tests passed
✅ Default behavior (no os_type) works correctly
✅ Unknown OS fallback works correctly

### Test Files Created
1. `/home/user/polly/test_os_aware_prompts.py` - Comprehensive OS-aware functionality tests
2. `/home/user/polly/test_backward_compatibility.py` - Backward compatibility verification

## Usage Examples

### Without OS Type (Default - Linux)
```python
system, user = get_prompt("command", "list files", language="en")
# System: "You are a Linux/bash command expert..."
```

### With Explicit OS Type
```python
# macOS
system, user = get_prompt("command", "list files", language="en", os_type="Darwin")
# System: "You are a macOS/bash/zsh command expert..."

# Windows
system, user = get_prompt("command", "list files", language="en", os_type="Windows")
# System: "You are a Windows/PowerShell/CMD command expert..."
```

### From Command Line
The `polly` CLI automatically detects the OS using `config.get_effective_os()` and passes it to the prompts system:
```bash
# On macOS, prompts will automatically use "macOS/bash/zsh"
polly -c "list all files"

# On Windows, prompts will automatically use "Windows/PowerShell/CMD"
polly -c "list all files"
```

## Benefits

1. **Cross-Platform Support**: Polly now provides contextually appropriate commands for each operating system
2. **Improved User Experience**: Users get OS-specific commands rather than Linux-only suggestions
3. **Maintainable**: Centralized OS shell name mapping makes updates easy
4. **Flexible**: Easy to add support for new OS types or shell combinations
5. **Backward Compatible**: No breaking changes to existing functionality

## Implementation Quality

- ✅ Clean, maintainable code
- ✅ Comprehensive documentation
- ✅ Full backward compatibility
- ✅ Proper fallback handling
- ✅ Both English and Portuguese support
- ✅ Well-tested functionality
- ✅ No breaking changes
