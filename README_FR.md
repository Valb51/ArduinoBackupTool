[![Download](https://img.shields.io/github/v/release/Valb51/ArduinoBackupTool?label=Download%20Latest)](https://github.com/Valb51/ArduinoBackupTool/releases/latest)

# Arduino Backup Tool v1.1.2

**Arduino Backup Tool** est une application graphique légère (PyQt5) permettant de **sauvegarder** et **restaurer** le firmware (flash, EEPROM) ainsi que les **fuses** (lfuse, hfuse, efuse) des cartes Arduino compatibles avec `avrdude`.

---

## 🆕 Nouveautés de la version 1.1.2

- Mise à jour du chemin d’installation Python dans le script `build_gui.py`
- Meilleure détection automatique du port COM, du MCU, du programmateur et du débit
- Nettoyage automatique des dossiers `build/`, `dist/`, `__pycache__/`
- Ajout d’options de confort : raccourci bureau, lancement automatique post-build
- Divers correctifs et stabilisations

---

## ⚠️ Limitations et compatibilité

- **Cartes non supportées** : les **Arduino Leonardo** (et compatibles ATmega32u4) ne sont pas reconnues correctement via `avrdude`.  
  👉 Ces cartes utilisent un port COM qui se réinitialise automatiquement lors de l'ouverture, empêchant la communication fiable avec le programmateur.

- **Supportées** : Uno, Nano, Mega, Pro Mini, ATmega328P, ATmega2560, etc.

---

## 🧰 Installation des drivers manuellement

Les drivers nécessaires **ne sont plus installés automatiquement**. Veuillez les installer manuellement si besoin :

- **CH340 (puce utilisée par beaucoup de clones Arduino)**  
  📥 [Télécharger le pilote CH340](https://sparks.gogo.co.nz/assets/_site/ch340.zip)

- **FTDI (pour cartes originales ou clones avec FT232RL)**  
  📥 [Télécharger le pilote FTDI](https://www.ftdichip.com/Drivers/VCP.htm)

- **Zadig (pour les programmateurs USBasp ou USBtinyISP)**  
  📥 [Télécharger Zadig](https://zadig.akeo.ie/)

---

## 📦 Prérequis

- Windows 10/11 (x64)
- Python 3.7+ (installable automatiquement si absent)
- `avrdude` intégré (aucune installation manuelle requise)
- Modules Python :
    - `PyQt5`, `pyserial`, `pywin32`, `pyinstaller`

---

## 🚀 Téléchargement

📥 **Version Windows (portable, sans installation)**  
👉 [Télécharger ArduinoBackupTool.exe](./dist/ArduinoBackupTool.exe)

---

## ▶️ Utilisation

1. **Lancer** l’exécutable `ArduinoBackupTool.exe`
2. Dans l’onglet **Configuration AVRDude**, valider les chemins vers `avrdude.exe` et `avrdude.conf`
3. Dans l’onglet **Paramètres Carte** :
    - Choisir ou détecter automatiquement : Port COM, MCU, Programmateur, Baudrate
4. Cliquer sur :
    - **Backup All** : pour sauvegarder la mémoire flash, EEPROM et les fuses
    - **Restore All** : pour restaurer une sauvegarde complète
5. Suivre la **barre de progression** et les **messages d’état**

---

## 📁 Arborescence du projet

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

yaml
Copier
Modifier

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.  
Voir le fichier `LICENSE` pour plus d’informations.

---

## 🤝 Contribution

Les retours, suggestions et correctifs sont les bienvenus :
- Signalez un bug ou une demande via les **issues**
- Créez une branche de fonctionnalité via Git, puis ouvrez une **pull request**

---

**Développé avec ❤️ pour simplifier la gestion du firmware Arduino.**