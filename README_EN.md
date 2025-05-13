[![Download](https://img.shields.io/github/v/release/Valb51/ArduinoBackupTool?label=Download%20Latest)](https://github.com/Valb51/ArduinoBackupTool/releases/latest)

# Arduino Backup Tool v1.1.2

**Arduino Backup Tool** is a lightweight graphical application (PyQt5) for **backing up** and **restoring** the firmware (flash, EEPROM) and **fuses** (lfuse, hfuse, efuse) of Arduino boards compatible with `avrdude`.

---

## 🆕 What's New in v1.1.2

- Updated Python installer path in `build_gui.py` script.
- Improved auto-detection of COM port, MCU, programmer, and baud rate.
- Automatic cleanup of `build/`, `dist/`, and `__pycache__/` folders.
- Added convenience options: create desktop shortcut, auto-launch after build.
- Various minor fixes and stability improvements.

---

## ⚠️ Limitations & Compatibility

- **Unsupported boards**: **Arduino Leonardo** (and other ATmega32u4-based) boards are not recognized reliably via `avrdude`.  
  👉 These boards reset their COM port on open, preventing stable communication with the programmer.

- **Supported boards**: Uno, Nano, Mega, Pro Mini, ATmega328P, ATmega2560, etc.

---

## 🧰 Manual Driver Installation

Drivers are **no longer installed automatically**. Please install manually if needed:

- **CH340** (common on many Arduino clones)  
  📥 [Download CH340 driver](https://sparks.gogo.co.nz/assets/_site/ch340.zip)

- **FTDI** (for original boards or clones with FT232RL)  
  📥 [Download FTDI driver](https://www.ftdichip.com/Drivers/VCP.htm)

- **Zadig** (for USBasp or USBtinyISP programmers)  
  📥 [Download Zadig](https://zadig.akeo.ie/)

---

## 📦 Prerequisites

- Windows 10/11 (x64)
- Python 3.7+ (auto-installable if missing)
- Bundled `avrdude` (no manual install required)
- Python modules: `PyQt5`, `pyserial`, `pywin32`, `pyinstaller`

---

## 🚀 Download

📥 **Windows Version (portable, no installer)**  
👉 [Download ArduinoBackupTool.exe](./dist/ArduinoBackupTool.exe)

---

## ▶️ Usage

1. **Launch** the `ArduinoBackupTool.exe` executable.
2. In the **AVRDude Configuration** tab, verify or adjust paths to `avrdude.exe` and `avrdude.conf`.
3. In the **Board Settings** tab:
    - Select or **Auto-detect** COM port, MCU, programmer, and baud rate.
4. Click on:
    - **Backup All**: to back up flash memory, EEPROM, and fuses
    - **Restore All**: to restore from a full backup
5. Follow the **progress bar** and **status messages**.

---

## 📁 Project Structure

/
├─ avrdude/
│ ├─ avrdude.exe
│ └─ avrdude.conf
├─ assets/
│ ├─ app.ico
│ └─ loader.gif
├─ src/
│ └─ arduino_backup_tool.py
├─ build_gui.py
├─ dist/
│ └─ ArduinoBackupTool.exe
├─ tools/
│ ├─ CH340/
│ ├─ FTDI/
│ └─ Zadig/

---

## 📄 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for more details.

---

## 🤝 Contribution

Feedback, suggestions, and fixes are welcome:
- Report bugs or requests via **issues**
- Create a feature branch via Git, then open a **pull request**

---

**Developed with ❤️ to simplify Arduino firmware management.**
