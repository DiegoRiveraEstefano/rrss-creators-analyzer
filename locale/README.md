# Translations

Configure `LANGUAGES` in `config/settings/base.py` for any supported locales, then extract translation strings with:

```bash
uv run python manage.py makemessages --all --no-location
```

This generates `django.po` files under `<locale>/LC_MESSAGES/django.po`. Translate `msgid` entries into `msgstr`, for example:

```po
msgid "users"
msgstr "utilisateurs"
```

Compile translations into binary `.mo` files used at runtime:

```bash
uv run python manage.py compilemessages
```

Django reads `.mo` files rather than `.po` files directly; outdated `.mo` files will hide updated translations.

## Production

The container image runs `compilemessages` during build, so keeping `.po` files updated is sufficient for deployment.

## Add a New Language

1. Update [`LANGUAGES`](https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-LANGUAGES) in `config/settings/base.py`.
2. Create the locale directory next to this file (e.g., `fr_FR`).
3. Run `uv run python manage.py makemessages --all --no-location` and translate the generated `.po` file.
