# AETHERIX Scripts

This directory contains shell scripts for common development tasks.

## 🚀 Quick Start

```bash
# Initialize the development environment
./scripts/init.sh

# Run all tests
./scripts/run_tests.sh

# Run interactive demos
./scripts/run_demos.sh
```

## 📜 Available Scripts

### `init.sh` - Environment Setup

Sets up the development environment, creates a virtual environment, and installs dependencies.

```bash
# Standard setup
./scripts/init.sh

# Include development tools (linting, formatting)
./scripts/init.sh --dev
```

### `run_tests.sh` - Test Runner

Runs the test suite using pytest (if available) or unittest.

```bash
# Run tests
./scripts/run_tests.sh

# Verbose output
./scripts/run_tests.sh -v
./scripts/run_tests.sh --verbose

# With coverage reporting (requires coverage package)
./scripts/run_tests.sh --coverage
```

### `run_demos.sh` - Demo Runner

Runs interactive demonstrations of AETHERIX capabilities.

```bash
# Interactive menu
./scripts/run_demos.sh

# Run specific demo (1-6)
./scripts/run_demos.sh 1    # Link Budget Demo
./scripts/run_demos.sh 2    # DTN Routing Demo
./scripts/run_demos.sh 3    # Orbital Mechanics Demo
./scripts/run_demos.sh 4    # QKD Demo
./scripts/run_demos.sh 5    # Mars Mission Scenario
./scripts/run_demos.sh 6    # Integrated Demo

# Run all demos
./scripts/run_demos.sh all
```

### `link_budget_demo.sh` - Link Budget Demo

Quick script to run the link budget demonstration.

```bash
./scripts/link_budget_demo.sh
```

### `lint.sh` - Code Quality Checks

Runs code quality checks using flake8, black, isort, and mypy.

```bash
# Check code (no modifications)
./scripts/lint.sh

# Auto-fix issues
./scripts/lint.sh --fix
```

**Note:** Install dev dependencies first with `./scripts/init.sh --dev`

### `clean.sh` - Cleanup

Removes build artifacts, cache files, and temporary files.

```bash
# Clean caches and build artifacts
./scripts/clean.sh

# Also remove virtual environment
./scripts/clean.sh --all
```

## 📁 File Structure

```
scripts/
├── init.sh             # Environment setup
├── run_tests.sh        # Test runner
├── run_demos.sh        # Demo runner (interactive)
├── link_budget_demo.sh # Link budget demo
├── lint.sh             # Code quality checks
├── clean.sh            # Cleanup script
└── README.md           # This file
```

## 🔧 Requirements

- **Bash 4.0+**
- **Python 3.9+**

## 💡 Tips

1. All scripts can be run from any directory - they automatically find the project root.
2. Scripts will automatically activate the virtual environment if it exists.
3. Use `--help` or `-h` on most scripts to see available options.
4. The `init.sh` script sets up `PYTHONPATH` for you.
