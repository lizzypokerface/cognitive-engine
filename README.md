# cognitive-engine
General-Purpose Cognitive Automation Platform


## Getting Started

### Requirements

- **Python 3.13+**

### Setup

1. **Create a Virtual Environment:**

    In the root directory, run:

    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows use: venv\Scripts\activate
    ```

2. **Install Poetry:**

    Install [Poetry](https://python-poetry.org/docs/cli/) for dependency management:

    ```bash
    pip install -U pip setuptools
    pip install poetry
    ```

3. **Install Dependencies:**

    Use Poetry to install project dependencies:

    ```bash
    poetry install --no-root
    ```

    *(Note: This installs pandas, selenium, pyyaml, openai, and other core libraries).*

4. **Set Up Pre-Commit Hooks:**

    Install [pre-commit](https://pre-commit.ci/) hooks for static tests:

    ```bash
    pre-commit install
    ```
