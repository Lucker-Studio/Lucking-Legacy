@echo off
pipenv run pyinstaller Lucking.spec
move /y dist\Lucking.exe .
rd /s /q __pycache__
rd /s /q build
rd /s /q dist
start Lucking.exe