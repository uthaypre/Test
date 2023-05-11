"""
2nd Try
This script tries to combine all of the different scripts into ONE complete script.
"""
import sys, traceback
import os.path
import matplotlib.pyplot as plt
from pypylon import pylon
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import math
import time
import numpy as np

#########################################
# LCD middle postition
global x_LCD, y_LCD

# Variables for data
global x
global value
global direct

x = 65 # number of pictures/ shifts
value = list() # average pixel value of image (single value)
direct = True  # direction: False = vertical ; True = horizontal

print("where am i")

class CameraReader(QObject):
    start_measurement_trigger = pyqtSignal()
    img_acquisition_finished = pyqtSignal()
    
    
    NumberOfPictures = x
    i = 1

    def grabImage(self, i):
        print("is this narnia?")
        
        cam_obj.Open() 
        cam_obj.ExposureTime.SetValue(502714/2)  # 100'000 microsecond                                   # start communication with device
        cam_obj.StartGrabbing(1)                         # int argument for number of frames we want to aquire
        grab = cam_obj.RetrieveResult(2000, pylon.TimeoutHandling_Return)
        if grab.GrabSucceeded():
            cv_img = grab.GetArray()
        
        value.append(np.mean(cv_img)) # average pixel value of each image (single value for each image)
        cam_obj.Close()
        
    
    @pyqtSlot()
    def startMeasurement(self):
        print("Step 3")
        print("     Start taking pictures")
        print("     Open Widget for Filter Lightsource")
        self.start_measurement_trigger.emit()

    @pyqtSlot()
    def takePicture(self):
        print("or is it the upside down?")
        if self.i < self.NumberOfPictures:
            self.grabImage(self.i)
            self.start_measurement_trigger.emit()
            self.i = self.i + 1
        elif self.i == self.NumberOfPictures:
            self.grabImage(self.i)
            self.img_acquisition_finished.emit()
        else:
            print("something went wrong")
            self.img_acquisition_finished.emit()

   
class DisplayWidget(QWidget):
    print("what should i do")
    next_pattern_trigger = pyqtSignal()
    
    h = 480                 # Pixel in y-direction
    w = 800                 # pixel in x-direction
    
    NumberOfShifts = x
    width_stripe = 15
    if direct == False:
        StartPosition = int((w-x)/2-(math.ceil(width_stripe/2)))
    elif direct == True:
        StartPosition = int((h-x)/2-(math.ceil(width_stripe/2)))
    j = 1
    # print('que passa')
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupDisplay()

    def setupDisplay(self):
        print("the DEMAGORGON is here")
        self.app = QApplication.instance() # accesses the QApplication object
        print("ATTACK")
        # Get avaliable screens/monitors
        # https://doc.qt.io/qt-5/qscreen.html
        # Get info on selected screen
        self.selected_screen = 1  # Select the desired monitor/screen

        self.screens_available = self.app.screens()
        
        self.screen = self.screens_available[self.selected_screen]
        self.screen_width = self.screen.size().width()
        self.screen_height = self.screen.size().height()

        # Create a black image for init
        self.pixmap = QPixmap(self.screen_width, self.screen_height)
        self.pixmap.fill(QColor("black"))

        # Create QLabel object
        self.app_widget = QLabel()

        # Varioius flags that can be applied to make displayed window frameless, fullscreen, etc...
        # https://doc.qt.io/qt-5/qt.html#WindowType-enum
        # https://doc.qt.io/qt-5/qt.html#WidgetAttribute-enum
        self.app_widget.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowDoesNotAcceptFocus
            | Qt.WindowStaysOnTopHint
        )
        # Hide mouse cursor
        self.app_widget.setCursor(Qt.BlankCursor)

        # set geometry to the screen geometry
        self.app_widget.setGeometry(
            self.screen.geometry()
        )  # Set the size of Qlabel to size of the screen
        self.app_widget.setWindowTitle("myImageDisplayApp")
        self.app_widget.setAlignment(
            Qt.AlignLeft | Qt.AlignTop
        )  # https://doc.qt.io/qt-5/qt.html#AlignmentFlag-enum
        self.app_widget.setPixmap(self.pixmap)

        self.app_widget.showFullScreen()
        # Set the screen on which widget is on        
        self.app_widget.windowHandle().setScreen(self.screen)
        print("Hey, What you doin?")
    
        

    @pyqtSlot()
    def showPattern(self):
        if direct == False:
            I = np.zeros((self.h, self.w, 3), dtype=np.uint8)
            I[:,self.StartPosition+(self.j-1):self.StartPosition+(self.j-1)+self.width_stripe] = [0, 255, 0]
            print("que vert")
        elif direct == True:
            I = np.zeros((self.h, self.w, 3), dtype=np.uint8)
            I[self.StartPosition+(self.j-1):self.StartPosition+(self.j-1)+self.width_stripe,:] = [0, 255, 0]
            print("que horiz")
        pixmap = QPixmap(self.array2Pixmap(I))
        self.app_widget.setPixmap(pixmap)
        self.j = (self.j+1)
        #if self.j == 0:
        #    self.j = 1
        self.next_pattern_trigger.emit()
        # self.sig_new_pic.emit()
        

    @pyqtSlot()
    def computeCoords(self):
        print("what is life")
        # quit application after to 1 secons
        # Data for plotting
        t = np.arange(self.StartPosition+math.ceil(self.width_stripe/2), self.StartPosition+math.ceil(self.width_stripe/2)+x, 1)
        s = value
        indices = [index for index, item in enumerate(s) if item == max(s)]
        with open('LCD_zero_position.txt', 'w') as f:
            if direct == True:
                y_LCD = self.StartPosition+math.ceil(self.width_stripe/2)+np.array(indices)
                print(y_LCD)
                f.write(f'y-coordinate:\n{y_LCD}')
                self.finished.emit()
            elif direct == False:
                x_LCD = self.StartPosition+math.ceil(self.width_stripe/2)+np.array(indices)
                print(x_LCD)
                f.write(f'x-coordinate:\n{x_LCD}')
                self.finished.emit()
        
        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(t, s, linewidth=3)
        plt.axvline(x=401, ls=':', lw=3)
        plt.xlabel('Pixel in x-direction',fontsize=16)
        plt.ylabel('Greyscale level',fontsize=16)
        plt.tick_params(axis='both',  labelsize=16)
        plt.xlim([375, 425])
        
        ax.grid()
        
        #fig.savefig("test.png")
        plt.show()
        
        QTimer.singleShot(1 * 1000, QApplication.quit)
    
    def array2Pixmap(self,img):
        print("RUN")
        w,h,ch = img.shape
        # Convert resulting image to pixmap
        if img.ndim == 1:
            img =  cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        qimg = QImage(img.data, h, w, 3*h, QImage.Format_RGB888) 
        qpixmap = QPixmap(qimg)

        return qpixmap
