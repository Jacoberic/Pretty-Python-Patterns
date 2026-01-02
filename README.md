# Setup Python
## Download python
Download python312 from https://www.python.org/downloads/.

## Create a virtual environment
Create a python 3.12 virtual environment in this directory called .venv using this command in the command line:
### Windows
"c:\\Program Files\\Python312\\python" -m venv .venv

### Linux
python3 -m venv .venv

Activate the virtual environment with the command: activate while in the .venv/Scripts directory, or by selecting the python.exe in the Lib directory of the .venv using Visual Studio Code and then activating by creating a new cmd terminal

### Install requirements
pip install -r requirements.txt

### To save requirements
pip freeze > requirements.txt

## Create Executable
pyinstaller -y -w -n "Project Name" --add-data _internal/*;. main.py