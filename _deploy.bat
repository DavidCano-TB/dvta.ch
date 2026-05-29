@echo off
cd /d c:\dvdcoin
git add -A
git status --short > c:\dvdcoin\_deploy_out.txt 2>&1
git commit -m "deploy: sync all pending changes" >> c:\dvdcoin\_deploy_out.txt 2>&1
git push >> c:\dvdcoin\_deploy_out.txt 2>&1
echo DONE >> c:\dvdcoin\_deploy_out.txt
