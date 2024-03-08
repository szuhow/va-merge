import sys, os
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QProgressBar, QMessageBox
from PySide2.QtCore import QThread, Signal
import subprocess

class MergeThread(QThread):
    progress = Signal(int)

    def run(self):
        # Replace with your actual merge logic using subprocess
        for i in range(101):
            self.progress.emit(i)
            QThread.msleep(100)

class MyApp(QWidget):
    def __init__(self):
        super(MyApp, self).__init__()

        self.video_file = None
        self.audio_file = None
        self.output_file = None
        self.btn4 = None
        self.generate_default_output = True  # Flag to control automatic output path
        # self.default_audio_suffix = '.'  # Default audio suffix
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

        self.btn4 = QPushButton('Merge', self)
        self.btn4.clicked.connect(self.merge_files)

        self.progress = QProgressBar(self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.video_label)
        vbox.addWidget(btn1)
        vbox.addWidget(self.audio_label)
        vbox.addWidget(btn2)
        vbox.addWidget(self.output_label)
        vbox.addWidget(btn3)
        vbox.addWidget(self.btn4)
        vbox.addWidget(self.progress)

        self.setLayout(vbox)

        self.setWindowTitle('Audio-video merge GUI')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def critical(self):
        QMessageBox.critical(
            self,
            'Critical',
            'This is a critical message.'
        )
    def toggle_default_output(self, checked):
        self.generate_default_output = checked

    def generate_output_path(self):
        if self.video_file:
            # Extract video filename without extension
            video_name, ext  = os.path.splitext(os.path.basename(self.video_file))
            # Generate default output path with suffix
            self.output_file = os.path.join(os.path.dirname(self.video_file), '{0}{1}'.format(video_name + "_merged", ext))
            self.output_label.setText('Output: ' + self.output_file)

    def generate_audio_path(self):
        if self.video_file:
            # Extract video filename without extension
            video_name, _  = os.path.splitext(os.path.basename(self.video_file))
            # Generate default output path with suffix
            
            self.audio_file = os.path.join(os.path.dirname(self.video_file), '{0}.aac'.format(video_name))
            self.audio_label.setText('Audio: ' + self.audio_file)

    def select_video(self):
        self.video_file, _ = QFileDialog.getOpenFileName(self)
        self.video_label.setText('Video: ' + self.video_file)

        # Optionally generate default output path based on video
        if self.generate_default_output:
            self.generate_output_path()
            self.generate_audio_path()

    def select_audio(self):
        self.audio_file, _ = QFileDialog.getOpenFileName(self)
        self.audio_label.setText('Audio: ' + (self.audio_file or '(Optional)'))

    def select_output(self):
        self.output_file, _ = QFileDialog.getSaveFileName(self)
        self.output_label.setText('Output: ' + self.output_file)
        self.generate_default_output = True # User-defined output disables automatic generation

    def merge_files(self):
        if self.video_file and self.audio_file and self.output_file:
            # Disable the merge button to prevent multiple executions
            self.btn4.setEnabled(False)
            try:
                command = 'ffmpeg -n -i "{}" -i "{}" -c:v copy -c:a copy "{}"'.format(self.video_file, self.audio_file, self.output_file)
                subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)  # Capture combined output
                self.thread = MergeThread()
                self.thread.finished.connect(self.on_thread_finished)
                self.thread.progress.connect(self.progress.setValue)
                self.thread.start()
                
            except subprocess.CalledProcessError as err:
                QMessageBox.critical(self, "Cannot merge", 'Error: {}'.format(err.output.decode().splitlines()[-1]))  # Decode captured output
            finally:
                # Re-enable the merge button in any case
                self.btn4.setEnabled(True)
    def on_thread_finished(self):
        QMessageBox.information(self, "Merge completed", "The merge has been completed.")
        self.thread.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    ex = MyApp()
    
    sys.exit(app.exec_())