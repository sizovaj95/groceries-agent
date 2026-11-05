## General
- this project uses uv as a project manger
- all logic code is located in `src` folder
- constant.py has configurations, constant and file paths that are not secret.
- Secrets should go to `.env`. Never put secrets into any other file, no exceptions

## Testing
- all test should be created in tests/ folder
- each module should have its own test file
- file naming convention for modules: test_<name_of_module>.py
- unit tests for module should be existing within a class defined as follows:
```
from unittest import TestCase

import src.module import as mod

class TestModule1(TestCase):
    def test_function_one(self):
        test_data = []
        result = mod.function_one(test_data)
        expected = "expected result"
        self.assertEqual(expected, result)
```
- if function being tested requiers connection to external services (like OCR service or LLM API), this service should be mocked via unittest patch. Never use real third-party services in tests. Third-party local packages (e.g. pandas) are ok to be used during tests
- tests can be ran with `uv run pytest tests/`

