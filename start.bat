@echo off
call conda activate base
pip install -r requirements.txt
python clock.py
pause