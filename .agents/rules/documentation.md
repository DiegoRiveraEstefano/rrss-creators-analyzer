---
trigger: always_on
---

# RRSS Creators Analyzer: Living Documentation

1. **Single Source of Truth**:
   - Root markdown files (`README.md`, `DOCS.md`, `GUIDELINES.md`, `STYLE_GUIDE.md`, `DESIGN.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `AGENTS.md`) and `docs/` contain the canonical specification of the system.
   - `old-migrations/` is kept strictly as historical reference for the legacy domain schema.
2. **Synchronous Updates**:
   - If a model, service signature, role permission, table, filter, or environment variable changes, the corresponding documentation must be updated in the same pull request.
3. **English Standard**:
   - All `.md` documentation files are maintained in neutral, concise, technical English.
