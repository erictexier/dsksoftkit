from dsk.base.widgets.simpleqt import QtT
from dsk.base.lib.default_path import DefaultPath


class DskSplash(QtT.QtWidgets.QSplashScreen):
    """
    DskSplash screen with customizable message shown during the application startup.
    """
    def __init__(self):
        """
        Constructor. Widget is initially hidden.
        """
        image_path = DefaultPath.getIconFile("dialog_splash.png")
        super(DskSplash,self).__init__(QtT.QtGui.QPixmap(image_path))


    def set_message(self, text):
        """
        Sets the message to display on the widget.

        :param text: Text to display.
        """

        self.showMessage(text, color = QtT.QtCore.Qt.green)
        QtT.QtWidgets.QApplication.instance().processEvents()

    def show(self):
        """
        Shows the dialog of top of all other dialogs.
        """
        QtT.QtWidgets.QDialog.show(self)
        self.raise_()
        self.activateWindow()

    def hide(self):
        """
        Hides the dialog and clears the current message.
        """
        # There's no sense showing the previous message when we show the
        # splash next time.
        self.set_message("")
        QtT.QtWidgets.QDialog.hide(self)