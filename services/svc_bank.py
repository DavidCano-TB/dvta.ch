"""Windows Service wrapper for DVDcoin Bank Principal (port 8000)"""
import os, sys, subprocess, time
import win32serviceutil, win32service, win32event, servicemanager

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class DVDcoinBankService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DVDcoin-Bank"
    _svc_display_name_ = "DVDcoin Bank Principal"
    _svc_description_ = "Servidor principal del Bank DVDcoin (puerto 8000) - main.py"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.proc = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.proc:
            self.proc.terminate()
            try: self.proc.wait(timeout=10)
            except: self.proc.kill()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self._run()

    def _run(self):
        while True:
            if win32event.WaitForSingleObject(self.stop_event, 0) == win32event.WAIT_OBJECT_0:
                break
            try:
                self.proc = subprocess.Popen(
                    [sys.executable, os.path.join(_DIR, "main.py")],
                    cwd=_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                while self.proc.poll() is None:
                    if win32event.WaitForSingleObject(self.stop_event, 2000) == win32event.WAIT_OBJECT_0:
                        self.proc.terminate()
                        return
                servicemanager.LogErrorMsg(f"{self._svc_name_}: process exited, restarting in 5s")
                time.sleep(5)
            except Exception as e:
                servicemanager.LogErrorMsg(f"{self._svc_name_}: {e}")
                time.sleep(10)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DVDcoinBankService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DVDcoinBankService)