#########################################
    
class ZeroMeasureThread(QThread):
    print("are we done yet?")
    finished = pyqtSignal()
    def run(self):
        
        ######
        print("Step 2")
        print("     Start Zero Measurement")
        display = DisplayWidget()
        print("THere is an inbetween")
        camera = CameraReader()
        
        camera.start_measurement_trigger.connect(display.showPattern)
        display.next_pattern_trigger.connect(camera.takePicture)
        camera.img_acquisition_finished.connect(display.computeCoords)
        
        # start task 1
        QTimer.singleShot(0, camera.startMeasurement) 
        
        
        print('ok')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        
        self.label = QLabel("Press here if you want to start the measurement:")
        self.setWindowTitle("Lens Measurement")
        self.startbutton = QPushButton("Start")
        
        self.startbutton.clicked.connect(self.zero_measure_msg)
        
        layout.addWidget(self.label, 6,7)
        layout.addWidget(self.startbutton, 7, 7, 8, 8)
        
        w = QWidget()
        w.setLayout(layout)
        
        self.setCentralWidget(w)
        
        self.show()
        
    def zero_measure_msg(self):
        dialog = QDialog(self)
        
        dialog.setWindowTitle("LCD Zero Measurement")
        dialog.setModal(True)
        path = r"C:\Users\utha\Documents\SVN\IAMP_Lensprinter\trunk\Software\PhaseShiftingSchlieren\LCD_zero_position.txt"
        layout = QGridLayout(dialog)
        if os.path.isfile(path):
            label = QLabel("There are old zero coordinates available. You only need to redo them if you changed the setup. Do you want to redo it?")
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(self.start_zero_measure)
            button_box.rejected.connect(self.start_measurement)
            
        else:
            label = QLabel("There are no old zero coordinates available. You need to determine them first.")
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(self.start_zero_measure)

        layout.addWidget(button_box, 7,7)
        layout.addWidget(label,6,7)
        dialog.exec()
    def start_zero_measure(self):
        print('Redo zero measurement')
        self.thread = ZeroMeasureThread()
        self.thread.finished.connect(self.zero_measure_finished)
        self.thread.start()
        
    def zero_measure_finished(self):
        self.thread.quit()
        self.thread.wait()
        del self.thread
        QApplication.quit()
    def start_measurement(self):
        print("next step")
        QApplication.quit()

if __name__ == "__main__":
    print("start camera here")
    print("Step 1")
    print("     Connect Basler camera")
    tl_factory = pylon.TlFactory.GetInstance()      # getting transport layer
    devices = tl_factory.EnumerateDevices()          
    for device in devices:
        print(device.GetFriendlyName())
    cam_obj = pylon.InstantCamera()                  # creating InstantCamera object
    cam_obj.Attach(tl_factory.CreateFirstDevice())   # connection between object and device via attach 

    app = QApplication(sys.argv)
    window = MainWindow()

    app.exec()
    sys.exit(app.exec())