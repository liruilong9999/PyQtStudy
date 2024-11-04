# app/main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from pakeage.testpy.testpy1 import TestWidget  # 绝对导入

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test_widget = TestWidget()
    test_widget.show()

    sys.exit(app.exec_())
