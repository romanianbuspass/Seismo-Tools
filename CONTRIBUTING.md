# Contributing to Seismo Tools

Thank you for contributing! This document outlines how to report issues, suggest features, and submit code.

## Reporting Issues

### Before You Report
1. Check existing issues to avoid duplicates
2. Test with the latest version
3. Gather error messages and context

### Creating an Issue
Include:
- **Tool name** (Sensor Terminal, Signal Generator, DMM Panel, etc.)
- **Environment** (Windows 10, Raspberry Pi OS, etc.)
- **Python version** (`python --version`)
- **Steps to reproduce**
- **Expected behavior** vs. actual behavior
- **Error messages or tracebacks**

**Example:**
```
Title: Sensor Terminal crashes on startup

Tool: Sensor Terminal
OS: Ubuntu 22.04
Python: 3.10.6

Error:
ImportError: No module named 'PyQt5'

Steps:
1. Run: python Sensor_Terminal.py
2. Observe: Crash immediately
```

## Feature Requests

Propose new features with:
- Clear use case (what problem does it solve?)
- Affected tool(s)
- Example workflow
- Related references or issues

**Example:**
```
Title: Add data smoothing filter to Sensor Terminal

Current: Raw sensor data has 50 Hz noise
Desired: Built-in low-pass filter option
Use Case: Field deployment with high-noise environment
```

## Submitting Code

### Fork & Branch
```bash
git clone https://github.com/yourusername/seismo-tools.git
cd seismo-tools
git checkout -b feature/your-feature-name
```

### Code Standards
- **Python**: PEP 8 (use `autopep8`)
- **Comments**: Docstring on all functions
- **Naming**: Descriptive variable names
- **Testing**: Manual test on Windows/Linux/Pi if possible

### Commit Messages
```
Feature: Add low-pass filter to Sensor Terminal
Fix: Serial port detection on Linux
Docs: Update README with hardware setup
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation

## Testing
- [ ] Tested on Windows
- [ ] Tested on Linux
- [ ] Tested on Raspberry Pi (if applicable)
- [ ] No regressions observed

## Related Issues
Fixes #123
```

## Development Setup

### Local Environment
```bash
# Clone
git clone https://github.com/yourusername/seismo-tools.git
cd seismo-tools

# Install dependencies
pip install PyQt5 pyserial numpy matplotlib

# Run tool
python Sensor_Terminal.py
```

### Debugging

**Print debug info:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Variable x = %s", x)
```

**Use Python debugger:**
```python
import pdb; pdb.set_trace()
```

## Building & Testing

### Test on Multiple Platforms
- **Windows 10/11** — Primary
- **Ubuntu 20.04+** — Secondary
- **Raspberry Pi OS** — Embedded

### Build Standalone
```bash
pyinstaller Sensor_Terminal.spec
# Test dist/Sensor_Terminal/
```

## Documentation

Updates welcome!

- **README.md** — Overview, features, quick start
- **QUICKREF.md** — API examples, troubleshooting
- **Docstrings** — In-code documentation
- **Comments** — Explain non-obvious logic

## Recognition

Contributors will be listed in:
- CONTRIBUTORS.md (all-time list)
- Release notes (per-version)

---

Thank you for making Seismo Tools better! 🙌
