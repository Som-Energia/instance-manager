# Instance-manager

OpenERP server instance manager.

## Python version

Python 3.11

## Installation and run

1. Install Python 3.11 version
2. Setup Poetry in the project directory

    ```
    poetry env use <python-path>
    poetry install
    ```

3. Start application

    ```
    poetry run uvicorn gestor.main:app --reload
    ```

*Do not use `--reload` flag in production.*
