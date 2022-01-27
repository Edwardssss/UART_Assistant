# 静态import
import sys
import serial
import serial.tools.list_ports
# 动态import
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, hex_
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from Uart_UI import Ui_MainWindow

# 设置应用名称
App_name = "串口收发助手"


# 开始定义类
class UART_serial(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(UART_serial, self).__init__()
        self.setupUi(self)
        self.setWindowTitle(App_name)
        self.Uart_serial = serial.Serial()
        self.uart_refresh()
        self.init()
        self.clear_num()

        # 接收和发送数据置零
        self.data_num_received = 0
        self.Rx_lcdNumber.setDigitCount(10)  # 等待10ms
        self.Rx_lcdNumber.display(self.data_num_received)  # 显示数据
        self.data_num_transmit = 0
        self.Tx_lcdNumber.setDigitCount(10)  # 等待10ms
        self.Tx_lcdNumber.display(self.data_num_transmit)  # 显示数据
        self.data_num_received = 0
        self.data_num_sent = 0

    def init(self):
        self.pushButton_refresh.clicked.connect(self.uart_refresh)  # 关联刷新串口按钮
        self.pushButton_open.clicked.connect(self.uart_open)  # 关联打开串口按钮
        self.pushButton_send.clicked.connect(self.send_data)  # 关联发送按钮
        self.timer = QTimer(self)  # 定时器接收数据
        self.timer.timeout.connect(self.receive_data)
        self.pushButton_clear.clicked.connect(self.clear_num)
        self.setWindowIcon(QIcon('Teri.ico'))

    def uart_refresh(self):
        self.Com_Dict = {}  # 创建一个空字典来准备存放串口的信息
        port_list = list(serial.tools.list_ports.comports())  # 创建一个列表来存放串口信息
        self.comboBox_uart.clear()
        # 遍历列表，存放串口数据到字典中
        for port in port_list:
            self.Com_Dict["%s" % port[1]] = "%s" % port[0]
            self.comboBox_uart.addItem(port[1])
        # 判断字典内的串口数量是否为0
        if len(self.Com_Dict) == 0:
            self.comboBox_uart.setCurrentText("")
            self.pushButton_open.setEnabled(False)
            # 若为0，则关闭发送按钮
        else:
            self.pushButton_open.setEnabled(True)
            # 若不为0，则打开发送按钮

    def uart_open(self):
        if self.pushButton_open.text() == '打开串口':
            self.Uart_serial.port = self.Com_Dict[self.comboBox_uart.currentText()]  # 设置端口
            self.Uart_serial.baudrate = int(self.comboBox_baud.currentText())  # 设置波特率，强制转化为int
            self.Uart_serial.bytesize = int(self.comboBox_data.currentText())  # 设置数据位，强制转化为int
            self.Uart_serial.stopbits = int(self.comboBox_stop.currentText())  # 设置停止位，强制转化为int
            self.Uart_serial.parity = self.comboBox_check.currentText()  # 设置校验位
            # 尝试打开串口
            try:
                self.Uart_serial.open()
            except:
                QMessageBox.warning(self, "错误", "无法打开串口！")  # 自定义错误：无法打开串口
                return
            if self.Uart_serial.isOpen():
                self.pushButton_open.setText('关闭串口')
                # 打开串口接收定时器，周期为10ms
                self.timer.start(10)
        else:
            self.timer.stop()  # 关闭串口定时器
            try:
                self.Uart_serial.close()
            except:
                QMessageBox.warning(self, "错误", "无法关闭串口！")  # 自定义错误：无法关闭串口

            if not self.Uart_serial.isOpen():
                self.pushButton_open.setText('打开串口')

    def send_data(self):
        if self.Uart_serial.isOpen():
            send_data = self.tx_plainTextEdit.toPlainText()
            send_data = send_data.encode('UTF-8')  # 发送格式为UTF-8
            send_count = self.Uart_serial.write(send_data)
            self.data_num_sent += send_count
            self.Tx_lcdNumber.display(self.data_num_sent)

    def receive_data(self):
        if self.Uart_serial.isOpen():
            try:
                number_count = self.Uart_serial.inWaiting()
            except:
                self.timer.stop()
                self.Uart_serial.close()
                self.pushButton_open.setText('打开串口')
                return
            if number_count > 0:
                data = self.Uart_serial.read(number_count)
                if self.comboBox_decode.currentText() == "HEX":
                    rev_data = ''
                    for i in range(0, len(data)):
                        rev_data = rev_data + '{:02X}'.format(data[i]) + ' '
                        self.rx_textBrowser.insertPlainText(rev_data)
                else:
                    self.rx_textBrowser.insertPlainText(data.decode('UTF-8'))
                # 统计接收字符的数量
                self.data_num_received += number_count
                self.Rx_lcdNumber.display(self.data_num_received)

                # 获取到text光标
                textCursor = self.rx_textBrowser.textCursor()
                # 滚动到底部
                textCursor.movePosition(textCursor.End)
                # 设置光标到text中去
                self.rx_textBrowser.setTextCursor(textCursor)

    def clear_num(self):
        self.data_num_sent = 0  # 发送量清零
        self.Tx_lcdNumber.display(self.data_num_sent)  # 显示零发送量
        self.tx_plainTextEdit.clear()  # 清空发送框
        self.data_num_received = 0  # 接收量清零
        self.Rx_lcdNumber.display(self.data_num_received)  # 显示零接收量
        self.rx_textBrowser.clear()  # 清空接收框


# 主程序开始
if __name__ == '__main__':
    # 实例化
    app_window = QtWidgets.QApplication(sys.argv)
    uart_RxTx = UART_serial()
    # 显示窗口
    uart_RxTx.show()
    sys.exit(app_window.exec_())
