@echo off
call conda activate cnn
pip install -r requirements.txt
python clock.py
pause