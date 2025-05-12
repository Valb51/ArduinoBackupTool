import sys
import os
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QProgressBar, QPushButton, QMessageBox, QCheckBox
)

class BuildWorker(QThread):
    progress_changed = pyqtSignal(int)
    status_changed = pyqtSignal(str)
    finished_ok = pyqtSignal()
    finished_err = pyqtSignal(str)

    def __init__(self, add_shortcut=False, launch_after=False):
        super().__init__()
        self.add_shortcut = add_shortcut
        self.launch_after = launch_after

    def run(self):
        try:
            os.makedirs(os.path.abspath("../backup"), exist_ok=True)

            steps = [
                ("[1/8] Change to script folder", ["cmd", "/c", "cd /d", os.getcwd()]),
                ("[2/8] Check Python", ["python", "--version"]),
                ("[3/8] Install Python deps", ["pip", "install", "pyqt5", "pyinstaller", "pyserial", "pywin32"]),
                ("[4/8] Check avrdude files", ["cmd", "/c", "if not exist ../avrdude/avrdude.exe exit 1"]),
                ("[5/8] Run PyInstaller", [
                    "pyinstaller", "--noconfirm", "--onefile", "--windowed",
                    "--icon=../assets/app.ico",
                    "--name", "ArduinoBackupTool",
                    "--hidden-import", "serial.tools.list_ports",
                    "--add-binary", "../avrdude/avrdude.exe;.",
                    "--add-data", "../avrdude/avrdude.conf;.",
                    "--add-data", "../assets/loader.gif;.",
                    "--add-data", "../assets/app.ico;.",
                    "../src/arduino_backup_tool.py"
                ]),
                ("[6/8] Move EXE to root", ["cmd", "/c", "move /y dist\ArduinoBackupTool.exe .."]),
                ("[7/8] Cleanup", ["cmd", "/c", "if exist build rmdir /s /q build && if exist dist rmdir /s /q dist && if exist __pycache__ rmdir /s /q __pycache__"])
            ]

            if self.add_shortcut:
                steps.append(("[8] Créer le raccourci sur le bureau", [
                    "python", "-c",
                    (
                        "import os, win32com.client; "
                        "desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop'); "
                        "target = os.path.abspath('../ArduinoBackupTool.exe'); "
                        "shortcut = os.path.join(desktop, 'ArduinoBackupTool.lnk'); "
                        "shell = win32com.client.Dispatch('WScript.Shell'); "
                        "s = shell.CreateShortCut(shortcut); s.TargetPath = target; "
                        "s.WorkingDirectory = os.path.dirname(target); s.save()"
                    )
                ]))

            if self.launch_after:
                steps.append(("[9] Lancer l'application", ["cmd", "/c", "start "" ..\ArduinoBackupTool.exe"]))

            total = len(steps)
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW

            for idx, (label, cmd) in enumerate(steps, start=1):
                pct = int((idx - 1) * 100 / total)
                self.status_changed.emit(label)
                self.progress_changed.emit(pct)

                res = subprocess.run(cmd, capture_output=True, text=True,
                                     startupinfo=startupinfo, creationflags=creationflags)
                if res.returncode != 0:
                    raise RuntimeError(f"{label} failed:\n{res.stderr.strip()}")

            self.status_changed.emit("Build terminé")
            self.progress_changed.emit(100)
            self.finished_ok.emit()

        except Exception as e:
            self.finished_err.emit(str(e))

class BuilderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Build ArduinoBackupTool")
        self.setWindowIcon(QIcon("../assets/app.ico"))
        self.setGeometry(300, 300, 480, 240)

        self.status_lbl = QLabel("Prêt à builder")
        self.spinner_lbl = QLabel()
        self.spinner_lbl.setAlignment(Qt.AlignCenter)
        self.spinner = QMovie("../assets/loader.gif")
        self.spinner_lbl.setMovie(self.spinner)
        self.spinner_lbl.setVisible(False)

        self.shortcut_chk = QCheckBox("Créer un raccourci sur le bureau")
        self.launch_chk = QCheckBox("Lancer l'application après le build")

        self.progress = QProgressBar()
        self.build_btn = QPushButton("Lancer le build")
        self.build_btn.clicked.connect(self.start_build)

        vbox = QVBoxLayout()
        vbox.addWidget(self.status_lbl)
        vbox.addWidget(self.spinner_lbl)
        vbox.addWidget(self.shortcut_chk)
        vbox.addWidget(self.launch_chk)
        vbox.addWidget(self.progress)
        vbox.addWidget(self.build_btn)
        self.setLayout(vbox)

    def start_build(self):
        self.build_btn.setEnabled(False)
        self.spinner_lbl.setVisible(True)
        self.spinner.start()
        self.worker = BuildWorker(
            add_shortcut=self.shortcut_chk.isChecked(),
            launch_after=self.launch_chk.isChecked()
        )
        self.worker.status_changed.connect(self.status_lbl.setText)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.finished_ok.connect(self.on_success)
        self.worker.finished_err.connect(self.on_error)
        self.worker.start()

    def on_success(self):
        self.spinner.stop()
        self.spinner_lbl.setVisible(False)
        QMessageBox.information(self, "Succès", "Build réussi !")
        self.close()

    def on_error(self, msg):
        self.spinner.stop()
        self.spinner_lbl.setVisible(False)
        QMessageBox.critical(self, "Erreur", f"Build échoué :\n{msg}")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BuilderWindow()
    win.show()
    sys.exit(app.exec_())