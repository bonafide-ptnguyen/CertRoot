# Continuous Integration (CI) Implementation

This document describes the Continuous Integration (CI) setup for the backend of the project. The CI pipeline is implemented using **GitHub Actions** and is currently focused on:

- Automatically running **unit tests** on every change.
- Automatically running **system tests** on every change.
- Providing fast feedback through the GitHub **Actions** tab.

> ✅ The screenshot from the GitHub Actions “CI” workflow view (multiple green runs) confirms that the pipeline is running successfully and all recent workflow executions have completed with a **successful** status.

---

## 1. CI Objectives

The main goals of the CI pipeline are:

1. **Early feedback:** Automatically test code whenever a commit is pushed or a pull request (PR) is opened.
2. **Regression prevention:** Ensure that changes do not break existing functionality by running both unit and system tests.
3. **Consistency:** Always execute tests in a clean, repeatable environment (GitHub-hosted runners).
4. **Visibility:** Make the test status clearly visible to the team through GitHub’s green (success) / red (failure) indicators.

At this stage, the CI pipeline is **testing-focused only**. Deployment and other CD-related activities are intentionally left for future work.

---

## 2. Tooling and Technologies

- **Version Control:** Git + GitHub repository  
- **CI Platform:** GitHub Actions  
- **Language:** Python 3.11  
- **Test Framework:** `pytest`  
- **Backend Stack:** Python backend (e.g., FastAPI and related libraries)  
- **Dependency Management:** `requirements.txt` stored in the `backend` directory  

---

## 3. Relevant Repository Structure

The CI configuration assumes the following structure (simplified):

```text
project-root/
├── backend/
│   ├── __init__.py
│   ├── certifier_integration.py
│   ├── requirements.txt
│   └── tests/
│       ├── unittests/
│       │   └── ... (unit test files)
│       └── systemtests/
│           └── ... (system test files)
└── .github/
    └── workflows/
        └── ci.yml
```

Key points:

- `backend/requirements.txt` contains **all** backend Python dependencies (e.g., `fastapi`, `uvicorn`, `web3`, `pymongo`, `blake3`, `httpx`, `python-multipart`, `pytest`, etc.).
- `backend/tests/unittests/` contains unit test modules.
- `backend/tests/systemtests/` contains higher-level system test modules.
- `.github/workflows/ci.yml` defines the GitHub Actions workflow.

---

## 4. Workflow Triggers

The CI workflow is configured to run automatically on:

- **Pushes** to the main development branches.
- **Pull requests** targeting those branches.

Example trigger configuration:

```yaml
name: Backend CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

This ensures that both direct commits and PRs are validated before integration.

---

## 5. Environment and Dependencies

To keep CI consistent with local development, the workflow installs dependencies from `backend/requirements.txt` rather than listing packages individually.

Typical install step:

```yaml
- name: Install backend dependencies
  working-directory: backend
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

This guarantees that:

- The same versions of libraries used locally (e.g., FastAPI, web3, pymongo, etc.) are also used in CI.
- Adding new dependencies only requires updating `requirements.txt`, not the workflow file.

The environment variable `PYTHONPATH` is set to the repository root so that `backend` can be imported as a package during tests:

```yaml
env:
  PYTHONPATH: ${{ github.workspace }}
```

---

## 6. CI Jobs

The current CI pipeline is structured into two testing jobs:

1. **`unit-tests`** – runs backend unit tests.
2. **`system-tests`** – runs backend system tests and depends on the success of the unit tests.

The jobs are defined in `.github/workflows/ci.yml`.

### 6.1 Job 1: Unit Tests

**Purpose:** Validate core backend functionality at a fine-grained level.

Main responsibilities:

- Check out the repository.
- Set up Python 3.11 on the GitHub runner.
- Install all backend dependencies from `requirements.txt`.
- Run unit tests in `backend/tests/unittests/`.

Example configuration:

```yaml
unit-tests:
  runs-on: ubuntu-latest
  env:
    PYTHONPATH: ${{ github.workspace }}

  steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Install backend dependencies
      working-directory: backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run unit tests
      working-directory: backend
      run: |
        python -m pytest tests/unittests/ -v
```

If any unit test fails, this job is marked as failed and later jobs are skipped to prevent further processing of a broken build.

---

### 6.2 Job 2: System Tests

**Purpose:** Exercise the backend at a higher level, verifying integrated behaviour and end-to-end flows.

This job:

- Depends on `unit-tests` (runs only if unit tests pass).
- Repeats the environment setup and dependency installation.
- Runs tests located under `backend/tests/systemtests/`.

Example configuration:

```yaml
system-tests:
  runs-on: ubuntu-latest
  needs: unit-tests
  env:
    PYTHONPATH: ${{ github.workspace }}

  steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Install backend dependencies
      working-directory: backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run system tests
      working-directory: backend
      run: |
        python -m pytest tests/systemtests/ -v
```

By chaining the jobs with `needs: unit-tests`, the pipeline enforces a logical order:

```text
Unit tests must pass → then system tests run.
```

---

## 7. Evidence of Successful CI Runs

The GitHub Actions **CI** workflow page shows multiple recent runs, all marked with a green check mark (✔) and completed successfully. Each run is associated with a commit or pull request message such as:

- “Add GitHub Actions CI workflow”
- “Add basic unit tests for hello, hashing, blockchain”
- “Add comprehensive unit tests (hello, hashing, blockchain)”

Each run also displays a short duration (e.g., 17–25 seconds), confirming that:

- The CI workflow is correctly configured and being triggered on pushes and PRs.
- The defined jobs (unit and system tests) are executing without errors.
- The project currently has a stable build, as no recent runs are failing.

A screenshot of this view can be embedded in this document as:

```md
![CI Workflow Runs Screenshot](/CertRoot/CI_Success.png)
```

---

## 8. Future Improvements (Beyond Current Scope)

While the current CI focuses on automated testing, several enhancements can be implemented later:

- **Static analysis and linting** (e.g., `flake8`, `black`, or `ruff`) to enforce coding standards.
- **Test coverage reporting** (e.g., `coverage.py`) with thresholds to prevent decreases in coverage.
- **Performance or load testing** as separate jobs.
- **Continuous Deployment (CD)** steps to automatically deploy the backend after successful CI runs.

For this phase, the implemented CI pipeline already satisfies the goal of automatically verifying backend correctness on every change and is confirmed to be running successfully via GitHub Actions.
