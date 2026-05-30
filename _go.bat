@echo off
cd /d c:\dvdcoin
del _fix_porras.py 2>nul
git add -A
git commit -m "fix: total votos en porras usa backend - participantes unicos reales"
git push
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
start "" /min cmd /c "cd /d c:\dvdcoin && python main.py"
timeout /t 3 /nobreak >nul
start "" /min cmd /c "cd /d c:\dvdcoin\modules\exams && python app_exams.py"
echo DONE
