import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QProgressBar, QMessageBox
from PySide2.QtCore import QThread, Signal
import subprocess

class MergeThread(QThread):
    progress = Signal(int)

    def run(self):
        for i in range(101):
            self.progress.emit(i)
            QThread.msleep(100)

class MyApp(QWidget):
    def __init__(self):
        super(MyApp, self).__init__()

        self.video_file = None
        self.audio_file = None
        self.output_file = None

        self.initUI()

    def initUI(self):
        self.video_label = QLabel('No video selected', self)
        self.audio_label = QLabel('No audio selected', self)
        self.output_label = QLabel('No output file selected', self)

        btn1 = QPushButton('Select Video', self)
        btn1.clicked.connect(self.select_video)

        btn2 = QPushButton('Select Audio', self)
        btn2.clicked.connect(self.select_audio)

        btn3 = QPushButton('Select Output', self)
        btn3.clicked.connect(self.select_output)

        btn4 = QPushButton('Merge', self)
        btn4.clicked.connect(self.merge_files)

        self.progress = QProgressBar(self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.video_label)
        vbox.addWidget(btn1)
        vbox.addWidget(self.audio_label)
        vbox.addWidget(btn2)
        vbox.addWidget(self.output_label)
        vbox.addWidget(btn3)
        vbox.addWidget(btn4)
        vbox.addWidget(self.progress)

        self.setLayout(vbox)

        self.setWindowTitle('Audio-video merge GUI')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def select_video(self):
        self.video_file, _ = QFileDialog.getOpenFileName(self)
        self.video_label.setText('Video: ' + self.video_file)

    def select_audio(self):
        self.audio_file, _ = QFileDialog.getOpenFileName(self)
        self.audio_label.setText('Audio: ' + self.audio_file)

    def select_output(self):
        self.output_file, _ = QFileDialog.getSaveFileName(self)
        self.output_label.setText('Output: ' + self.output_file)

    def merge_files(self):
        if self.video_file and self.audio_file and self.output_file:
            command = 'ffmpeg -i "{}" -i "{}" -c:v copy -c:a copy "{}"'.format(self.video_file, self.audio_file, self.output_file)
            self.thread = MergeThread()
            self.thread.progress.connect(self.progress.setValue)
            self.thread.start()
            subprocess.call(command, shell=True)
            # if self.progress.setValue == 100:
            #     QMessageBox.information(self, "Merge completed", "The merge has been completed.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())