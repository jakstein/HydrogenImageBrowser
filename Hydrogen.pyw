from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtGui import QPixmap
#import os
#from PIL import Image, ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydrogen")
        self.setMinimumSize(300, 200)

        label = QLabel(self)
        pixmap = QPixmap("test1.jpg")
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height()) 

        self.setCentralWidget(label)

        
    



browser = QApplication([])
basewindow = MainWindow()



basewindow.show()
browser.exec()
