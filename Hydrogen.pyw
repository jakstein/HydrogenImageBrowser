from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QDial, QSlider
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QEvent
#import os
#from PIL import Image, ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydrogen")
        self.movex, self.movey = 0, 0

        # image/label stuff
        self.label = QLabel(self)
        self.pixmap = QPixmap("test1.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, self.pixmap.width(), self.pixmap.height())
        self.label.setScaledContents(True)  
        self.setGeometry(0, 0, self.label.width(), self.label.height()) # x, y, width, height
        self.setMinimumSize(self.pixmap.width(), self.pixmap.height())



        # zoom slider stuff
        self.zoomslider = QSlider(Qt.Vertical, self)
        self.zoomslider.setGeometry(0, self.width(), 20, 300)
        self.zoomslider.setRange(1, 500)
        self.zoomslider.setValue(100)
        self.zoomslider.valueChanged.connect(self.zoom_changed)

        # dial stuff
        self.rotationdial = QDial(self)
        self.rotationdial.setGeometry(0, self.height()-75, 75, 75)
        self.rotationdial.setRange(-180, 180)
        self.rotationdial.setValue(0)
        self.rotationdial.valueChanged.connect(self.rotate_image)

        self.installEventFilter(self)
        self.rotationdial.installEventFilter(self)

    def updateLabel(self): # handle all label transformations
        self.label.setGeometry(((self.width() - (self.pixmap.width() * self.zoomslider.value() / 100)) // 2) + self.movex, ((self.height() - (self.pixmap.height() * self.zoomslider.value() / 100)) // 2) + self.movey, self.pixmap.width() * self.zoomslider.value() / 100, self.pixmap.height() * self.zoomslider.value() / 100)

    def resizeEvent(self, event):
        self.updateLabel()
        self.zoomslider.setGeometry(self.width() - 20, 0, 20, self.height())
        self.rotationdial.setGeometry(0, self.height()-75, 75, 75)

    def zoom_changed(self):
        self.updateLabel()
        
    def rotate_image(self):
        self.label.setPixmap(self.pixmap.transformed(QTransform().rotate(self.rotationdial.value())))
        self.updateLabel()

    def eventFilter(self, source, event, drag=[False], dragstart=[None]): # drag move behaviour | use default arguments to store variables in eventFilter
        if event.type() == QEvent.MouseButtonPress and source != self.rotationdial: 
            dragstart[0] = event.position()
            drag = True
        
        elif event.type() == QEvent.MouseMove and drag and source != self.rotationdial: # update image position as it's being dragged
            self.movex += event.position().x() - dragstart[0].x()
            self.movey += event.position().y() - dragstart[0].y()
            self.updateLabel()
            dragstart[0] = event.position()

        elif event.type() == QEvent.MouseButtonRelease and source != self.rotationdial:
            drag = False
            return True

        if source == self.rotationdial and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            self.rotationdial.setValue(0)
            self.updateLabel()
            return True


        return super().eventFilter(source, event)

browser = QApplication([])
basewindow = MainWindow()
basewindow.show()
browser.exec()
