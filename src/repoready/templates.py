"""Template generation for repository setup files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .models import GeneratedFile, ProjectProfile, SetupLevel, SetupOptions


class TemplateLibrary:
    """Build generated files for a repository profile."""

    def build(self, root: Path, profile: ProjectProfile, options: SetupOptions) -> List[GeneratedFile]:
        """Build a complete list of files for the selected profile."""

        files: List[GeneratedFile] = []
        project_name = root.name
        files.extend(self._common(project_name, profile, options))
        if options.include_github:
            files.extend(self._github(profile, options))
        if options.include_language_configs:
            if profile is ProjectProfile.PYTHON:
                files.extend(self._python(project_name, options))
            elif profile is ProjectProfile.NODE:
                files.extend(self._node(options))
            elif profile is ProjectProfile.GO:
                files.extend(self._go(options))
            elif profile is ProjectProfile.RUST:
                files.extend(self._rust(options))
            elif profile is ProjectProfile.WEB:
                files.extend(self._web(options))
        if profile is ProjectProfile.DOCKER or options.include_docker:
            files.extend(self._docker(project_name))
        return self._dedupe(files)

    def _file(self, path: str, content: str, group: str, description: str) -> GeneratedFile:
        if not content.endswith("\n"):
            content += "\n"
        return GeneratedFile(path=path, content=content, group=group, description=description)

    def _dedupe(self, files: List[GeneratedFile]) -> List[GeneratedFile]:
        seen = set()
        result: List[GeneratedFile] = []
        for file in files:
            if file.path in seen:
                continue
            seen.add(file.path)
            result.append(file)
        return result

    def _common(self, project_name: str, profile: ProjectProfile, options: SetupOptions) -> List[GeneratedFile]:
        files: List[GeneratedFile] = []
        files.append(self._file(".gitignore", self._gitignore(profile), "common", "Git ignore rules"))
        files.append(self._file(".gitattributes", GITATTRIBUTES, "common", "Git line-ending rules"))
        if options.include_editorconfig:
            files.append(self._file(".editorconfig", EDITORCONFIG, "common", "Editor consistency"))
        if options.include_env:
            files.append(self._file(".env.example", env_example(project_name), "common", "Environment example"))
        if options.include_security and options.level is not SetupLevel.MINIMAL:
            files.append(self._file("SECURITY.md", security_md(project_name), "common", "Security policy"))
        if options.level is SetupLevel.STRICT:
            files.append(self._file("CONTRIBUTING.md", contributing_md(project_name), "common", "Contribution guide"))
        return files

    def _github(self, profile: ProjectProfile, options: SetupOptions) -> List[GeneratedFile]:
        files = [
            self._file(".github/PULL_REQUEST_TEMPLATE.md", PR_TEMPLATE, "github", "Pull request template"),
            self._file(".github/ISSUE_TEMPLATE/bug_report.md", BUG_TEMPLATE, "github", "Bug issue template"),
            self._file(".github/ISSUE_TEMPLATE/feature_request.md", FEATURE_TEMPLATE, "github", "Feature issue template"),
            self._file(".github/workflows/ci.yml", ci_workflow(profile), "github", "GitHub Actions CI"),
        ]
        if options.include_dependabot and options.level is not SetupLevel.MINIMAL:
            files.append(self._file(".github/dependabot.yml", dependabot_yml(profile), "github", "Dependabot config"))
        if options.level is SetupLevel.STRICT:
            files.append(self._file(".github/ISSUE_TEMPLATE/config.yml", ISSUE_CONFIG, "github", "Issue template chooser"))
        return files

    def _python(self, project_name: str, options: SetupOptions) -> List[GeneratedFile]:
        files = [
            self._file("ruff.toml", RUFF_TOML, "python", "Ruff lint configuration"),
            self._file("mypy.ini", MYPY_INI, "python", "Mypy type checking configuration"),
            self._file("pytest.ini", PYTEST_INI, "python", "Pytest configuration"),
        ]
        if options.include_precommit:
            files.append(self._file(".pre-commit-config.yaml", PRECOMMIT_YAML, "python", "Pre-commit hooks"))
        if options.level is SetupLevel.STRICT:
            files.append(self._file("pyproject.toml", python_pyproject(project_name), "python", "Python package metadata"))
        return files

    def _node(self, options: SetupOptions) -> List[GeneratedFile]:
        files = [
            self._file(".prettierrc", PRETTIERRC, "node", "Prettier configuration"),
            self._file(".prettierignore", PRETTIERIGNORE, "node", "Prettier ignore rules"),
        ]
        if options.level is SetupLevel.STRICT:
            files.append(self._file(".npmrc", NPMRC, "node", "NPM defaults"))
        return files

    def _go(self, options: SetupOptions) -> List[GeneratedFile]:
        files = [self._file(".golangci.yml", GOLANGCI, "go", "Go lint configuration")]
        if options.level is SetupLevel.STRICT:
            files.append(self._file("Makefile", GO_MAKEFILE, "go", "Go development commands"))
        return files

    def _rust(self, options: SetupOptions) -> List[GeneratedFile]:
        files = [self._file("rustfmt.toml", RUSTFMT, "rust", "Rust formatting configuration")]
        if options.level is SetupLevel.STRICT:
            files.append(self._file(".cargo/config.toml", CARGO_CONFIG, "rust", "Cargo configuration"))
        return files

    def _web(self, options: SetupOptions) -> List[GeneratedFile]:
        files = [
            self._file(".prettierrc", PRETTIERRC, "web", "Prettier configuration"),
            self._file(".prettierignore", PRETTIERIGNORE, "web", "Prettier ignore rules"),
        ]
        if options.level is SetupLevel.STRICT:
            files.append(self._file(".stylelintrc.json", STYLELINTRC, "web", "Stylelint configuration"))
        return files

    def _docker(self, project_name: str) -> List[GeneratedFile]:
        return [
            self._file("Dockerfile", dockerfile(project_name), "docker", "Docker image definition"),
            self._file("compose.yaml", compose_yaml(project_name), "docker", "Docker Compose setup"),
            self._file(".dockerignore", DOCKERIGNORE, "docker", "Docker ignore rules"),
        ]

    def _gitignore(self, profile: ProjectProfile) -> str:
        sections: Dict[ProjectProfile, str] = {
            ProjectProfile.PYTHON: PYTHON_GITIGNORE,
            ProjectProfile.NODE: NODE_GITIGNORE,
            ProjectProfile.GO: GO_GITIGNORE,
            ProjectProfile.RUST: RUST_GITIGNORE,
            ProjectProfile.WEB: NODE_GITIGNORE,
            ProjectProfile.DOCKER: DOCKER_GITIGNORE,
            ProjectProfile.GENERAL: GENERAL_GITIGNORE,
            ProjectProfile.AUTO: GENERAL_GITIGNORE,
        }
        return sections.get(profile, GENERAL_GITIGNORE)


GENERAL_GITIGNORE = """# OS files
.DS_Store
Thumbs.db

