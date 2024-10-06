from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QDial, QSlider, QFileDialog
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt,  QEvent
import sys
from PIL import Image, ImageQt
import pillow_avif, pillow_jxl

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydrogen")
        self.movex, self.movey = 0, 0
        
        self.pixmap = self.getImage()

        # image/label stuff
        self.label = QLabel(self)
       
            
        #self.pixmap = QPixmap("test1.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, self.pixmap.width(), self.pixmap.height())
        self.label.setScaledContents(True)  
        self.setGeometry(0, 0, self.label.width(), self.label.height()) # x, y, width, height

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

        # event filters
        self.installEventFilter(self)
        self.rotationdial.installEventFilter(self)
        self.zoomslider.installEventFilter(self)

    def getImage(self): # get image from path
        if len(sys.argv) > 1 and not sys.argv[1].endswith(".avif"): # try opening image from command line arguments | prefer direct qpixmap if not avif or jxl
            return QPixmap(sys.argv[1])
        elif len(sys.argv) > 1 and sys.argv[1].endswith(".avif"): # if command argument is avif, use pillow_avif to open it and convert to qpixmap
            return ImageQt.toqpixmap(Image.open(sys.argv[1], formats=["avif"]))
        elif len(sys.argv) > 1 and sys.argv[1].endswith(".jxl"): # if command argument is jxl, use pillow_jxl to open it and convert to qpixmap
            return ImageQt.toqpixmap(Image.open(sys.argv[1], formats=["jxl"]))

        else: # if no command argument, let user choose file
            path = QFileDialog.getOpenFileName(self, "Open Image", 'c:\\', "Images (*.png *.jpg *.jpeg *.bmp *.gif *.avif *.jxl)")[0]
            if path.endswith(".avif"): # if user chooses avif, use pillow_avif to open it and convert to qpixmap
                return ImageQt.toqpixmap(Image.open(path, formats=["avif"]))
            elif path.endswith(".jxl"): # if user chooses jxl, use pillow_jxl to open it and convert to qpixmap
                return ImageQt.toqpixmap(Image.open(path, formats=["jxl"]))
            elif path: # if user chooses any other image, open it with QPixmap
                return QPixmap(path)
            else: # if user cancels file dialog, exit
                sys.exit()

    def updateLabel(self): # handle all label (image) transformations
        self.label.setGeometry(((self.width() - (self.pixmap.width() * self.zoomslider.value() / 100)) // 2) + self.movex, ((self.height() - (self.pixmap.height() * self.zoomslider.value() / 100)) // 2) + self.movey, self.pixmap.width() * self.zoomslider.value() / 100, self.pixmap.height() * self.zoomslider.value() / 100)

    def resizeEvent(self, event): # handle scaling of widgets when window is resized
        self.updateLabel()
        self.zoomslider.setGeometry(self.width() - 20, 0, 20, self.height())
        self.rotationdial.setGeometry(0, self.height()-75, 75, 75)

    def zoom_changed(self):
        self.updateLabel()
        
    def rotate_image(self): # handle rotating image by creating a new pixmap with the rotated image using .transformed
        self.label.setPixmap(self.pixmap.transformed(QTransform().rotate(self.rotationdial.value())))
        self.updateLabel()

    def eventFilter(self, source, event, drag=[False], dragstart=[None]): # handle mouse events | use default arguments to store variables in eventFilter
        if event.type() == QEvent.MouseButtonPress and source == self: # drag move start
            dragstart[0] = event.position()
            drag = True
        
        elif event.type() == QEvent.MouseMove and drag and source == self: # update image position as it's being dragged
            self.movex += event.position().x() - dragstart[0].x()
            self.movey += event.position().y() - dragstart[0].y()
            self.updateLabel()
            dragstart[0] = event.position()

        elif event.type() == QEvent.MouseButtonRelease and source == self: # finish dragging
            drag = False
            return True

        if source == self.rotationdial and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton: # reset rotation dial if right clicked
            self.rotationdial.setValue(0)
            self.updateLabel()
            return True

        if source == self and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton: # reset image position if right clicked
            self.movex, self.movey = 0, 0
            self.updateLabel()
            return True
        
        if source == self.zoomslider and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton: # reset zoom slider if right clicked
            self.zoomslider.setValue(100)
            self.updateLabel()
            return True
        
        if source == self and event.type() == QEvent.Wheel: # zoom in/out with mouse wheel
            self.zoomslider.setValue(self.zoomslider.value() + event.angleDelta().y() // 20)
            self.updateLabel()
            return True
        
        return super().eventFilter(source, event)

browser = QApplication([])
basewindow = MainWindow()
basewindow.show()
browser.exec()
