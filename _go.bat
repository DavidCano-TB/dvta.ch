@echo off
cd /d c:\dvdcoin
git add -A
git commit -m "feat: anuncios con fecha vencimiento, borrado para autor/admin, texto corregido" > c:\dvdcoin\_out.txt 2>&1
git push >> c:\dvdcoin\_out.txt 2>&1
echo DONE >> c:\dvdcoin\_out.txt