# Editor folders
.vscode/
.idea/

# Environment files
.env
.env.*
!.env.example

# Logs
*.log

# RepoReady internals
.repoready/backups/
"""

PYTHON_GITIGNORE = GENERAL_GITIGNORE + """
# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.venv/
venv/
"""

NODE_GITIGNORE = GENERAL_GITIGNORE + """
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
.next/
dist/
build/
coverage/
"""

GO_GITIGNORE = GENERAL_GITIGNORE + """
# Go
bin/
*.test
*.out
coverage.out
vendor/
"""

RUST_GITIGNORE = GENERAL_GITIGNORE + """
# Rust
target/
Cargo.lock
"""

DOCKER_GITIGNORE = GENERAL_GITIGNORE + """
# Docker
.docker/
compose.override.yaml
"""

GITATTRIBUTES = """* text=auto eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf
"""

EDITORCONFIG = """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true

[*.py]
indent_size = 4

[Makefile]
indent_style = tab
"""

RUFF_TOML = """line-length = 100
target-version = "py39"

[lint]
select = ["E", "F", "I", "B", "UP", "SIM"]
ignore = ["UP006", "UP007"]
"""

MYPY_INI = """[mypy]
python_version = 3.9
ignore_missing_imports = True
warn_unused_configs = True
strict_optional = True
"""

PYTEST_INI = """[pytest]
testpaths = tests
addopts = -ra
"""

PRECOMMIT_YAML = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
      - id: ruff-format
"""

PRETTIERRC = """{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "es5",
  "printWidth": 100
}
"""

PRETTIERIGNORE = """node_modules
dist
build
coverage
.next
.env
.env.*
"""

NPMRC = """fund=false
audit=true
save-exact=true
"""

GOLANGCI = """run:
  timeout: 5m

linters:
  enable:
    - govet
    - staticcheck
    - ineffassign
    - misspell
"""

GO_MAKEFILE = """.PHONY: test lint run

test:
	go test ./...

lint:
	golangci-lint run

run:
	go run ./...
"""

RUSTFMT = """edition = "2021"
max_width = 100
newline_style = "Unix"
"""

CARGO_CONFIG = """[build]
rustflags = ["-D", "warnings"]
"""

STYLELINTRC = """{
  "extends": ["stylelint-config-standard"]
}
"""

