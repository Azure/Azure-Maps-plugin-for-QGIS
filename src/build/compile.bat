@echo off
call "C:\Program Files\QGIS 3.22.5\bin\o4w_env.bat"

@echo on
pyrcc5 -o src\resources.py src\resources.qrc