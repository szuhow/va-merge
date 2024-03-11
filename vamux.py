#!/usr/bin/python
import sys
import os
import argparse
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QProgressBar, QMessageBox
from PySide2.QtCore import QThread, Signal
import subprocess
from functools import partial
global gui

class MergeThread(QThread):
    progress = Signal(int)

    def run(self):
        # Replace with your actual merge logic using subprocess
        for i in range(101):
            self.progress.emit(i)
            QThread.msleep(1)


class MyApp(QWidget):
    def __init__(self, nogui_args=None):
        super(MyApp, self).__init__()

        self.video_file = None
        self.audio_file = None
        self.output_file = None
        self.btn4 = None
        self.generate_default_output = True  # Flag to control automatic output path
        
        if nogui_args:
            self.process_nogui_args(nogui_args)
        else:
            self.init_ui()

    def init_ui(self):
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
        self.setAcceptDrops(True)
        self.setWindowTitle('Audio-video merge GUI')
        self.setGeometry(300, 300, 300, 200)
        self.show()


    def dragEnterEvent(self, event):
        mime_data = event.mimeData()

        # Check if the mime data contains file URLs
        if mime_data.hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()

        # Retrieve file paths from mime data
        urls = mime_data.urls()
        if urls:
            # For simplicity, only use the first dropped file
            file_path = urls[0].toLocalFile()

            # Check the file type and update labels accordingly
            if file_path.lower().endswith(('.mp4', '.avi', '.mkv')):
                self.video_file = file_path
                self.video_label.setText('Video: ' + self.video_file)
                self.generate_output_path()
                self.generate_audio_path()
            elif file_path.lower().endswith(('.aac', '.mp3')):
                self.audio_file = file_path
                self.audio_label.setText('Audio: ' + (self.audio_file or '(Optional)'))
            elif not self.output_file and os.path.isdir(file_path):
                # Update the output file path if not already set
                self.output_file = os.path.join(file_path, 'output.mp4')
                self.output_label.setText('Output: ' + self.output_file)
    def critical(self, message):
        if gui:
            QMessageBox.critical(
                self,
                'Critical',
                message
            )
        else: 
            raise Exception(message)
        
    def information(self, message):
        if gui:
            QMessageBox.information(
                self,
                'Information',
                message
            )
        else:
            exit(0)
    def toggle_default_output(self, checked):
        self.generate_default_output = checked

    def generate_output_path(self):
        if self.video_file:
            # Extract video filename without extension
            video_name, ext = os.path.splitext(os.path.basename(self.video_file))
            # Generate default output path with suffix
            self.output_file = os.path.join(os.path.dirname(self.video_file), '{0}{1}'.format(video_name + "_merged", ext))
            self.output_label.setText('Output: ' + self.output_file)

    def generate_audio_path(self):
        if self.video_file:
            # Extract video filename without extension
            video_name, _ = os.path.splitext(os.path.basename(self.video_file))
            # Generate default output path with suffix
            self.audio_file = os.path.join(os.path.dirname(self.video_file), '{0}.aac'.format(video_name))
            self.audio_label.setText('Audio: ' + self.audio_file)

    def select_video(self):
        self.video_file, _ = QFileDialog.getOpenFileName(self)

        self.video_label.setText('Video: ' + self.video_file)
        self.generate_output_path()
        self.generate_audio_path()

    def select_audio(self):
        self.audio_file, _ = QFileDialog.getOpenFileName(self)
        self.audio_label.setText('Audio: ' + (self.audio_file or '(Optional)'))

    def select_output(self):
        self.output_file, _ = QFileDialog.getSaveFileName(self)
        self.generate_default_output = True  # User-defined output disables automatic generation

    def merge_files(self):
        
            # Validate video file
            

            # Disable the merge button to prevent multiple executions
           
                
                if self.video_file and self.audio_file and self.output_file:
                    if gui:
                        self.btn4.setEnabled(False)
                    try:
                        command = 'ffmpeg -n -i "{}" -i "{}" -c:v copy -c:a copy "{}"'.format(self.video_file, self.audio_file, self.output_file)
                        subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)  # Capture combined output
                        self.thread = MergeThread()
                        self.thread.finished.connect(self.on_thread_finished)
                        if gui:
                            self.thread.progress.connect(self.progress.setValue)
                        self.thread.start()
                    except subprocess.CalledProcessError as err:
                        self.critical('Cannot merge - Error: {}'.format(err.output.decode().splitlines()[-1]))  # Decode captured output
                    finally:
                        # Re-enable the merge button in any case
                        if gui:
                            self.btn4.setEnabled(True)

            # else:
            #     if not os.path.isfile(self.video_file):
            #         self.critical('Invalid video file.', gui = False)
            #         return

            #     # Validate audio file
            #     if self.audio_file and not os.path.isfile(self.audio_file):
            #         self.critical('Invalid audio file.', gui = False)
            #         return

            #     # Validate output path
            #     if not os.path.isdir(os.path.dirname(self.output_file)):
            #         self.critical('Invalid output directory.', gui = False)
            #         return
            #     # try:
            #     command = 'ffmpeg -n -i "{}" -i "{}" -c:v copy -c:a copy "{}"'.format(self.video_file, self.audio_file, self.output_file)
            #     subprocess.check_call(command, shell=True)
                # except subprocess.CalledProcessError as err:
                #     raise Exception(err)

    def on_thread_finished(self):
        self.information("The merge has been completed.")
        self.thread.deleteLater()

    def process_nogui_args(self, args):
        parser = argparse.ArgumentParser(description="Audio-Video Merge Tool")
        parser.add_argument('--video', required=True, help='Path to the video file')
        parser.add_argument('--audio', required=True, help='Path to the audio file')
        parser.add_argument('--output', required=True, help='Path for the output file')
        
        args = parser.parse_args(args)

        self.video_file = args.video
        self.audio_file = args.audio
        self.output_file = args.output

        # if gui:
        #     self.generate_output_path()
        #     self.generate_audio_path()

        self.merge_files()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    if len(sys.argv) > 1 and sys.argv[1] == "--nogui":
            if sys.argv[2:]:
                gui = False
                ex = MyApp(nogui_args=sys.argv[2:])
            else:
                raise Exception("Missing input and output params")
    else:
        gui = True
        ex = MyApp()

    sys.exit(app.exec_())