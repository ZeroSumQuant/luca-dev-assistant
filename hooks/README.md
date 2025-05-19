# LUCA Git Hooks

This directory contains git hooks to enforce safety standards for the LUCA Dev Assistant project.

## Available Hooks

### pre-push
- Runs `safety-check.sh` before allowing any push to remote
- Ensures all tests pass with ≥95% coverage
- Verifies code formatting and linting
- Checks documentation is updated
- Blocks push if any check fails

## Installation

Run the installation script from the repository root:

```bash
./hooks/install.sh
```

This will:
1. Copy hooks to `.git/hooks/`
2. Make them executable
3. Backup any existing hooks

## Usage

Once installed, the hooks run automatically:
- `pre-push`: Triggered when you run `git push`

## Emergency Bypass

In critical situations where you need to push despite failures:

```bash
git push --no-verify
```

⚠️ **WARNING**: Use bypass only in emergencies. Document why safety checks were skipped.

## Uninstallation

To remove hooks:

```bash
rm .git/hooks/pre-push
```

## Hook Details

### pre-push Hook Checks:
1. Repository location verification
2. Virtual environment activation
3. Python version (3.13 required)
4. Code formatting (black, isort)
5. Linting (flake8)
6. Security scanning (bandit)
7. Test coverage (≥95%)
8. Documentation updates

## Development

To modify hooks:
1. Edit files in `hooks/` directory
2. Run `./hooks/install.sh` to update
3. Test thoroughly before committing

## Troubleshooting

### Hook not running
- Ensure hook is executable: `chmod +x .git/hooks/pre-push`
- Check hook exists: `ls -la .git/hooks/`

### Push blocked incorrectly
- Run `./safety-check.sh` manually to see specific failures
- Ensure virtual environment is activated
- Check Python version is 3.13

### Need to push urgently
- Use `git push --no-verify` (document why)
- Fix issues and run safety checks after

---

Remember: These hooks protect code quality and safety. Use bypass only when absolutely necessary.