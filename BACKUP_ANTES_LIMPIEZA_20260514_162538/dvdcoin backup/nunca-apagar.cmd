:: ── 1. Nunca apagar/hibernar/suspender ──────────────────────────────────
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0
powercfg /change disk-timeout-ac 0
powercfg /change disk-timeout-dc 0
powercfg /h off

:: ── 2. Al cerrar la tapa: no hacer nada (ni con cable ni con batería) ───
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_BUTTONS LIDACTION 0

:: ── 3. Al pulsar el botón de encendido: no hacer nada ──────────────────
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_BUTTONS PBUTTONACTION 0
powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_BUTTONS PBUTTONACTION 0

:: ── 4. Aplicar cambios ──────────────────────────────────────────────────
powercfg /S SCHEME_CURRENT

:: ── 5. Desactivar el bloqueo automático de pantalla ────────────────────
reg add "HKCU\Control Panel\Desktop" /v ScreenSaveActive /t REG_SZ /d 0 /f
reg add "HKCU\Control Panel\Desktop" /v ScreenSaverIsSecure /t REG_SZ /d 0 /f
reg add "HKCU\SOFTWARE\Policies\Microsoft\Windows\Personalization" /v NoLockScreen /t REG_DWORD /d 1 /f

:: ── 6. Desactivar el inicio de sesión requerido al volver del reposo ───
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_NONE CONSOLELOCK 0
powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_NONE CONSOLELOCK 0
powercfg /S SCHEME_CURRENT

echo.
echo ✓ Configuracion completada. El PC no se apagara, suspendera ni bloqueara.
pauseCómo usarlo:

:: ── Para revertirlo en cualquier momento, ejecuta como admin:
:: ──cmdpowercfg /restoredefaultschemes