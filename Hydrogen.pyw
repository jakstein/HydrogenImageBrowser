from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtGui import QPixmap
#import os
#from PIL import Image, ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydrogen")
        

        self.label = QLabel(self)
        pixmap = QPixmap("test1.jpg")
        self.ratio = pixmap.width() / pixmap.height()
        self.label.setPixmap(pixmap)
        self.label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        self.setGeometry(0, 0, self.label.width(), self.label.height()) # x, y, width, height
        self.setMinimumSize(pixmap.width(), pixmap.height())
        self.label.setScaledContents(False)  
        self.setCentralWidget(self.label)
    def resizeEvent(self, event):
        self.label.setGeometry(0, 0, self.width(), self.ratio * self.width())





browser = QApplication([])
basewindow = MainWindow()



basewindow.show()
browser.exec()
