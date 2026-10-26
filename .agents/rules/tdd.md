---
trigger: always_on
---

# RRSS Creators Analyzer: Test-Driven Development (TDD)

## Core Directives

1. **Pytest First**:
   - Tests execute via `uv run pytest` with `pytest-django`.
   - Settings module: `config.settings.test`.
2. **Factory-Boy for Fixtures**:
   - Model fixtures are built using `factory.django.DjangoModelFactory` (`CreatorFactory`, `ChannelFactory`, `StreamingSessionFactory`, `VideoFactory`, `VideoPublicationFactory`, `ChannelAlertFactory`).
   - Never hardcode raw database seeds across test cases.
3. **Role-Based Access & Visibility Testing**:
   - Always verify that users with `role=UserRole.CREATOR` can only view their own `Creator`, `StreamingSession`, `Video`, and `ChannelAlert` records, and receive `403` or empty querysets for other creators' data.
   - Verify that `manager`, `analyst`, and `company_admin` roles have the expected permissions.
4. **N+1 Prevention**:
   - Use `django_assert_max_num_queries` on selector, `django-tables2` list views, and dashboard tests.
5. **Coverage Requirements**:
   - Every `Service` method must have unit test coverage verifying:
     1. Happy path execution and database persistence.
     2. Guard clause violations (raising `BusinessLogicError`).
     3. Proper invalidation/update of `DiskCache` analytical keys.
