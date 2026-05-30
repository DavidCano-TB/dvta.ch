@echo off
cd /d c:\dvdcoin
git add modules/exams/app_exams.py
git commit -m "fix: servir porras directamente desde app_exams sin depender del proxy bank"
git push
