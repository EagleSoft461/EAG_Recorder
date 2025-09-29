import sys
import cv2
import numpy as np
import pyautogui
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget,
    QFileDialog, QListWidget, QComboBox
)
from PyQt6.QtCore import QTimer, Qt


class ScreenRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EAG Recorder")
        self.setGeometry(200, 200, 400, 400)

        # Durum değişkenleri
        self.recording = False
        self.paused = False
        self.start_time = None
        self.elapsed_time = 0
        self.video_writer = None
        self.file_path = ""
        self.saved_files = []

        # Ana layout
        layout = QVBoxLayout()

        # Butonlar
        self.start_btn = QPushButton("Kaydı Başlat")
        self.start_btn.clicked.connect(self.start_recording)
        layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("Duraklat")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Kaydı Durdur")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_btn)

        # Kronometre etiketi
        self.timer_label = QLabel("Süre: 00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_label)

        # FPS ve kalite ayarı
        self.fps_label = QLabel("FPS Seçin:")
        layout.addWidget(self.fps_label)
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["10", "20", "30", "60"])
        layout.addWidget(self.fps_combo)

        # Kaydedilen dosyaların listesi
        self.files_label = QLabel("Kaydedilen Dosyalar:")
        layout.addWidget(self.files_label)
        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # Ana widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_recording(self):
        screen_size = pyautogui.size()
        fps = int(self.fps_combo.currentText())

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Kaydedilecek dosya adı", "", "AVI Dosyaları (*.avi)"
        )
        if not file_path:
            return

        self.file_path = file_path
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.video_writer = cv2.VideoWriter(self.file_path, fourcc, fps, screen_size)

        self.recording = True
        self.paused = False
        self.start_time = time.time()
        self.elapsed_time = 0

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.timer.start(1000)

        self.record_frame()

    def record_frame(self):
        if not self.recording:
            return

        if not self.paused:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.video_writer.write(frame)

        QTimer.singleShot(10, self.record_frame)

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.start_time = time.time() - self.elapsed_time
            self.pause_btn.setText("Duraklat")
        else:
            self.paused = True
            self.pause_btn.setText("Devam Et")

    def stop_recording(self):
        self.recording = False
        self.timer.stop()
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        # Dosyayı listeye ekle
        if self.file_path:
            self.saved_files.append(self.file_path)
            self.files_list.addItem(self.file_path)

        self.timer_label.setText("Süre: 00:00")

    def update_timer(self):
        if self.recording and not self.paused:
            self.elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(self.elapsed_time), 60)
            self.timer_label.setText(f"Süre: {minutes:02}:{seconds:02}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorder()
    window.show()
    sys.exit(app.exec())