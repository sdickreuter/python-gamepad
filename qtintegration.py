#
#   example class for integrating python-gamepad into qt
#

from PyQt5.QtCore import pyqtSlot, QThread, QMutex, QWaitCondition, pyqtSignal, QObject, QTimer
import pygamepad

class GamepadThread(QObject):
    ASignal = pyqtSignal()
    BSignal = pyqtSignal()
    XSignal = pyqtSignal()
    YSignal = pyqtSignal()

    def __init__(self, parent=None):
        if getattr(self.__class__, '_has_instance', False):
            RuntimeError('Cannot create another instance')
        self.__class__._has_instance = True
        try:
            super(GamepadThread, self).__init__(parent)
            self.abort = False
            self.thread = QThread()
            #try:
            self.pad = pygamepad.Gamepad()
            #except:
            #    print("Could not initialize Gamepad")
            #    self.pad = None
            #else:
            self.thread.started.connect(self.process)
            self.thread.finished.connect(self.stop)
            self.moveToThread(self.thread)
        except:
            (type, value, traceback) = sys.exc_info()
            sys.excepthook(type, value, traceback)

    def start(self):
        self.thread.start(QThread.HighPriority)

    @pyqtSlot()
    def stop(self):
        self.abort = True

    def check_Analog(self):
        return (self.pad.get_analogL_x(),self.pad.get_analogL_y())

    def __del__(self):
        self.__class__.has_instance = False
        try:
            self.ASignal.disconnect()
            self.BSignal.disconnect()
            self.XSignal.disconnect()
            self.YSignal.disconnect()
        except TypeError:
            pass
        self.abort = True

    def work(self):
        self.pad._read_gamepad()
        if self.pad.changed:
            if self.pad.A_was_released():
                self.ASignal.emit()
            if self.pad.B_was_released():
                self.BSignal.emit()
            if self.pad.X_was_released():
                self.XSignal.emit()
            if self.pad.Y_was_released():
                self.YSignal.emit()

    @pyqtSlot()
    def process(self):
        while not self.abort:
            try:
                self.work()
            except:
                (type, value, traceback) = sys.exc_info()
                sys.excepthook(type, value, traceback)
