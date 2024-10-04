from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QDial, QSlider
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
#import os
#from PIL import Image, ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydrogen")

        # image/label stuff
        self.label = QLabel(self)
        self.pixmap = QPixmap("test1.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, self.pixmap.width(), self.pixmap.height())
        self.label.setScaledContents(True)  
        self.setGeometry(0, 0, self.label.width(), self.label.height()) # x, y, width, height
        self.setMinimumSize(self.pixmap.width(), self.pixmap.height())

        # zoom slider stuff
        self.zoomslider = QSlider(self)
        self.zoomslider.setOrientation(Qt.Vertical)
        self.zoomslider.setGeometry(0, self.width(), 20, 300)
        self.zoomslider.setMinimum(1)
        self.zoomslider.setMaximum(500)
        self.zoomslider.setValue(100)
        self.zoomslider.valueChanged.connect(self.zoom_changed)
        
    def updateLabel(self): # handle all label transformations
        self.label.setGeometry((self.width() - (self.pixmap.width() * self.zoomslider.value() / 100)) // 2, (self.height() - (self.pixmap.height() * self.zoomslider.value() / 100)) // 2, self.pixmap.width() * self.zoomslider.value() / 100, self.pixmap.height() * self.zoomslider.value() / 100)

    def resizeEvent(self, event):
        self.updateLabel()
        self.zoomslider.setGeometry(self.width() - 20, 0, 20, self.height())

    def zoom_changed(self):
        self.updateLabel()
        

browser = QApplication([])
basewindow = MainWindow()



basewindow.show()
browser.exec()
