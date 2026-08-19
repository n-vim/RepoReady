# Contributing to RepoReady

Thank you for your interest in contributing to RepoReady.

RepoReady is a Python CLI that prepares repositories with clean config files, workflows, templates, and setup essentials. The project should stay simple, practical, readable, and safe to use.

---

## Ways to Contribute

You can help by:

- Fixing bugs
- Improving generated config files
- Adding tests
- Improving documentation
- Improving project detection
- Improving repository health checks
- Improving CLI messages
- Suggesting useful setup profiles

---

## Development Setup

Clone the repository:

```bash
git clone https://github.com/n-vim/RepoReady.git
cd RepoReady
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -e ".[dev]"
```

---

## Running Checks

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

---

## Pull Request Guidelines

Before opening a pull request:

- Keep the change focused
- Add tests when behavior changes
- Update documentation when user-facing behavior changes
- Avoid unrelated formatting changes
- Do not commit cache/build folders
- Do not commit secrets or local environment files
- Make sure tests pass locally

---

## Adding New Generated Files

When adding a generated file:

1. Add the template in `src/repoready/templates.py`.
2. Add it to the correct profile or setup level.
3. Make sure it is safe and useful by default.
4. Add tests for the generated output.
5. Update the README if the behavior is user-facing.

Generated files should be practical, clean, and not overly opinionated.

---

## Adding New Checks

Repository health checks should help users improve their project.

A good check should:

- Have a clear purpose
- Produce a useful message
- Avoid noisy false positives
- Include a suggestion when something is missing
- Include tests

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
