import sys
import os
import subprocess
import shutil
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QProgressBar, QPushButton, QMessageBox, QCheckBox
)

class BuildWorker(QThread):
    progress_changed = pyqtSignal(int)
    status_changed   = pyqtSignal(str)
    finished_ok      = pyqtSignal()
    finished_err     = pyqtSignal(str)

    def __init__(self, add_shortcut=False, launch_after=False):
        super().__init__()
        self.add_shortcut = add_shortcut
        self.launch_after = launch_after

    def run(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        required = {
            os.path.join(project_root, 'src', 'arduino_backup_tool.py'): 'Script principal',
            os.path.join(project_root, 'avrdude', 'avrdude.exe'):       'avrdude.exe',
            os.path.join(project_root, 'avrdude', 'avrdude.conf'):     'avrdude.conf',
            os.path.join(project_root, 'assets', 'app.ico'):           "icône de l'application",
            os.path.join(project_root, 'assets', 'loader.gif'):        'GIF de chargement',
            os.path.join(project_root, 'tools', 'python_installer', 'python-3.13.3-amd64.exe'): 'Installeur Python'
        }

        missing = [label for path, label in required.items() if not os.path.exists(path)]
        if missing:
            self.status_changed.emit(f"❌ Fichiers manquants : {', '.join(missing)}")
            self.finished_err.emit(f"Manquant : {', '.join(missing)}")
            return

        try:
            os.makedirs(os.path.join(project_root, 'backup'), exist_ok=True)
            installer_path = os.path.join(project_root, 'tools', 'python_installer', 'python-3.11.5-amd64.exe')

            steps = [
                ("[1/7] Vérifier Python", ["python", "--version"]),
                ("[2/7] Installer Python si nécessaire", ["cmd", "/c",
                    f"where python >nul 2>&1 || start /wait \"\" \"{installer_path}\" "
                    "/quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0"
                ]),
                ("[3/7] Installer dépendances", [
                    "python", "-m", "pip", "install",
                    "pyqt5", "pyinstaller", "pyserial", "pywin32"
                ]),
                ("[4/7] Lancer PyInstaller", [
                    "python", "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
                    f"--icon={os.path.join(project_root, 'assets', 'app.ico')}",
                    "--name=ArduinoBackupTool",
                    "--hidden-import=serial.tools.list_ports",
                    f"--add-binary={os.path.join(project_root, 'avrdude','avrdude.exe')}:.",
                    f"--add-data={os.path.join(project_root, 'avrdude','avrdude.conf')}:.",
                    f"--add-data={os.path.join(project_root, 'assets','loader.gif')}:.",
                    f"--add-data={os.path.join(project_root, 'assets','app.ico')}:.",
                    os.path.join(project_root, 'src', 'arduino_backup_tool.py')
                ]),
                ("[5/7] Déplacer l'exécutable", ["python", "-c",
                    (
                        "import shutil, os; "
                        f"src = r'{os.path.join(project_root, 'dist', 'ArduinoBackupTool.exe')}'; "
                        f"dst = r'{project_root}'; "
                        "shutil.move(src, dst)"
                    )
                ]),
                ("[6/7] Nettoyer", ["cmd", "/c",
                    "if exist build rmdir /s /q build && "
                    "if exist dist  rmdir /s /q dist && "
                    "if exist __pycache__ rmdir /s /q __pycache__"
                ])
            ]

            if self.add_shortcut:
                shortcut_py = (
                    "import os, win32com.client; "
                    "desk = os.path.join(os.environ['USERPROFILE'], 'Desktop'); "
                    f"target = r'{os.path.join(project_root, 'ArduinoBackupTool.exe')}'; "
                    "shell = win32com.client.Dispatch('WScript.Shell'); "
                    "s = shell.CreateShortCut(os.path.join(desk, 'ArduinoBackupTool.lnk')); "
                    "s.TargetPath = target; s.WorkingDirectory = os.path.dirname(target); s.save()"
                )
                steps.append(("[7/7] Créer raccourci", ["python", "-c", shortcut_py]))

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

            total = len(steps)
            for idx, (label, cmd) in enumerate(steps, start=1):
                pct = int((idx - 1) * 100 / total)
                self.status_changed.emit(label)
                self.progress_changed.emit(pct)

                res = subprocess.run(
                    cmd,
                    cwd=project_root,
                    startupinfo=startupinfo,
                    creationflags=creationflags,
                    capture_output=True,
                    text=True
                )
                if res.returncode != 0:
                    raise RuntimeError(f"{label} a échoué :\n{res.stderr.strip()}")

            self.status_changed.emit("✅ Build terminé")
            self.progress_changed.emit(100)

            if self.launch_after:
                exe = os.path.join(project_root, 'ArduinoBackupTool.exe')
                subprocess.Popen(exe, shell=True)

            self.finished_ok.emit()

        except Exception as e:
            self.finished_err.emit(str(e))


class BuilderWindow(QWidget):
    def __init__(self):
        super().__init__()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        self.setWindowTitle("Build ArduinoBackupTool")
        self.setWindowIcon(QIcon(os.path.join(project_root, 'assets', 'app.ico')))
        self.setGeometry(300, 300, 500, 240)

        self.status_lbl  = QLabel("Prêt à builder")
        self.spinner_lbl = QLabel()
        self.spinner_lbl.setAlignment(Qt.AlignCenter)
        self.spinner     = QMovie(os.path.join(project_root, 'assets', 'loader.gif'))
        self.spinner_lbl.setMovie(self.spinner)
        self.spinner_lbl.setVisible(False)

        self.shortcut_chk = QCheckBox("Créer un raccourci sur le bureau")
        self.launch_chk   = QCheckBox("Lancer l'application après le build")

        self.progress     = QProgressBar()
        self.build_btn    = QPushButton("Lancer le build")
        self.build_btn.clicked.connect(self.start_build)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.spinner_lbl)
        layout.addWidget(self.shortcut_chk)
        layout.addWidget(self.launch_chk)
        layout.addWidget(self.progress)
        layout.addWidget(self.build_btn)

    def start_build(self):
        self.build_btn.setEnabled(False)
        self.spinner_lbl.setVisible(True)
        self.spinner.start()
        self.worker = BuildWorker(
            add_shortcut=self.shortcut_chk.isChecked(),
            launch_after=self.launch_chk.isChecked()
        )
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.status_changed.connect(self.status_lbl.setText)
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
        QMessageBox.critical(self, "Erreur", msg)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BuilderWindow()
    win.show()
    sys.exit(app.exec_())
