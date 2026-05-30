@echo off
cd /d c:\dvdcoin
git add -A
git commit -m "feat: admin panel exams + fix porras servidas directamente"
git push
echo %ERRORLEVEL% > c:\dvdcoin\_final_result.txt
git log --oneline -1 >> c:\dvdcoin\_final_result.txt
