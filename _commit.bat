@echo off
cd /d c:\dvdcoin
git add -A
git commit -m "feat: renombrar cuentos a anuncios, permitir subir/borrar a todos los miembros"
git push
echo DONE > c:\dvdcoin\_commit_result.txt
