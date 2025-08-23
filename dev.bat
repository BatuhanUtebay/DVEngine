@echo off
REM Development commands for DVGE - Windows batch version

if "%1"=="install" (
    pip install -r requirements.txt
    goto :eof
)

if "%1"=="dev-install" (
    pip install -r requirements.txt
    pip install pre-commit isort
    pre-commit install
    goto :eof
)

if "%1"=="setup-hooks" (
    pre-commit install
    pre-commit autoupdate
    goto :eof
)

if "%1"=="test" (
    python -m pytest tests/ -v
    goto :eof
)

if "%1"=="test-cov" (
    python -m pytest tests/ -v --cov=dvge --cov-report=html --cov-report=term
    goto :eof
)

if "%1"=="lint" (
    flake8 dvge\ tests\
    mypy dvge\
    goto :eof
)

if "%1"=="format" (
    black dvge\ tests\
    isort dvge\ tests\
    goto :eof
)

if "%1"=="quality" (
    call %0 format
    call %0 lint
    call %0 test
    goto :eof
)

if "%1"=="clean" (
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    del /s /q *.pyc 2>nul
    if exist .pytest_cache rmdir /s /q .pytest_cache
    if exist htmlcov rmdir /s /q htmlcov
    if exist .mypy_cache rmdir /s /q .mypy_cache
    if exist .coverage del .coverage
    goto :eof
)

if "%1"=="run" (
    python main.py
    goto :eof
)

echo Available commands:
echo   install      - Install runtime dependencies
echo   dev-install  - Install development dependencies
echo   setup-hooks  - Setup pre-commit hooks
echo   test         - Run tests
echo   test-cov     - Run tests with coverage
echo   lint         - Run linters
echo   format       - Format code with black and isort
echo   quality      - Run all quality checks
echo   clean        - Clean build artifacts
echo   run          - Run the application