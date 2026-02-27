import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QComboBox, 
                             QPushButton, QProgressBar, QCheckBox, 
                             QMessageBox, QDialog, QTextEdit, QFileDialog, 
                             QLineEdit, QFrame, QStatusBar, QToolButton, QSpacerItem)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class LogWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rufus Log")
        self.resize(650, 450)
        layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        layout.addWidget(self.log_text)
        
        self.log_text.append("Rufus 3.20.1929 (Portable)")
        self.log_text.append("Windows version: 10.0 (Build 19045)")
        self.log_text.append("Syslinux versions: 6.04-pre1 (installed), 6.04-pre1 (embedded)")
        self.log_text.append("Grub versions: 2.06 (embedded)")
        self.log_text.append("E2fsprogs version: 1.47.0 (embedded)")
        self.log_text.append("Vulkan Renderer: None")
        self.log_text.append("Locale: en_US.UTF-8")
        self.log_text.append("------------------------------------------------")
        self.log_text.append("Ready.")
        
        self.setLayout(layout)

class RufusClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rufus 3.20.1929")
        self.setFixedSize(640, 780) 
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                font-size: 9pt;
                color: #000000;
            }
            QLabel {
                color: #000000;
                padding: 2px;
            }
            /* Section Headers */
            QLabel#sectionHeader {
                font-size: 16pt;
                font-weight: normal;
                color: #000000;
                padding: 5px 0;
            }
            QComboBox, QLineEdit {
                border: 1px solid #D0D0D0;
                border-radius: 2px;
                padding: 4px 6px;
                background-color: white;
                min-height: 24px;
                font-size: 9pt;
                selection-background-color: #0078D7;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #0078D7;
            }
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #D0D0D0;
            }
            QPushButton {
                background-color: #E1E1E1;
                border: 1px solid #A0A0A0;
                border-radius: 2px;
                padding: 4px 15px;
                min-width: 75px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #E5F1FB;
                border-color: #0078D7;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
            QPushButton:disabled {
                color: #888888;
                background-color: #F0F0F0;
                border-color: #D0D0D0;
            }
            /* The Big Green Start Button - Exact Rufus Green */
            #btnStart {
                background-color: #00CC00;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #009900;
                min-height: 32px;
                padding: 5px 20px;
            }
            #btnStart:hover {
                background-color: #00DD00;
                border-color: #00AA00;
            }
            #btnStart:pressed {
                background-color: #00AA00;
            }
            #btnStart:disabled {
                background-color: #CCCCCC;
                color: #666666;
                border: 1px solid #999999;
            }
            QCheckBox {
                spacing: 5px;
                font-size: 9pt;
            }
            QProgressBar {
                border: 1px solid #A0A0A0;
                border-radius: 2px;
                text-align: center;
                background-color: white;
                height: 22px;
                font-size: 9pt;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #00CC00;
            }
            /* Icon Only Buttons */
            QToolButton {
                border: 1px solid #D0D0D0;
                background-color: white;
                border-radius: 2px;
                padding: 4px;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
                font-size: 18px;
            }
            QToolButton:hover {
                background-color: #E5F1FB;
                border-color: #0078D7;
            }
            QToolButton:pressed {
                background-color: #D0D0D0;
            }
            QStatusBar {
                background-color: #F0F0F0;
                border-top: 1px solid #D0D0D0;
                font-size: 9pt;
                color: #000000;
            }
            /* Link style for advanced options */
            QLabel#linkLabel {
                color: #000000;
                text-decoration: none;
                font-size: 9pt;
            }
            QLabel#linkLabel:hover {
                color: #0078D7;
                text-decoration: underline;
            }
        """)

        self.init_ui()

    def create_header(self, text):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 5)
        label = QLabel(text)
        label.setObjectName("sectionHeader")
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #000000; min-height: 1px; max-height: 1px;")
        
        layout.addWidget(label)
        layout.addWidget(line, 1)
        return layout

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(15, 10, 15, 10)

        main_layout.addLayout(self.create_header("Drive Properties"))

        lbl_device = QLabel("Device")
        lbl_device.setStyleSheet("font-weight: normal; font-size: 9pt; padding-bottom: 2px;")
        self.combo_device = QComboBox()
        self.combo_device.addItem("CCCOMA_X64FRE_EN-GB_DV9 (F:) [8 GB]")
        self.combo_device.addItem("Generic Flash Disk 8.00 GB (E:)")
        
        device_layout = QVBoxLayout()
        device_layout.setSpacing(2)
        device_layout.addWidget(lbl_device)
        device_layout.addWidget(self.combo_device)
        main_layout.addLayout(device_layout)

        lbl_boot = QLabel("Boot selection")
        lbl_boot.setStyleSheet("font-weight: normal; font-size: 9pt; padding-bottom: 2px;")
        
        boot_row = QHBoxLayout()
        boot_row.setSpacing(5)
        
        self.combo_boot = QComboBox()
        self.combo_boot.setEditable(True)
        self.combo_boot.lineEdit().setReadOnly(True)
        self.combo_boot.addItem("Win11_22H2_EnglishInternational_x64.iso")
        
        lbl_check = QLabel("✓") 
        lbl_check.setStyleSheet("font-size: 14pt; color: #666; padding: 0 5px;")
        
        btn_select = QPushButton("SELECT")
        btn_select.clicked.connect(self.browse_file)
        
        btn_boot_arrow = QToolButton()
        btn_boot_arrow.setText("▼")
        btn_boot_arrow.setFixedWidth(25)
        
        boot_row.addWidget(self.combo_boot, 1)
        boot_row.addWidget(lbl_check)
        boot_row.addWidget(btn_select)
        boot_row.addWidget(btn_boot_arrow)
        
        boot_layout = QVBoxLayout()
        boot_layout.setSpacing(2)
        boot_layout.addWidget(lbl_boot)
        boot_layout.addLayout(boot_row)
        main_layout.addLayout(boot_layout)

        lbl_image = QLabel("Image option")
        lbl_image.setStyleSheet("font-weight: normal; font-size: 9pt; padding-bottom: 2px;")
        self.combo_image_option = QComboBox()
        self.combo_image_option.addItem("Standard Windows installation")
        self.combo_image_option.addItem("Windows To Go")
        
        image_layout = QVBoxLayout()
        image_layout.setSpacing(2)
        image_layout.addWidget(lbl_image)
        image_layout.addWidget(self.combo_image_option)
        main_layout.addLayout(image_layout)

        grid_part = QGridLayout()
        grid_part.setSpacing(10)
        grid_part.setColumnStretch(1, 1)
        grid_part.setColumnStretch(3, 1)
        
        lbl_part = QLabel("Partition scheme")
        lbl_part.setStyleSheet("font-weight: normal; font-size: 9pt;")
        self.combo_partition = QComboBox()
        self.combo_partition.addItem("GPT")
        self.combo_partition.addItem("MBR")
        
        lbl_target = QLabel("Target system")
        lbl_target.setStyleSheet("font-weight: normal; font-size: 9pt;")
        self.combo_target = QComboBox()
        self.combo_target.addItem("UEFI (non CSM)")
        self.combo_target.addItem("BIOS (or UEFI-CSM)")
        
        grid_part.addWidget(lbl_part, 0, 0)
        grid_part.addWidget(self.combo_partition, 1, 0)
        grid_part.addWidget(lbl_target, 0, 2)
        grid_part.addWidget(self.combo_target, 1, 2)
        
        main_layout.addLayout(grid_part)
        
        main_layout.addSpacing(5)

        lbl_adv_drive = QLabel("▼ Show advanced drive properties")
        lbl_adv_drive.setObjectName("linkLabel")
        main_layout.addWidget(lbl_adv_drive)
        
        main_layout.addSpacing(15)

        main_layout.addLayout(self.create_header("Format Options"))

        lbl_vol = QLabel("Volume label")
        lbl_vol.setStyleSheet("font-weight: normal; font-size: 9pt; padding-bottom: 2px;")
        self.input_label = QLineEdit("CCCOMA_X64FRE_EN-GB_DV9")
        
        vol_layout = QVBoxLayout()
        vol_layout.setSpacing(2)
        vol_layout.addWidget(lbl_vol)
        vol_layout.addWidget(self.input_label)
        main_layout.addLayout(vol_layout)

        grid_fmt = QGridLayout()
        grid_fmt.setSpacing(10)
        grid_fmt.setColumnStretch(1, 1)
        grid_fmt.setColumnStretch(3, 1)
        
        lbl_fs = QLabel("File system")
        lbl_fs.setStyleSheet("font-weight: normal; font-size: 9pt;")
        self.combo_fs = QComboBox()
        self.combo_fs.addItem("NTFS")
        self.combo_fs.addItem("FAT32")
        self.combo_fs.addItem("exFAT")
        
        lbl_cluster = QLabel("Cluster size")
        lbl_cluster.setStyleSheet("font-weight: normal; font-size: 9pt;")
        self.combo_cluster = QComboBox()
        self.combo_cluster.addItem("4096 bytes (Default)")
        self.combo_cluster.addItem("8192 bytes")
        
        grid_fmt.addWidget(lbl_fs, 0, 0)
        grid_fmt.addWidget(self.combo_fs, 1, 0)
        grid_fmt.addWidget(lbl_cluster, 0, 2)
        grid_fmt.addWidget(self.combo_cluster, 1, 2)
        
        main_layout.addLayout(grid_fmt)

        lbl_adv_fmt = QLabel("▲ Hide advanced format options")
        lbl_adv_fmt.setObjectName("linkLabel")
        main_layout.addWidget(lbl_adv_fmt)

        self.chk_quick = QCheckBox("Quick format")
        self.chk_quick.setChecked(True)
        self.chk_extended = QCheckBox("Create extended label and icon files")
        self.chk_extended.setChecked(True)
        
        bad_blocks_row = QHBoxLayout()
        self.chk_badblocks = QCheckBox("Check device for bad blocks")
        self.combo_badblocks = QComboBox()
        self.combo_badblocks.addItem("1 pass")
        self.combo_badblocks.setFixedWidth(100)
        self.combo_badblocks.setEnabled(False)
        
        bad_blocks_row.addWidget(self.chk_badblocks)
        bad_blocks_row.addWidget(self.combo_badblocks)
        bad_blocks_row.addStretch()

        chk_layout = QVBoxLayout()
        chk_layout.setSpacing(5)
        chk_layout.addWidget(self.chk_quick)
        chk_layout.addWidget(self.chk_extended)
        chk_layout.addLayout(bad_blocks_row)
        
        main_layout.addLayout(chk_layout)
        
        main_layout.addSpacing(15)

        main_layout.addLayout(self.create_header("Status"))

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(86)
        self.progress_bar.setFormat("Copying ISO files: 86.0%")
        main_layout.addWidget(self.progress_bar)

        bottom_controls = QHBoxLayout()
        bottom_controls.setSpacing(10)
        bottom_controls.setContentsMargins(0, 10, 0, 0)
        
        icons_layout = QHBoxLayout()
        icons_layout.setSpacing(5)
        
        btn_icon1 = QToolButton()
        btn_icon1.setText("🌐")
        btn_icon1.setToolTip("Download updates")
        
        btn_icon2 = QToolButton()
        btn_icon2.setText("ℹ")
        btn_icon2.setToolTip("About")
        
        btn_icon3 = QToolButton()
        btn_icon3.setText("⚙")
        btn_icon3.setToolTip("Settings")
        
        btn_icon4 = QToolButton()
        btn_icon4.setText("📄")
        btn_icon4.setToolTip("Log")
        btn_icon4.clicked.connect(self.show_log)
        
        icons_layout.addWidget(btn_icon1)
        icons_layout.addWidget(btn_icon2)
        icons_layout.addWidget(btn_icon3)
        icons_layout.addWidget(btn_icon4)
        icons_layout.addStretch()
        
        self.btn_start = QPushButton("START")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setEnabled(False)
        self.btn_start.setFixedWidth(100)
        self.btn_start.clicked.connect(self.start_process)
        
        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.setFixedWidth(100)
        self.btn_cancel.clicked.connect(self.cancel_process)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_cancel)
        
        bottom_controls.addLayout(icons_layout, 1)
        bottom_controls.addLayout(btn_layout)
        
        main_layout.addLayout(bottom_controls)
        
        main_layout.addStretch()

        central_widget.setLayout(main_layout)
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("F:\\sources\\install.wim (4.4 GB)                       00:00:46", 0)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Disk Image", "", "ISO Images (*.iso);;All Files (*)")
        if file_name:
            clean_name = file_name.split("/")[-1].split("\\")[-1]
            self.combo_boot.setItemText(0, clean_name)
            self.input_label.setText(clean_name.split('.')[0].upper())
            self.log_message(f"Selected image: {file_name}")

    def show_log(self):
        self.log_window = LogWindow()
        self.log_window.show()

    def log_message(self, msg):
        if hasattr(self, 'log_window'):
            self.log_window.log_text.append(f"[INFO] {msg}")

    def start_process(self):
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Formatting... 0%")
        self.simulate_write()

    def cancel_process(self):
        reply = QMessageBox.question(self, "Cancel", "Are you sure you want to cancel?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("")
            self.btn_start.setEnabled(True)
            self.btn_cancel.setEnabled(False)
            self.statusBar.showMessage("Ready", 0)

    def simulate_write(self):
        self.timer = QTimer()
        self.progress = 86
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def update_progress(self):
        self.progress += 1
        if self.progress > 100:
            self.progress = 0
        self.progress_bar.setValue(self.progress)
        self.progress_bar.setFormat(f"Copying ISO files: {self.progress}.0%")
        
        if self.progress >= 100:
            self.timer.stop()
            self.btn_start.setEnabled(True)
            self.btn_cancel.setEnabled(False)
            self.statusBar.showMessage("Ready", 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = RufusClone()
    window.show()
    sys.exit(app.exec())
