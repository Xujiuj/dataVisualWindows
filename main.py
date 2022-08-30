import array
import ctypes
import inspect
import random
import sys
import threading
import time

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from pyqt_led import Led
from pyqtgraph import PlotWidget

from untitled import Ui_MainWindow


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.i = 0
        self.length = 100
        super(Window, self).__init__()
        self.setupUi(self)
        self.bind()
        self.init_warnings()
        self.init_graph()

        self.init_data([self.light_v, self.ledt_v, self.control_v, self.data_v])
        threading.TIMEOUT_MAX = 1
        self.thread_v()
        self.thread_a()
        self.thread_b()

    def bind(self):
        self.light_v_setting.clicked.connect(self.hello)
        self.light_a_setting.clicked.connect(self.hello)
        self.led_a_setting.clicked.connect(self.hello)
        self.led_v_setting.clicked.connect(self.hello)
        self.data_a_setting.clicked.connect(self.hello)
        self.data_v_setting.clicked.connect(self.hello)
        self.control_a_setting.clicked.connect(self.hello)
        self.control_v_setting.clicked.connect(self.hello)
        self.data_a_setting_3.clicked.connect(self.hello)
        # self.report.clicked.connect(self.reported)

    def set_warnings(self, led: Led):
        led.set_shape(1)
        led.set_on_color(Led.red)
        led.set_off_color(Led.green)

    def init_warnings(self):
        self.set_warnings(self.pushButton)
        self.set_warnings(self.pushButton_2)
        self.set_warnings(self.pushButton_3)
        self.set_warnings(self.pushButton_4)
        self.set_warnings(self.pushButton_5)
        self.set_warnings(self.pushButton_6)
        self.set_warnings(self.pushButton_7)
        self.set_warnings(self.pushButton_8)
        self.set_warnings(self.pushButton_10)

    def init_graph(self):
        self.light_v_show = self.set_graph(graph=self.light_v)
        self.light_a_show = self.set_graph(graph=self.light_a, y='电流/A', min=0, max=10)
        self.led_v_show = self.set_graph(graph=self.ledt_v)
        self.led_a_show = self.set_graph(graph=self.led_a, y='电流/A', min=0, max=10)
        self.data_v_show = self.set_graph(graph=self.data_v)
        self.data_a_show = self.set_graph(graph=self.data_a, y='电流/A', min=0, max=10)
        self.control_v_show = self.set_graph(graph=self.control_v)
        self.control_a_show = self.set_graph(graph=self.control_a, y='电流/A', min=0, max=10)
        self.data_bit_show = self.set_graph(graph=self.data_bit, y='数据流/bit', min=0, max=2)

    def set_graph(self, graph: PlotWidget, y='电压/V', min=160, max=250):
        graph.setBackground('w')
        graph.setLabel('left', y)
        graph.setYRange(max=max, min=min)
        graph.setXRange(min=0, max=100)
        graph.showGrid(x=True, y=True)
        curve_ = graph.plot()
        return curve_

    def reported(self):
        QMessageBox.information(self, "上报成功", "上报成功")

    # 定义槽函数
    def hello(self):
        print(self)
        self.box = QMessageBox.information(self, "设置成功", "设置成功")
        self.box.addButton('确定', QMessageBox.YesRole)
        self.box.show()

    def init_data(self, curves):
        data = array.array('i')
        self.v_data = np.zeros(self.length).__array__('d')
        self.a_data = np.zeros(self.length).__array__('d')
        bit = [0] * 19
        bit.append(2)
        self.bit = bit * 5

        for v in curves:
            v.plot().setData(self, self.v_data, 'r')
            print(v)

    def shuffle_a(self):
        count = self.i
        while True:
            value = random.random()
            if count < self.length:
                self.a_data[count] = 5 + value
                count += 1
            else:
                self.a_data[:-1] = self.a_data[1:]
                self.a_data[count - 1] = 5 + value
            if self.a_data.mean() > 5:
                # print(self.a_data[:15])
                if self.a_data[:15].mean() > self.light_warn_min_value_a.value():
                    for button in [self.pushButton_2, self.pushButton_4, self.pushButton_6, self.pushButton_8]:
                        button.turn_off()
                else:
                    for button in [self.pushButton_2, self.pushButton_4, self.pushButton_6, self.pushButton_8]:
                        button.turn_on()
                    # time.sleep(2)
            time.sleep(0.1)

    def shuffle_v(self):
        count = self.i
        while True:
            value = random.randint(-1, 1)
            out = random.randint(-50, 0)
            if out < -45:
                value = out + 40
            if count < self.length:
                self.v_data[count] = 220 + value
                count += 1
            else:
                self.v_data[:-1] = self.v_data[1:]
                self.v_data[count - 1] = 220 + value
            if self.v_data.mean() > 200:
                # print(self.v_data[:15])
                if self.v_data[:15].mean() > self.light_warn_min_value.value():
                    for button in [self.pushButton, self.pushButton_3, self.pushButton_5, self.pushButton_7]:
                        button.turn_off()
                else:
                    for button in [self.pushButton, self.pushButton_3, self.pushButton_5, self.pushButton_7]:
                        button.turn_on()
                    # time.sleep(2)
            time.sleep(0.1)

    def shuffle_bit(self):
        while True:
            self.bit[:-1], self.bit[-1] = self.bit[1:], self.bit[0]
            time.sleep(0.1)

    def new_v(self):
        for curve in [self.light_v_show, self.led_v_show, self.data_v_show, self.control_v_show]:
            curve.setData(self.v_data, pen='r')

    def new_a(self):
        for curve in [self.light_a_show, self.led_a_show, self.data_a_show, self.control_a_show]:
            curve.setData(self.a_data, pen='b')

    def new_b(self):
        self.data_bit_show.setData(self.bit, pen='y')

    def thread_v(self):
        self.th1 = threading.Thread(target=self.shuffle_v, name='led_c')
        self.th1.setDaemon(True)
        self.th1.start()
        self.timer = QTimer()
        self.timer.timeout.connect(self.new_v)
        print('do')
        self.timer.start(50)

    def thread_a(self):
        self.th2 = threading.Thread(target=self.shuffle_a, name='led_a')
        self.th2.setDaemon(True)
        self.th2.start()
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.new_a)
        self.timer2.start(50)

    def thread_b(self):
        self.th3 = threading.Thread(target=self.shuffle_bit, name='led_b')
        self.th3.setDaemon(True)
        self.th3.start()
        self.timer3 = QTimer()
        self.timer3.timeout.connect(self.new_b)
        self.timer3.start(50)

    def _async_raise(self, tid, exctype):
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def die(self):
        self.stop_thread(self.th1)
        self.stop_thread(self.th2)
        self.stop_thread(self.th3)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '警告', '<font color=red><b>是否关闭程序</b></font>',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            self.die()
        else:
            event.ignore()


if __name__ == '__main__':
    # if hasattr(sys, 'frozen'):
    #     os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
    app = QtWidgets.QApplication(sys.argv)
    myWin = Window()
    myWin.show()
    sys.exit(app.exec_())
