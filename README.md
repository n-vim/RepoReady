<div align="center">

# RepoReady

**Prepare clean, consistent, GitHub-ready repositories from the command line.**

RepoReady is a Python CLI that adds essential configuration files, workflows, templates, and repository setup files to your project safely and quickly.

<br>

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-Typer-0E7C86?style=flat)
![Terminal](https://img.shields.io/badge/Terminal-Rich-4B8BBE?style=flat)
![Config](https://img.shields.io/badge/Config-YAML-yellow?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Beta-blue?style=flat)

</div>

---

## Overview

RepoReady helps developers prepare repositories with the files that are usually needed for clean project setup, open-source readiness, automation, and maintainability.

Instead of manually creating `.gitignore`, `.editorconfig`, GitHub Actions workflows, issue templates, pull request templates, Dependabot config, Docker files, linting configs, test configs, and other setup files, RepoReady can generate them for you in a controlled and safe way.

It is designed for developers who want their repositories to look clean, professional, and ready to use without repeating the same setup work again and again.

---

## Why RepoReady?

A good repository needs more than source code.

A clean project usually needs:

- Proper ignore rules
- Editor configuration
- Environment examples
- GitHub Actions workflow
- Dependabot configuration
- Issue templates
- Pull request template
- Security policy
- Language-specific config files
- Linting setup
- Testing setup
- Docker support
- Safe overwrite behavior
- Backup and restore support

RepoReady brings these essentials together into one simple CLI.

---

## Features

- Generate common repository setup files
- Detect project type automatically
- Support multiple project profiles
- Preview files before creating them
- Show unified diffs before overwriting
- Skip existing files by default
- Create backups before overwriting files
- Restore files from backups
- Validate repository setup with doctor reports
- Export doctor reports as Markdown or JSON
- Clean cache and build junk from repositories
- Support setup levels: `minimal`, `standard`, and `strict`
- Configure defaults with `.repoready.yaml`
- Works locally and offline
- Built with Python, Typer, Rich, and PyYAML

---

## Supported Profiles

RepoReady includes setup profiles for common project types.

| Profile | Purpose |
| --- | --- |
| `auto` | Detect the project type automatically |
| `general` | Add common repository essentials |
| `python` | Add Python project configuration files |
| `node` | Add Node.js and frontend project setup files |
| `go` | Add Go project setup files |
| `rust` | Add Rust project setup files |
| `web` | Add general web project setup files |
| `docker` | Add Docker-related setup files |

---

## Setup Levels

RepoReady supports different setup levels depending on how much configuration you want.

| Level | Description |
| --- | --- |
| `minimal` | Adds only the most important repository files |
| `standard` | Adds a balanced setup for most projects |
| `strict` | Adds stronger tooling, workflows, and repository quality files |

For most projects, `standard` is the best choice.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/n-vim/RepoReady.git
cd RepoReady
```

Install RepoReady locally:

```bash
python -m pip install -e .
```

For development setup:

```bash
python -m pip install -e ".[dev]"
```

Check that the CLI is installed:

```bash
repoready --help
```

You can also use the alternate command:

```bash
repo-ready --help
```

---

## Quick Start

Prepare the current repository automatically:

```bash
repoready setup .
```

Prepare a Python repository:

```bash
repoready setup . --profile python
```

Preview what RepoReady will create:

```bash
repoready preview . --profile python
```

Show a diff before applying changes:

```bash
repoready diff . --profile python
```

Run a repository setup check:

```bash
repoready doctor .
```

---

## Commands

| Command | Description |
| --- | --- |
| `setup` | Create repository setup files |
| `preview` | Preview files that would be generated |
| `diff` | Show unified diffs for generated changes |
| `doctor` | Check repository setup quality |
| `detect` | Detect the project type |
| `list` | List available setup profiles |
| `info` | Show details about a profile |
| `init` | Create a `.repoready.yaml` config file |
| `backups` | List available backups |
| `restore` | Restore files from a backup |
| `clean` | Remove cache and build junk |

---

## Usage Examples

### Prepare a repository

```bash
repoready setup .
```

This scans the current folder, detects the project type, and creates useful setup files.

---

### Use a specific profile

```bash
repoready setup . --profile python
```

This applies Python-focused repository configuration.

---

### Use a setup level

```bash
repoready setup . --profile python --level strict
```

This creates a stronger setup with more tooling and quality files.

---

### Preview without writing files

```bash
repoready preview . --profile python
```

Use this when you want to see what RepoReady would generate before touching your project.

---

### Show file differences

```bash
repoready diff . --profile python
```

This shows a unified diff so you can review changes before applying them.

---

### Force overwrite existing files

```bash
repoready setup . --profile python --force
```

RepoReady skips existing files by default. Use `--force` only when you intentionally want to overwrite files.

---

### Run doctor check

```bash
repoready doctor .
```

This checks whether the repository has important setup files and reports what is missing.

---

### Save a Markdown report

```bash
repoready doctor . --format markdown --output REPOREADY_REPORT.md
```

---

### Save a JSON report

```bash
repoready doctor . --format json --output repoready-report.json
```

---

### Detect project type

```bash
repoready detect .
```

Example output:

```text
Detected project type: python
```

---

### List profiles

```bash
repoready list
```

---

### View profile information

```bash
repoready info python
```

---

### Create a config file

```bash
repoready init
```

This creates a `.repoready.yaml` file in the current repository.

---

### List backups

```bash
repoready backups .
```

---

### Restore from backup

```bash
repoready restore . --backup latest
```

---

### Clean repository junk

```bash
repoready clean .
```

This removes common cache and build folders such as `__pycache__`, `.pytest_cache`, `dist`, and `build`.

---

## Files RepoReady Can Generate

Depending on the selected profile and setup level, RepoReady can generate files such as:

```text
.gitignore
.gitattributes
.editorconfig
.env.example
.repoready.yaml
pre-commit-config.yaml
pytest.ini
mypy.ini
ruff.toml
Dockerfile
.dockerignore
.github/workflows/ci.yml
.github/dependabot.yml
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
.github/pull_request_template.md
SECURITY.md
```

Language-specific profiles may generate additional files based on the project type.

---

## Python Profile

The Python profile can add files for common Python development workflows.

Example:

```bash
repoready setup . --profile python --level standard
```

Useful generated files may include:

```text
.gitignore
.editorconfig
.env.example
ruff.toml
pytest.ini
mypy.ini
pre-commit-config.yaml
.github/workflows/ci.yml
.github/dependabot.yml
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
.github/pull_request_template.md
SECURITY.md
```

This is useful for Python libraries, CLI tools, APIs, automation scripts, and open-source projects.

---

## Node Profile

The Node profile is useful for JavaScript, TypeScript, frontend, and full-stack projects.

Example:

```bash
repoready setup . --profile node
```

Useful generated files may include:

```text
.gitignore
.editorconfig
.env.example
.prettierrc
.github/workflows/ci.yml
.github/dependabot.yml
.github/pull_request_template.md
```

---

## Go Profile

The Go profile prepares repositories for Go projects.

Example:

```bash
repoready setup . --profile go
```

Useful generated files may include:

```text
.gitignore
.editorconfig
.github/workflows/ci.yml
.github/dependabot.yml
```

---

## Rust Profile

The Rust profile prepares repositories for Rust projects.

Example:

```bash
repoready setup . --profile rust
```

Useful generated files may include:

```text
.gitignore
.editorconfig
.github/workflows/ci.yml
.github/dependabot.yml
```

---

## Docker Profile

The Docker profile adds Docker-related repository files.

Example:

```bash
repoready setup . --profile docker
```

Useful generated files may include:

```text
Dockerfile
.dockerignore
.github/workflows/ci.yml
```

---

## Configuration

RepoReady supports a local config file named `.repoready.yaml`.

Create one with:

```bash
repoready init
```

Example configuration:

```yaml
default_profile: auto
default_level: standard
backup_on_overwrite: true
skip_existing: true

author:
  name: Nitish Vimal
  github: n-vim

doctor:
  fail_below: 60
  warn_below: 80

clean:
  remove:
    - __pycache__
    - .pytest_cache
    - .mypy_cache
    - .ruff_cache
    - dist
    - build
```

This helps keep repository setup consistent across multiple projects.

---

## Safe File Writing

RepoReady is designed to avoid damaging your existing files.

By default, it:

- Creates missing files
- Skips files that already exist
- Shows what will change in preview mode
- Can show diffs before writing
- Creates backups before overwriting files
- Lets you restore previous backups

Use `--force` only when you want RepoReady to overwrite existing files.

---

## Backup and Restore

When overwriting files, RepoReady can create backups so you can recover previous versions.

List backups:

```bash
repoready backups .
```

Restore the latest backup:

```bash
repoready restore . --backup latest
```

This makes it safer to apply setup changes to existing repositories.

---

## Doctor Reports

The `doctor` command checks repository setup health.

```bash
repoready doctor .
```

It can identify missing or incomplete setup essentials such as:

- `.gitignore`
- `.editorconfig`
- GitHub Actions workflow
- Dependabot config
- Issue templates
- Pull request template
- Security policy
- Environment example
- Language-specific config files

Export a Markdown report:

```bash
repoready doctor . --format markdown --output REPOREADY_REPORT.md
```

Export a JSON report:

```bash
repoready doctor . --format json --output repoready-report.json
```

---

## Clean Command

The `clean` command removes common generated junk and cache folders.

```bash
repoready clean .
```

Examples of folders it can remove:

```text
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
dist
build
node_modules/.cache
```

This is useful before pushing a repository to GitHub.

---

## Example Workflow

A good workflow for a new Python project:

```bash
repoready detect .
repoready preview . --profile python --level standard
repoready diff . --profile python --level standard
repoready setup . --profile python --level standard
repoready doctor .
```

For an existing repository:

```bash
repoready doctor .
repoready preview . --profile auto
repoready diff . --profile auto
repoready setup . --profile auto
```

---

## Project Structure

```text
RepoReady/
├── src/
│   └── repoready/
│       ├── __init__.py
│       ├── cli.py
│       ├── backups.py
│       ├── clean.py
│       ├── config.py
│       ├── detector.py
│       ├── doctor.py
│       ├── files.py
│       ├── models.py
│       ├── profiles.py
│       ├── renderer.py
│       ├── reports.py
│       ├── templates.py
│       └── utils.py
├── tests/
├── .github/
│   └── workflows/
│       └── ci.yml
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── pyproject.toml
└── .gitignore
```

---

## Built With

| Tool | Purpose |
| --- | --- |
| Python | Main programming language |
| Typer | Command-line interface |
| Rich | Terminal output |
| PyYAML | YAML configuration |
| Pytest | Testing |
| Ruff | Linting |
| Mypy | Type checking |
| Hatchling | Build backend |

---

## Development

Clone the repository:

```bash
git clone https://github.com/n-vim/RepoReady.git
cd RepoReady
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Run type checking:

```bash
mypy src
```

Run the CLI locally:

```bash
repoready --help
```

---

## Testing

Run the full test suite:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/test_cli.py
```

---

## Recommended GitHub Topics

Use these topics for the repository:

```text
python
cli
developer-tools
repository
automation
project-setup
github
configuration
typer
rich
```

---

## Good Use Cases

RepoReady is useful for:

- Preparing a new GitHub repository
- Cleaning up an existing project
- Adding missing setup files
- Creating consistent project configuration
- Preparing open-source repositories
- Adding GitHub workflow files
- Setting up Python project tooling
- Creating professional project structure
- Auditing repository readiness
- Removing cache and build junk

---

## Roadmap

Planned improvements:

- More profile-specific setup files
- Custom user-defined profiles
- More advanced doctor scoring
- HTML report output
- GitHub repository scanning
- Interactive setup mode
- Better monorepo support
- More framework-specific profiles
- Config migration support
- Project setup recommendations based on detected files

---

## Contributing

Contributions are welcome.

You can help by:

- Adding new profiles
- Improving generated files
- Adding tests
- Improving doctor checks
- Improving documentation
- Fixing bugs
- Improving CLI output
- Suggesting better setup defaults

Before contributing, please keep the project simple, safe, and practical.

---

## Security

If you find a security issue, please do not open a public issue with sensitive details.

Use GitHub's private vulnerability reporting feature if available, or open a public issue asking for a private contact method without including exploit details.

RepoReady should never expose secrets, execute scanned project code, or write outside the target repository path.

---

## Author

Created by **Nitish Vimal**.

GitHub: [n-vim](https://github.com/n-vim)

---

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**RepoReady helps you prepare cleaner repositories with less manual setup.**

</div>
