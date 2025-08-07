@echo off
cd /d "%~dp0"

echo === Installing required Python packages ===
python -m pip install --upgrade pip
python -m pip install flask comtypes pycaw psutil keyboard pywebview

echo === Starting server.py ===
python server.py
clr
stop
