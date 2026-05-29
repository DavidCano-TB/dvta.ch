@echo off
cd /d c:\dvdcoin
git add -A
git commit -m "fix: asegurar hub con botones Bank y Exams visibles" > c:\dvdcoin\_push_result.txt 2>&1
git push >> c:\dvdcoin\_push_result.txt 2>&1
echo DONE >> c:\dvdcoin\_push_result.txt
