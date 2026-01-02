#!/bin/bash
#Active virtual environment
source ./.venv/bin/activate

#Start on CPU core 6
#taskset -c 6 python main.py

#Just launch on whatever cores
python main.py
deactivate