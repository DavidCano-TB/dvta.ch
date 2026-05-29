@echo off
cd /d c:\dvdcoin
git status --short > c:\dvdcoin\_status.txt 2>&1
git log --oneline -5 >> c:\dvdcoin\_status.txt 2>&1
