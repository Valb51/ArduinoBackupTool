import sys
import os
import subprocess
import serial.tools.list_ports
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QComboBox, QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QGroupBox, QHBoxLayout, QLineEdit, QPlainTextEdit
)

class Worker(QThread):
    progress_changed = pyqtSignal(int)
    status_changed   = pyqtSignal(str)
    finished_ok      = pyqtSignal()
    finished_err     = pyqtSignal(str)

    def __init__(self, mode, params):
        super().__init__()
        self.mode   = mode
        self.params = params

    def run(self):
        try:
            tasks = []

            if self.mode == 'backup':
                base_dir = self.params['base_dir']
                now = datetime.now()
                prefix = f"abt_{now.strftime('%B').lower()}{now.day}"
                existing = [d for d in os.listdir(base_dir) if d.startswith(prefix)]
                letter = chr(ord('a') + len(existing))
                backup_dir = os.path.join(base_dir, f"{prefix}{letter}")
                os.makedirs(backup_dir, exist_ok=True)

                for name, ext in [('flash','hex'), ('eeprom','eep')]:
                    out = os.path.join(backup_dir, f"{name}.{ext}")
                    cmd = [
                        self.params['avrdude_path'], '-C', self.params['avrdude_conf_path'],
                        '-p', self.params['mcu'], '-c', self.params['prog'],
                        '-P', self.params['port'], '-b', self.params['baud'],
                        '-U', f"{name}:r:{out}:i"
                    ]
                    tasks.append((f"Read {name}", cmd))

                for fuse in ['lfuse','hfuse','efuse']:
                    out = os.path.join(backup_dir, f"{fuse}.txt")
                    cmd = [
                        self.params['avrdude_path'], '-C', self.params['avrdude_conf_path'],
                        '-p', self.params['mcu'], '-c', self.params['prog'],
                        '-P', self.params['port'], '-b', self.params['baud'],
                        '-U', f"{fuse}:r:{out}:h"
                    ]
                    tasks.append((f"Read {fuse}", cmd))

            else:
                base_dir = self.params['base_dir']
                for name, ext in [('flash','hex'), ('eeprom','eep')]:
                    inp = os.path.join(base_dir, f"{name}.{ext}")
                    cmd = [
                        self.params['avrdude_path'], '-C', self.params['avrdude_conf_path'],
                        '-p', self.params['mcu'], '-c', self.params['prog'],
                        '-P', self.params['port'], '-b', self.params['baud'],
                        '-U', f"{name}:w:{inp}:i"
                    ]
                    tasks.append((f"Write {name}", cmd))

                for fuse in ['lfuse','hfuse','efuse']:
                    fname = os.path.join(base_dir, f"{fuse}.txt")
                    with open(fname, 'r') as f:
                        val = f.read().strip()
                    cmd = [
                        self.params['avrdude_path'], '-C', self.params['avrdude_conf_path'],
                        '-p', self.params['mcu'], '-c', self.params['prog'],
                        '-P', self.params['port'], '-b', self.params['baud'],
                        '-U', f"{fuse}:w:{val}:m"
                    ]
                    tasks.append((f"Write {fuse}", cmd))

            total = len(tasks)
            for idx, (label, cmd) in enumerate(tasks, start=1):
                pct = int((idx-1) * 100 / total)
                self.status_changed.emit(label)
                self.progress_changed.emit(pct)

                startupinfo = None
                creationflags = 0
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    creationflags = subprocess.CREATE_NO_WINDOW

                proc = subprocess.run(
                    cmd,
                    capture_output=True, text=True,
                    startupinfo=startupinfo, creationflags=creationflags
                )
                if proc.returncode != 0:
                    raise RuntimeError(f"{label} failed:\n{proc.stderr}")

            self.status_changed.emit("Done")
            self.progress_changed.emit(100)
            self.finished_ok.emit()

        except Exception as e:
            self.finished_err.emit(str(e))


class ArduinoBackupTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Backup Tool")
        self.setGeometry(100, 100, 600, 600)
        self.base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        self.setWindowIcon(QIcon(os.path.join(self.base_path, "app.ico")))

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()

        self.default_avrdude_path      = os.path.join(base_path, 'avrdude.exe')
        self.default_avrdude_conf_path = os.path.join(base_path, 'avrdude.conf')
        self.avrdude_path      = self.default_avrdude_path
        self.avrdude_conf_path = self.default_avrdude_conf_path

        self.init_ui()
        self.detect_serial_ports()

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Config
        cfg = QGroupBox("AVRDude Config")
        cfg_l = QVBoxLayout()
        for label, attr, filt in [
            ("avrdude.exe:", 'avrdude_path', "Executable (*.exe)"),
            ("avrdude.conf:", 'avrdude_conf_path', "Config (*.conf)")
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            edit = QLineEdit(getattr(self, attr))
            setattr(self, f"{attr}_edit", edit)
            row.addWidget(edit)
            b1 = QPushButton("Browse...")
            b1.clicked.connect(lambda _, a=attr, f=filt: self.browse_file(a, f))
            row.addWidget(b1)
            b2 = QPushButton("Reset")
            b2.clicked.connect(lambda _, a=attr: self.reset_path(a))
            row.addWidget(b2)
            cfg_l.addLayout(row)
        cfg.setLayout(cfg_l)
        layout.addWidget(cfg)

        # Board Settings
        bd = QGroupBox("Board Settings")
        bd_l = QVBoxLayout()
        # Port
        r = QHBoxLayout()
        r.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        r.addWidget(self.port_combo)
        rb = QPushButton("Refresh")
        rb.clicked.connect(self.detect_serial_ports)
        r.addWidget(rb)
        bd_l.addLayout(r)
        # MCU
        r = QHBoxLayout()
        r.addWidget(QLabel("MCU:"))
        self.mcu = QComboBox()
        self.mcu.addItems([
            "atmega328p", "atmega168", "atmega2560", "attiny85",
            "atmega32u4", "atmega1280", "attiny13", "atmega8"
        ])
        r.addWidget(self.mcu)
        bd_l.addLayout(r)
        # Baud
        r = QHBoxLayout()
        r.addWidget(QLabel("Baud:"))
        self.baud = QComboBox()
        self.baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud.setCurrentText("57600")
        r.addWidget(self.baud)
        bd_l.addLayout(r)
        # Programmer
        r = QHBoxLayout()
        r.addWidget(QLabel("Programmer:"))
        self.prog = QComboBox()
        self.prog.addItems([
            "arduino", "usbtiny", "avrisp", "usbasp",
            "stk500v1", "stk500v2", "wiring"
        ])
        r.addWidget(self.prog)
        bd_l.addLayout(r)
        # Auto-detect button
        autodetect_btn = QPushButton("Auto-détecter")
        autodetect_btn.clicked.connect(self.autodetect_board)
        bd_l.addWidget(autodetect_btn)

        bd.setLayout(bd_l)
        layout.addWidget(bd)

        # Status & Progress
        self.status_lbl  = QLabel("Ready")
        self.progress    = QProgressBar()
        self.progress.setValue(0)
        self.spinner_lbl = QLabel()
        self.spinner_lbl.setAlignment(Qt.AlignCenter)
        self.spinner_lbl.setVisible(False)
        self.spinner     = QMovie(os.path.join(self.base_path, "loader.gif"))
        self.spinner_lbl.setMovie(self.spinner)

        layout.addWidget(self.status_lbl)
        layout.addWidget(self.progress)
        layout.addWidget(self.spinner_lbl)

        # Actions
        act = QGroupBox("Actions")
        al = QHBoxLayout()
        bkup = QPushButton("Backup All")
        bkup.clicked.connect(self.start_backup)
        rst  = QPushButton("Restore All")
        rst.clicked.connect(self.start_restore)
        al.addWidget(bkup)
        al.addWidget(rst)
        act.setLayout(al)
        layout.addWidget(act)

        # Console
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def autodetect_board(self):
        port = self.port_combo.currentText()
        if not port:
            self.log("Aucun port COM sélectionné.")
            return

        self.log(f"🔍 Auto-détection sur {port}...")

        test_list = [
            ("atmega328p", "arduino", "115200"),  # priorité
            ("atmega328p", "arduino", "57600"),
            ("atmega328p", "wiring", "57600"),
            ("atmega2560", "arduino", "115200"),
            ("atmega2560", "stk500v1", "57600"),
        ]

        for mcu, prog, baud in test_list:
            cmd = [
                self.avrdude_path, "-C", self.avrdude_conf_path,
                "-v", "-p", mcu, "-c", prog, "-P", port, "-b", baud
            ]
            self.log(f"➡️ Test : MCU={mcu}, Baud={baud}, Prog={prog}")
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                output = proc.stdout + proc.stderr
                if "Device signature" in output:
                    self.log(f"✅ Détection réussie : {mcu}, {baud}, {prog}")
                    self.mcu.setCurrentText(mcu)
                    self.baud.setCurrentText(baud)
                    self.prog.setCurrentText(prog)
                    return
                else:
                    self.log("⚠️ Pas de signature détectée.")
                    self.log("…stdout:\n" + proc.stdout)
                    self.log("…stderr:\n" + proc.stderr)
            except subprocess.TimeoutExpired:
                self.log("⏳ Temps dépassé pour cette combinaison.")
            except Exception as e:
                self.log(f"❌ Erreur : {e}")

        self.log("❌ Aucune combinaison valide détectée.")

    def browse_file(self, attr, filt):
        p, _ = QFileDialog.getOpenFileName(self, f"Select {attr}", "", filt)
        if p:
            setattr(self, attr, p)
            getattr(self, f"{attr}_edit").setText(p)

    def reset_path(self, attr):
        default = getattr(self, f"default_{attr}")
        setattr(self, attr, default)
        getattr(self, f"{attr}_edit").setText(default)
        self.log(f"{attr} reset to default.")

    def log(self, txt):
        self.console.appendPlainText(txt)

    def detect_serial_ports(self):
        self.port_combo.clear()
        try:
            ports = [p.device for p in serial.tools.list_ports.comports()]
        except Exception as e:
            self.log(f"pyserial error: {e}")
            ports = []
        self.port_combo.addItems(ports)
        self.log(f"Detected ports: {ports}")

    def start_backup(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location", os.path.abspath("backup"))
        if folder:
            self.run_worker('backup', folder)

    def start_restore(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder", os.path.abspath("backup"))
        if folder:
            self.run_worker('restore', folder)

    def run_worker(self, mode, folder):
        for w in self.findChildren(QPushButton):
            w.setEnabled(False)
        self.spinner_lbl.setVisible(True)
        self.spinner.start()
        params = {
            'avrdude_path': self.avrdude_path,
            'avrdude_conf_path': self.avrdude_conf_path,
            'mcu': self.mcu.currentText(),
            'prog': self.prog.currentText(),
            'port': self.port_combo.currentText(),
            'baud': self.baud.currentText(),
            'base_dir': folder
        }
        self.worker = Worker(mode, params)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.status_changed.connect(lambda s: (self.status_lbl.setText(s), self.log(s)))
        self.worker.finished_ok.connect(self.on_finished_ok)
        self.worker.finished_err.connect(self.on_finished_err)
        self.worker.start()

    def on_finished_ok(self):
        self.spinner.stop()
        self.spinner_lbl.setVisible(False)
        self.log("Operation successful.")
        QMessageBox.information(self, "OK", "Operation completed.")
        self.reset_ui()

    def on_finished_err(self, err):
        self.spinner.stop()
        self.spinner_lbl.setVisible(False)
        self.log(f"Error: {err}")
        QMessageBox.critical(self, "Error", err)
        self.reset_ui()

    def reset_ui(self):
        for w in self.findChildren(QPushButton):
            w.setEnabled(True)
        self.status_lbl.setText("Ready")
        self.progress.setValue(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ArduinoBackupTool()
    win.show()
    sys.exit(app.exec_())
