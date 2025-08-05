# Pretty-Python-Patterns

## Python Setup
Create a python 3.10 virtual environment in this directory called .venv using this command in the command line: "C:\Program Files\Python310\python.exe" -m venv .venv

Activate the virtual environment with the command: activate while in the .venv/Scripts directory, or by selecting the python.exe in the Lib directory of the .venv using Visual Studio Code and then activating by creating a new cmd terminal

Install the required module from the requirements document using the command:
pip install -r requirements.txt

When changing modules, use the command:
pip freeze > requirements.txt
to make a new requirements document.

To make an executable
pyinstaller -y -w -n "Project Name" --add-data _internal/*;. main.py
