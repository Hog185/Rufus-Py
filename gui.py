import sys
import json
import urllib.parse
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QPushButton, QProgressBar, QCheckBox,
    QMessageBox, QDialog, QTextEdit, QFileDialog,
    QLineEdit, QFrame, QStatusBar, QToolButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import states


# -----------------------------
# Log Window
# -----------------------------
class LogWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rufus Log")
        self.resize(650, 450)

        layout = QVBoxLayout(self)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            background-color: #1E1E1E;
            color: #EAEAEA;
            border: 1px solid #2C2C2C;
        """)

        layout.addWidget(self.log_text)

        self.log_text.append("Rufus")
        self.log_text.append("------------------------------------------------")
        self.log_text.append("Ready.")


# -----------------------------
# Main Window
# -----------------------------
class Rufus(QMainWindow):

    def __init__(self, usb_devices=None):
        super().__init__()

        self.usb_devices = usb_devices or {}

        self.setWindowTitle("Rufus")
        self.setFixedSize(640, 780)

        self.apply_dark_theme()
        self.init_ui()

    # -----------------------------
    # Dark Theme
    # -----------------------------
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: #EAEAEA;
                font-family: 'Segoe UI';
                font-size: 9pt;
            }

            QLabel { color: #EAEAEA; }

            QLabel#sectionHeader {
                font-size: 15pt;
                color: #FFFFFF;
            }

            QComboBox, QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid #2C2C2C;
                border-radius: 3px;
                padding: 4px;
                color: #EAEAEA;
            }

            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #3A82F7;
            }

            QPushButton {
                background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 6px;
                color: #EAEAEA;
            }

            QPushButton:hover {
                border-color: #3A82F7;
            }

            #btnStart:pressed {
                background-color: #00C853;
            }

            QProgressBar {
                background-color: #1E1E1E;
                border: 1px solid #2C2C2C;
                text-align: center;
                color: white;
            }

            QProgressBar::chunk {
                background-color: #00C853;
            }

            QToolButton {
                background-color: #1E1E1E;
                border: 1px solid #2C2C2C;
            }

            QStatusBar {
                background-color: #121212;
                border-top: 1px solid #2C2C2C;
                color: #AAAAAA;
            }

            QFrame {
                background-color: #2C2C2C;
                max-height: 1px;
            }
        """)

    # -----------------------------
    # UI
    # -----------------------------
    def create_header(self, text):
        layout = QHBoxLayout()
        label = QLabel(text)
        label.setObjectName("sectionHeader")

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)

        layout.addWidget(label)
        layout.addWidget(line, 1)
        return layout

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # Header
        main_layout.addLayout(self.create_header("Drive Properties"))

        # Device Combo
        self.combo_device = QComboBox()

        if self.usb_devices:
            for path, label in self.usb_devices.items():
                self.combo_device.addItem(f"{label} ({path})")
        else:
            self.combo_device.addItem("No USB devices found")

        main_layout.addWidget(QLabel("Device"))
        main_layout.addWidget(self.combo_device)

        # Boot Selection
        self.combo_boot = QComboBox()
        self.combo_boot.setEditable(True)
        self.combo_boot.addItem("installationmedia.iso")

        btn_select = QPushButton("SELECT")
        btn_select.clicked.connect(self.browse_file)

        row = QHBoxLayout()
        row.addWidget(self.combo_boot)
        row.addWidget(btn_select)

        main_layout.addWidget(QLabel("Boot selection"))
        main_layout.addLayout(row)

        # Progress
        main_layout.addLayout(self.create_header("Status"))

        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Buttons
        btn_row = QHBoxLayout()

        self.btn_start = QPushButton("START")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.start_process)

        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.clicked.connect(self.cancel_process)

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_cancel)

        main_layout.addLayout(btn_row)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    # -----------------------------
    # Logic
    # -----------------------------
    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Disk Image", "", "ISO Images (*.iso)"
        )
        if file_name:
            clean = file_name.split("/")[-1]
            self.combo_boot.setItemText(0, clean)

    def start_process(self):
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def update_progress(self):
        self.progress += 2
        self.progress_bar.setValue(self.progress)
        self.progress_bar.setFormat(f"{self.progress}%")

        if self.progress >= 100:
            self.timer.stop()
            self.statusBar.showMessage("Ready")

    def cancel_process(self):
        self.progress_bar.setValue(0)
        self.statusBar.showMessage("Cancelled")


# -----------------------------
# Entry
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    usb_devices = {}

    if len(sys.argv) > 1:
        try:
            decoded = urllib.parse.unquote(sys.argv[1])
            usb_devices = json.loads(decoded)
        except Exception:
            usb_devices = {}

    window = Rufus(usb_devices)
    window.show()
    sys.exit(app.exec())
