# CLAUDE.md

## Development Workflow

```bash
# 1. Run tests
uv run pytest tests/ -v

# 2. Before creating PR
pre-commit run --all-files && uv run pytest tests/ -v
```