DOCKERIGNORE = """.git
.github
.repoready
.env
.env.*
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
node_modules
dist
build
coverage
README.md
"""

PR_TEMPLATE = """## Summary

Describe the change and why it is needed.

## Checks

- [ ] Tests pass locally
- [ ] Documentation is updated if needed
- [ ] The change is focused and easy to review
"""

BUG_TEMPLATE = """---
name: Bug report
about: Report a problem that should be fixed
title: "Bug: "
labels: bug
assignees: ""
---

## What happened?

Describe the problem clearly.

## Expected behavior

What did you expect to happen?

## Steps to reproduce

1.
2.
3.

## Environment

- OS:
- Tool version:
- Relevant command:
"""

FEATURE_TEMPLATE = """---
name: Feature request
about: Suggest an improvement
title: "Feature: "
labels: enhancement
assignees: ""
---

## Problem

What problem should this solve?

## Proposed solution

Describe the feature or change.

## Alternatives

Any other approaches considered?
"""

ISSUE_CONFIG = """blank_issues_enabled: true
contact_links:
  - name: Questions and discussions
    url: https://github.com/n-vim/RepoReady/discussions
    about: Ask questions or discuss ideas here.
"""


def env_example(project_name: str) -> str:
    return f"""# {project_name} environment example
APP_ENV=development
LOG_LEVEL=info
"""


def security_md(project_name: str) -> str:
    return f"""# Security Policy

Thank you for helping keep {project_name} safe.

Please do not report security vulnerabilities in public issues. If you find a security problem, use GitHub private vulnerability reporting when available. If it is not available, open a public issue asking for a private contact method without sharing exploit details or sensitive information.

## Scope

Security reports may include unsafe file handling, path traversal, secret exposure, unsafe command execution, dependency risks, or behavior that could damage a user's repository.

## Safe Reporting

Please include:

- A short summary
- Steps to reproduce
- Affected files or commands
- Possible impact
- Suggested fix, if available

Do not include real tokens, passwords, private keys, or private repository data.
"""


def contributing_md(project_name: str) -> str:
    return f"""# Contributing to {project_name}

Thank you for your interest in contributing.

## Development

1. Fork the repository.
2. Create a focused branch.
3. Make your change.
4. Add tests or documentation when needed.
5. Open a pull request with a clear explanation.

## Guidelines

- Keep changes focused.
- Prefer simple solutions.
- Avoid unrelated formatting changes.
- Do not commit secrets, cache folders, or build output.
- Make sure tests pass before submitting.
"""


def ci_workflow(profile: ProjectProfile) -> str:
    if profile is ProjectProfile.NODE or profile is ProjectProfile.WEB:
        return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
      - run: npm ci
      - run: npm test --if-present
      - run: npm run lint --if-present
"""
    if profile is ProjectProfile.GO:
        return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - run: go test ./...
"""
    if profile is ProjectProfile.RUST:
        return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test --all
      - run: cargo clippy --all-targets -- -D warnings
"""
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -e ".[dev]"
      - run: pytest
      - run: ruff check .
"""


def dependabot_yml(profile: ProjectProfile) -> str:
    ecosystems = ["github-actions"]
    if profile is ProjectProfile.PYTHON:
        ecosystems.append("pip")
    elif profile in {ProjectProfile.NODE, ProjectProfile.WEB}:
        ecosystems.append("npm")
    elif profile is ProjectProfile.GO:
        ecosystems.append("gomod")
    elif profile is ProjectProfile.RUST:
        ecosystems.append("cargo")
    blocks = [
        "version: 2",
        "updates:",
    ]
    for ecosystem in ecosystems:
        blocks.extend(
            [
                f"  - package-ecosystem: {ecosystem}",
                "    directory: \"/\"",
                "    schedule:",
                "      interval: weekly",
            ]
        )
    return "\n".join(blocks) + "\n"


def python_pyproject(project_name: str) -> str:
    package_name = project_name.replace("-", "_").replace(" ", "_").lower()
    return f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "Clean Python project prepared with RepoReady."
readme = "README.md"
requires-python = ">=3.9"
license = {{ text = "MIT" }}
authors = [{{ name = "Nitish Vimal" }}]
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "ruff>=0.5.0", "mypy>=1.10.0"]

[tool.hatch.build.targets.wheel]
packages = ["src/{package_name}"]
"""


def dockerfile(project_name: str) -> str:
    return f"""FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip

CMD ["python", "-m", "{project_name.replace('-', '_')}"]
"""


def compose_yaml(project_name: str) -> str:
    service = project_name.lower().replace("_", "-").replace(" ", "-")
    return f"""services:
  {service}:
    build: .
    env_file:
      - .env
    volumes:
      - .:/app
"""
