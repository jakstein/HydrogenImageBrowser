from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtGui import QPixmap
#import os
#from PIL import Image, ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydrogen")
        
        self.label = QLabel(self)
        self.pixmap = QPixmap("test1.jpg")

        #self.ratio = self.pixmap.width() / self.pixmap.height()

        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, self.pixmap.width(), self.pixmap.height())
        self.setGeometry(0, 0, self.label.width(), self.label.height()) # x, y, width, height
        self.setMinimumSize(self.pixmap.width(), self.pixmap.height())
        self.label.setScaledContents(False)  
        self.setCentralWidget(self.label)

    def resizeEvent(self, event):
        self.label.setGeometry((self.width() - self.pixmap.width()) // 2, (self.height() - self.pixmap.height()) // 2, self.pixmap.width(), self.pixmap.height())





browser = QApplication([])
basewindow = MainWindow()



basewindow.show()
browser.exec()
