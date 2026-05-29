@echo off
cd /d c:\dvdcoin\static
if exist cuentos (
    if not exist anuncios (
        rename cuentos anuncios
        echo RENAMED cuentos to anuncios
    ) else (
        echo anuncios already exists, copying contents
        xcopy /E /Y cuentos\* anuncios\
        echo COPIED
    )
) else (
    if not exist anuncios (
        mkdir anuncios
        echo CREATED anuncios
    ) else (
        echo anuncios already exists
    )
)
