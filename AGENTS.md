# Repository Guidelines

- Use Python 3 syntax.
- Ensure Selenium API calls use the modern `By` locator methods.
- Before committing, run a syntax check:
  ```bash
  python3 -m py_compile $(git ls-files '*.py')
  ```
