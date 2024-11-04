from PyQt5.QtWidgets import QWidget
from .testwidget import Ui_TestWidget

class TestWidget(QWidget):
    def __init__(self, widget=None):
        super().__init__(widget)  # 正确调用父类构造函数
        self.ui = Ui_TestWidget()
        self.ui.setupUi(self)

    def __del__(self):
        print("TestWidget is being destroyed.")
