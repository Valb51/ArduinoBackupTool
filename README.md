[![Download](https://img.shields.io/github/v/release/Valb51/ArduinoBackupTool?label=Download%20Latest)](https://github.com/Valb51/ArduinoBackupTool/releases/latest)


## 📦 Arduino Backup Tool

**Arduino Backup Tool** is a graphical utility designed to **extract** and **restore** the firmware (`.hex`) and EEPROM (`.eep`) memory from Arduino boards (like the Nano or Uno) using **AVRDUDE**.  

This tool is ideal for **creating backups** of an already programmed Arduino board or **cloning its firmware** to other devices. It is especially useful when the original source code or project file is **unavailable**.

---

### 🧠 Why Backup Instead of Reverse Engineering?

Arduino compilers (like the Arduino IDE) translate human-readable C/C++ source code into machine code stored in the board as a `.hex` file. This file:
- **Cannot be converted back** to the original source code,
- **Loses all comments, variable names, and structure**,
- Is meant solely for execution by the microcontroller.

Therefore, this tool does **not retrieve your sketches or source code**, but only the **compiled binary** (the firmware running on the device), which can be:
- Used to **replicate** the behavior of the board,
- **Restored** in case of memory corruption or reprogramming,
- Shared to flash other identical boards (useful in production or maintenance).


# 📦 Arduino Backup Tool

A simple and intuitive graphical tool to **backup and restore** the firmware (.hex) and EEPROM of Arduino boards using **AVRDUDE**, with a graphical build interface and automatic packaging.

---

## 🇫🇷 Description (French)

Un outil graphique simple et intuitif permettant de sauvegarder et restaurer le firmware (.hex) et la mémoire EEPROM de cartes Arduino (comme la Nano) via **AVRDUDE**, avec options de compilation automatique.

### 🧰 Fonctionnalités
- Interface graphique en **PyQt5**
- Sauvegarde et restauration :
  - Firmware `.hex`
  - EEPROM `.eep`
- Détection automatique des ports COM
- Compilation avec **PyInstaller**
- Création automatique du dossier `backup/`
- Interface de build :
  - ✅ Option de raccourci sur le bureau
  - 🚀 Option de lancement immédiat après build
- Aucune console noire affichée

---

## 🇬🇧 Features (English)

- GUI built with **PyQt5**
- Backup and restore:
  - `.hex` firmware
  - `.eep` EEPROM
- Auto-detection of serial COM ports
- Single `.exe` build with **PyInstaller**
- Auto-creation of `backup/` folder
- Build GUI includes:
  - ✅ Option to create desktop shortcut
  - 🚀 Option to launch the app right after build
- No console window (silent build)

---

## 🗂 Project Structure

```
ArduinoBackupTool/
├── assets/                  # Icons and loading GIF
├── avrdude/                # avrdude.exe + config
├── src/                    # Main Python tool
├── tools/                  # Build GUI
├── build.bat               # Launches the build GUI
├── backup/                 # Auto-generated backup folder
└── README.md
```

---

## ▶️ How to Use

1. Launch `ArduinoBackupTool.exe`
2. Choose:
   - COM port
   - MCU type
   - Programmer (`arduino` default)
3. Click:
   - **Backup** → extracts `.hex` and `.eep`
   - **Restore** → flashes the saved files

---

## ⚙️ Build Instructions

> Requires Python 3 + pip

1. Double-click `build.bat`
2. Choose options:
   - Create desktop shortcut
   - Launch app after build
3. Wait until done → `ArduinoBackupTool.exe` is created

---

## ✅ Dependencies

```bash
pip install pyqt5 pyserial pyinstaller pywin32
```

---

## 💡 Future Ideas

- Cross-platform support
- Multilingual UI
- Auto-detect Arduino port
- Verify `.hex` integrity after backup