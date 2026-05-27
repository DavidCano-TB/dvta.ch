@echo off
:: ============================================================
:: activar_dvdch.bat
:: Redirige dvd.ch → localhost:8000 en ESTE ordenador
:: Requiere ejecutar como Administrador
:: ============================================================

:: Comprobar que se ejecuta como Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Debes ejecutar este archivo como Administrador.
    echo  Haz clic derecho sobre el .bat y elige "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

echo.
echo  [1/4] Añadiendo dvd.ch al archivo hosts...

:: Comprobar si ya existe la entrada
findstr /C:"dvd.ch" "%SystemRoot%\System32\drivers\etc\hosts" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Ya existe la entrada dvd.ch en hosts. Saltando.
) else (
    echo 127.0.0.1    dvd.ch >> "%SystemRoot%\System32\drivers\etc\hosts"
    echo       Entrada añadida correctamente.
)

echo.
echo  [2/4] Descargando netsh proxy helper (si no existe)...

:: Crear el script de proxy Python en C:\DvDcoin\proxy_dvdch.py
set PROXY_FILE=C:\DvDcoin\proxy_dvdch.py
if not exist "%PROXY_FILE%" (
    (
        echo import http.server, urllib.request, urllib.error, sys
        echo TARGET = "http://localhost:8000"
        echo.
        echo class Proxy^(http.server.BaseHTTPRequestHandler^):
        echo     def do_GET^(self^): self._proxy^(^)
        echo     def do_POST^(self^): self._proxy^(^)
        echo     def do_HEAD^(self^): self._proxy^(^)
        echo     def log_message^(self, *a^): pass
        echo     def _proxy^(self^):
        echo         url = TARGET + self.path
        echo         try:
        echo             length = int^(self.headers.get^('Content-Length', 0^)^)
        echo             body = self.rfile.read^(length^) if length else None
        echo             req = urllib.request.Request^(url, data=body, method=self.command^)
        echo             for k,v in self.headers.items^(^):
        echo                 if k.lower^(^) not in ^('host','content-length'^): req.add_header^(k,v^)
        echo             with urllib.request.urlopen^(req, timeout=30^) as r:
        echo                 self.send_response^(r.status^)
        echo                 for k,v in r.headers.items^(^): self.send_header^(k,v^)
        echo                 self.end_headers^(^)
        echo                 self.wfile.write^(r.read^(^)^)
        echo         except Exception as e:
        echo             self.send_error^(502, str^(e^)^)
        echo.
        echo if __name__ == '__main__':
        echo     print^("Proxy dvd.ch:80 → localhost:8000 activo"^)
        echo     http.server.HTTPServer^(^('', 80^), Proxy^).serve_forever^(^)
    ) > "%PROXY_FILE%"
    echo       Proxy script creado en %PROXY_FILE%
) else (
    echo       Proxy script ya existe. Saltando.
)

echo.
echo  [3/4] Creando regla de firewall para puerto 80...
netsh advfirewall firewall show rule name="DVDcoin proxy 80" >nul 2>&1
if %errorlevel% neq 0 (
    netsh advfirewall firewall add rule name="DVDcoin proxy 80" dir=in action=allow protocol=TCP localport=80 >nul
    echo       Regla de firewall añadida.
) else (
    echo       Regla de firewall ya existe. Saltando.
)

echo.
echo  [4/4] Iniciando proxy en segundo plano...

:: Matar proxy previo si existe
taskkill /f /fi "WINDOWTITLE eq DVDcoin-proxy" >nul 2>&1

:: Lanzar el proxy en una ventana minimizada
start "DVDcoin-proxy" /min python "%PROXY_FILE%"

echo       Proxy iniciado.
echo.
echo  ============================================================
echo   OK  Abre tu navegador y escribe:  dvd.ch
echo       Se cargara DVDcoin Bank directamente.
echo.
echo   NOTA: Solo funciona en ESTE ordenador.
echo         Los demas miembros siguen usando la URL de ngrok.
echo  ============================================================
echo.
pause
