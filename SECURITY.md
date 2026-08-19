# Security Policy

RepoReady is a local developer tool that writes setup files into repositories. Security matters because the tool handles paths, repository files, backups, and generated configuration.

---

## Supported Versions

Security fixes are handled for the latest release and the current `main` branch.

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| `main` branch | Yes |
| Older versions | No |

---

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Use GitHub private vulnerability reporting if it is available. If it is not available, open a public issue asking for a private contact method, but do not include exploit details, private data, tokens, passwords, or proof-of-concept code in the public issue.

Useful details to include privately:

- Summary of the issue
- Affected command or module
- Steps to reproduce
- Possible impact
- Operating system
- Python version
- Suggested fix, if available

---

## Security Expectations

RepoReady should:

- Avoid writing outside the selected repository path
- Avoid executing scanned project code
- Avoid printing secrets
- Avoid uploading repository contents anywhere
- Back up overwritten files when requested
- Treat unusual paths safely
- Fail with clear errors when something is unsafe

---

## Sensitive Files

Do not include real secrets in issues, tests, pull requests, screenshots, or examples.

Sensitive data includes:

- API keys
- Passwords
- Private keys
- Access tokens
- `.env` values
- Cloud credentials
- Private repository contents

If sensitive data is exposed accidentally, remove it and rotate the secret immediately.

---

## Scope

Security scope includes:

- CLI behavior
- Path handling
- File writing
- Backup and restore behavior
- Cleanup behavior
- Config loading
- Report generation
- Generated file safety

Vulnerabilities in projects prepared by RepoReady should be reported to those project maintainers.

---

## Thank You

Thank you for helping keep RepoReady safe and trustworthy.
