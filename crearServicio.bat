@echo off
SCHTASKS /Create /TN "MonitorDB" /TR "pythonw.exe 'C:\ServicioMonitor\pythonSqlServer.py'" /SC minute /MO 30 /RU System