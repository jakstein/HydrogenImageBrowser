from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QDial, QSlider, QFileDialog
from PySide6.QtGui import QKeyEvent, QPixmap, QTransform, QIcon, QGuiApplication, QImageReader
from PySide6.QtCore import Qt,  QEvent
import sys, os.path, os, ctypes, math
from PIL import Image, ImageQt
import pillow_avif, pillow_jxl
import natsort


"""
Shortcuts:
- R: flip image horizontally
- Shift + R: flip image vertically
- Ctrl + R: reset flip
- F: fit image to window
- H: toggle UI elements

- Right click on image: reset image position
- Right click on rotation dial: reset rotation
- Right click on zoom slider: reset zoom
- Right click on next/prev button: go to first/last image

"""

# TODO add autohiding of elements when not moving
# TODO improve scroll to cursor zooming

# setup for windows taskbar icon to show up properly
if sys.platform == "win32":
    myappid = 'mycompany.myproduct.subproduct.version' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

browser = QApplication([])
QImageReader.setAllocationLimit(1024) 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hydrogen_icon.png")))
        self.setWindowTitle("Hydrogen")
        self.movement = {"x": 0, "y": 0}
        self.filepaths = []
        self.UIvisibile = True
        self.helpVisible = False
        self.getFirstImage()
        #self.pixmap = QPixmap("testimages/test1.jpg")
        #os.chdir(os.path.dirname("testimages/test1.jpg"))

        # image/label stuff
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, self.pixmap.width(), self.pixmap.height())
        self.label.setScaledContents(True)
        self.setGeometry(0, 30, min(self.label.width(), QGuiApplication.primaryScreen().availableGeometry().width()), min(self.label.height(), QGuiApplication.primaryScreen().availableGeometry().height())) # set window size to image size or screen size if image is larger

        # zoom slider stuff
        self.zoomslider = QSlider(Qt.Vertical, self)
        self.zoomslider.setGeometry(0, self.width(), 20, 300)
        self.zoomslider.setRange(1, 500)
        self.zoomslider.setValue(100)
        self.zoomslider.valueChanged.connect(self.zoom_changed)
        self.zoomslider.setTickInterval(5)
        self.zoomslider.setStyleSheet("""
    QSlider::groove:vertical {
        background: rgba(255, 255, 255, 80);
        width: 8px;
        border-radius: 4px;
    }
    QSlider::handle:vertical {
        background: rgba(255, 255, 255, 150);
        border: 1px solid rgba(0, 0, 0, 100);
        height: 20px;
        margin: -4px;
        border-radius: 4px;
    }
""")

        # dial stuff
        self.rotationdial = QDial(self)
        self.rotationdial.setGeometry(0, self.height()-75, 75, 75)
        self.rotationdial.setRange(-180, 180)
        self.rotationdial.setValue(0)
        self.rotationdial.valueChanged.connect(self.rotate_image)
        self.rotationdial.setStyleSheet("""
    QDial {
        background: rgba(255, 255, 255, 50);
        border: 1px solid rgba(0, 0, 0, 50);
        border-radius: 37px;  /* half of dial size (75/2) */
    }
    QDial::handle {
        background: rgba(255, 255, 255, 150);
        border: 1px solid rgba(0, 0, 0, 100);
        border-radius: 5px;
    }
""")

        # navigation buttons
        self.nextbutton = QPushButton(">", self)
        self.nextbutton.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                border: 1px solid rgba(0, 0, 0, 50);
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        self.prevbutton = QPushButton("<", self)
        self.prevbutton.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                border: 1px solid rgba(0, 0, 0, 50);
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        self.nextbutton.setGeometry(self.width()-20, 0, 20, 20)
        self.prevbutton.setGeometry(self.width()-40, 0, 20, 20)
        self.nextbutton.setShortcut("Right")
        self.prevbutton.setShortcut("Left")
        self.nextbutton.clicked.connect(lambda: self.changeImage("next"))
        self.prevbutton.clicked.connect(lambda: self.changeImage("prev"))

        # help popup
        self.helpPopup = QLabel(self)
        self.helpPopup.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200);"
            "border-radius: 15px; color: white; padding: 10px;"
        )
        help_text = (
            "<b>Shortcuts:</b><br>"
            "<span style='border:1px solid white; border-radius:3px; padding:2px;'>R</span>: Flip image horizontally<br>"
            "<span style='border:1px solid white; border-radius:3px; padding:2px;'>Shift+R</span>: Flip image vertically<br>"
            "<span style='border:1px solid white; border-radius:3px; padding:2px;'>Ctrl+R</span>: Reset flip<br>"
            "<span style='border:1px solid white; border-radius:3px; padding:2px;'>F</span>: Fit image to window<br>"
            "<span style='border:1px solid white; border-radius:3px; padding:2px;'>H</span>: Toggle UI elements<br>"
            "<span style='border:1px solid white; border-radius:3px; padding:2px;'>Del</span>: Delete image<br>"
            "<span style='border:1px solid white; border-radius:3px; padding:2px;'>Q</span>: Toggle this help popup<br>"
            "Right click on image: Reset position<br>"
            "Right click on rotation dial: Reset rotation<br>"
            "Right click on zoom slider: Reset zoom<br>"
            "Right click on next/prev button: Go to first/last image"
        )
        self.helpPopup.setText(help_text)
        self.helpPopup.adjustSize()
        self.helpPopup.move((self.width() - self.helpPopup.width()) // 2, (self.height() - self.helpPopup.height()) // 2)
        self.helpPopup.setVisible(False)

        # event filters
        self.installEventFilter(self)
        self.rotationdial.installEventFilter(self)
        self.zoomslider.installEventFilter(self)
        self.prevbutton.installEventFilter(self)
        self.nextbutton.installEventFilter(self)

        if  self.pixmap.width() > (QGuiApplication.primaryScreen().availableGeometry().width() * 0.75) and self.pixmap.height() > (QGuiApplication.primaryScreen().availableGeometry().height() * 0.75):
            self.showMaximized()
            
        if self.pixmap.width() > QGuiApplication.primaryScreen().availableGeometry().width() or self.pixmap.height() > QGuiApplication.primaryScreen().availableGeometry().height():
            self.fitImage()

    def getFirstImage(self): # get initial image to display
            if len(sys.argv) > 1: 
                os.chdir(os.path.dirname(sys.argv[1])) 
                self.path = sys.argv[1]
                return self.loadImage(sys.argv[1])

            else: # if no command argument, let user choose file
                self.path = QFileDialog.getOpenFileName(self, "Open Image", os.getcwd(), "Images (*.png *.jpg *.jpeg *.bmp *.gif *.avif *.jxl)")[0]
                if not self.path:
                    sys.exit()
                os.chdir(os.path.dirname(self.path))
                return self.loadImage(self.path)

    def loadImage(self, path): # load image from path
        if not os.path.exists(path):
            self.scanDirectory()
            self.changeImage("next")
            return
        else:
            self.setWindowTitle(f"Hydrogen - {os.path.basename(path)}")
            if path.endswith(".avif"):
                self.pixmap = ImageQt.toqpixmap(Image.open(path, formats=["avif"]))
            elif path.endswith(".jxl"):
                self.pixmap = ImageQt.toqpixmap(Image.open(path, formats=["jxl"]))
            else:
                self.pixmap = QPixmap(path)
    
    def scanDirectory(self): # scan directory for images
            self.filepaths.clear()
            self.filepaths = [os.path.join(os.getcwd(), file) for file in os.listdir() if file.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".avif", ".jxl"))]
            self.filepaths = natsort.natsorted(self.filepaths)

    def changeImage(self, target): # change image to target image
        if not self.filepaths:
            self.scanDirectory()

        currentImageIterator = self.filepaths.index(self.path.replace("/", "\\"))
        match target:
            case "next":
                if currentImageIterator + 1 == len(self.filepaths):
                    currentImageIterator = -1
                self.loadImage(self.filepaths[currentImageIterator + 1])
                self.path = self.filepaths[currentImageIterator + 1]
            case "prev":
                self.loadImage(self.filepaths[currentImageIterator - 1])
                self.path = self.filepaths[currentImageIterator - 1]
            case "first":
                self.loadImage(self.filepaths[0])
                self.path = self.filepaths[0]
            case "last":
                self.loadImage(self.filepaths[-1])
                self.path = self.filepaths[-1]
    
        self.rotationdial.setValue(0)
        self.label.setPixmap(self.pixmap)
        if self.pixmap.width() > QGuiApplication.primaryScreen().availableGeometry().width() or self.pixmap.height() > QGuiApplication.primaryScreen().availableGeometry().height():
            self.fitImage()
        else:
            self.zoomslider.setValue(100)
        self.updateLabel()

    def updateLabel(self): # handle all label (image) transformations
        self.label.setGeometry(
            ((self.width() - (self.pixmap.width() * self.zoomslider.value() / 100)) // 2) + self.movement["x"],
            ((self.height() - (self.pixmap.height() * self.zoomslider.value() / 100)) // 2) + self.movement["y"],
            abs((self.pixmap.width() * self.zoomslider.value() / 100)*(math.cos(math.radians(self.rotationdial.value())))) + abs((self.pixmap.height() * self.zoomslider.value() / 100)*(math.sin(math.radians(self.rotationdial.value())))),
            abs((self.pixmap.height() * self.zoomslider.value() / 100)*(math.cos(math.radians(self.rotationdial.value())))) + abs((self.pixmap.width() * self.zoomslider.value() / 100)*(math.sin(math.radians(self.rotationdial.value())))))

    def resizeEvent(self, event): # handle scaling of widgets when window is resized
        self.updateLabel()
        self.zoomslider.setGeometry(self.width() - 20, 20, 20, self.height()-20)
        self.rotationdial.setGeometry(0, self.height()-75, 75, 75)
        self.nextbutton.setGeometry(self.width()-20, 0, 20, 20)
        self.prevbutton.setGeometry(self.width()-40, 0, 20, 20)

    def zoom_changed(self): # resize image when zoom slider is moved
        self.updateLabel()

    def fitImage(self): # fit image to window
        self.zoomslider.setValue(100*min(self.width()/self.pixmap.width(), self.height()/self.pixmap.height()))

    def rotate_image(self): # handle rotating image by creating a new pixmap with the rotated image using .transformed
        self.label.setPixmap(self.pixmap.transformed(QTransform().rotate(self.rotationdial.value())))
        self.updateLabel()

    def keyPressEvent(self, event: QKeyEvent): # handle key presses
        key = event.key()
        modifier = QApplication.keyboardModifiers()

        match (key, modifier):
            case (Qt.Key_R, Qt.ControlModifier):
                self.label.setPixmap(self.pixmap.transformed(QTransform().scale(1, 1)))
                self.updateLabel()
            case (Qt.Key_R, Qt.ShiftModifier):
                self.label.setPixmap(self.pixmap.transformed(QTransform().scale(1, -1)))
                self.updateLabel()
            case (Qt.Key_R, Qt.NoModifier):
                self.label.setPixmap(self.pixmap.transformed(QTransform().scale(-1, 1)))
                self.updateLabel()
            case (Qt.Key_F, Qt.NoModifier):
                self.fitImage()
            case (Qt.Key_Delete, Qt.NoModifier):
                if not self.filepaths:
                    self.scanDirectory()
                os.remove(self.path)
                self.changeImage("next")
            case (Qt.Key_H, Qt.NoModifier):
                self.UIvisibile = not self.UIvisibile
                self.nextbutton.setVisible(self.UIvisibile)
                self.prevbutton.setVisible(self.UIvisibile)
                self.zoomslider.setVisible(self.UIvisibile)
                self.rotationdial.setVisible(self.UIvisibile)
            case (Qt.Key_Q, Qt.NoModifier):
                self.helpVisible = not self.helpVisible
                self.helpPopup.setVisible(self.helpVisible)

    def eventFilter(self, source, event, drag=[False], dragstart=[None]): # handle mouse events | use default arguments to store variables in eventFilter
        if event.type() == QEvent.MouseButtonPress and source == self: # drag move start
            dragstart[0] = event.position()
            drag = True
        
        elif event.type() == QEvent.MouseMove and drag and source == self: # update image position as it's being dragged
            self.movement["x"] += event.position().x() - dragstart[0].x()   
            self.movement["y"] += event.position().y() - dragstart[0].y()
            self.updateLabel()
            dragstart[0] = event.position()

        elif event.type() == QEvent.MouseButtonRelease and source == self: 
            drag = False
            return True

        if source == self.rotationdial and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton: # reset rotation dial if right clicked
            self.rotationdial.setValue(0)
            self.updateLabel()
            return True

        if source == self and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton: # reset image position if right clicked
            self.movement = {"x": 0, "y": 0}
            self.updateLabel()
            return True
        
        if source == self.zoomslider and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton: # reset zoom slider if right clicked
            self.zoomslider.setValue(100)
            self.updateLabel()
            return True
        
        if event.type() == QEvent.Wheel and QApplication.keyboardModifiers() == Qt.ShiftModifier: # rotate image with mouse wheel
            self.rotationdial.setValue(self.rotationdial.value() + event.angleDelta().y() // 20)
            return True
        
        if source == self and event.type() == QEvent.Wheel: # zoom in/out with mouse wheel
            self.zoomslider.setValue(self.zoomslider.value() + event.angleDelta().y() // 20)
            self.movement["x"] = event.position().x() - self.width()/2 - (event.position().x() - self.width()/2) * self.zoomslider.value() / 100
            self.movement["y"] = event.position().y() - self.height()/2 - (event.position().y() - self.height()/2) * self.zoomslider.value() / 100
            self.updateLabel()
            return True
        
        if source == self.prevbutton and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            self.changeImage("first")
            return True
        
        elif source == self.nextbutton and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            self.changeImage("last")
            return True
        
        return super().eventFilter(source, event)

basewindow = MainWindow()
basewindow.show()
browser.exec()
