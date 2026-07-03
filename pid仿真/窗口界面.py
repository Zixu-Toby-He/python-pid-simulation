import typing

import numpy
import cv2

import PyQt5.QtWidgets
import PyQt5.QtCore
import PyQt5.QtGui


class PID窗口(PyQt5.QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("PID仿真测试器")
		self.setGeometry(100, 100, 1200, 900)
		
		# 创建主窗口部件
		主部件 = PyQt5.QtWidgets.QWidget()
		self.setCentralWidget(主部件)
		
		# 主水平布局（左右分区）
		主布局 = PyQt5.QtWidgets.QHBoxLayout(主部件)
		主布局.setContentsMargins(10, 10, 10, 10)
		主布局.setSpacing(20)
		
		# 左侧区域（RGB控制）
		左侧面板 = PyQt5.QtWidgets.QFrame()
		左侧面板.setFixedWidth(300)
		左侧布局 = PyQt5.QtWidgets.QVBoxLayout(左侧面板)
		左侧布局.setSpacing(10)
		
		# 创建滑块布局
		初始范围 = 1
		self.滑条精密度   = 10000
		self.PID控件管理字典 = {}
		标题布局 = PyQt5.QtWidgets.QHBoxLayout()
		滑块布局 = PyQt5.QtWidgets.QHBoxLayout()
		for 条目 in ['Kp', 'Ki', 'Kd']:
			标题标签 = PyQt5.QtWidgets.QLabel(条目)
			标题标签.setFont(PyQt5.QtGui.QFont("Arial", 18, PyQt5.QtGui.QFont.Bold))
			标题标签.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
			标题布局.addWidget(标题标签)

			# 滑块容器
			滑块容器 = PyQt5.QtWidgets.QVBoxLayout()
			滑块容器.setSpacing(5)
			
			# 垂直滑块 - 延长高度
			滑块 = PyQt5.QtWidgets.QSlider(PyQt5.QtCore.Qt.Vertical)
			滑块.setRange(0, self.滑条精密度 * 初始范围)
			滑块.setValue(0)
			滑块.setTickPosition(PyQt5.QtWidgets.QSlider.TicksBothSides)
			滑块.setTickInterval(10)
			滑块.setMinimumHeight(750)  # 延长滑块高度
			
			# 滑块上下限标签
			上限设置 = PyQt5.QtWidgets.QDoubleSpinBox()
			上限设置.setSingleStep(1)
			上限设置.setValue(初始范围)
			上限设置.setRange(初始范围 / 2, 1000)
			上限设置.setFont(PyQt5.QtGui.QFont("Times New Roman", 14))
			上限设置.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

			下限设置 = PyQt5.QtWidgets.QDoubleSpinBox()
			下限设置.setSingleStep(1)
			下限设置.setValue(0)
			下限设置.setRange(-1000, 初始范围 / 2)
			下限设置.setFont(PyQt5.QtGui.QFont("Times New Roman", 14))
			下限设置.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

			# 滑块样式
			样式 = f"""
				QSlider::groove:vertical {{
					border: 1px solid #999999;
					width: 30px;
					background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
					stop:0 {'#ff0000' if 条目=='Kp' else '#00ff00' if 条目=='Ki' else '#0000ff'}, 
					stop:1 #000000);
					margin: 0px;
				}}
				QSlider::handle:vertical {{
					background: #ffffff;
					border: 1px solid #5c5c5c;
					height: 30px;
					width: 40px;
					margin: -5px 0;
					border-radius: 3px;
				}}
			"""
			滑块.setStyleSheet(样式)
			
			# 将滑块和标签存储到字典
			self.PID控件管理字典[条目] = {
				"标签控件": 标题标签,
				"上限控件": 上限设置,
				"滑块控件": 滑块,
				"下限控件": 下限设置,
				"当前值": None, # 初始状态下需要更新一次图像
			}
			
			# 添加到容器
			滑块容器.addWidget(上限设置, 2, PyQt5.QtCore.Qt.AlignCenter)
			滑块容器.addWidget(滑块,     1, PyQt5.QtCore.Qt.AlignCenter)
			滑块容器.addWidget(下限设置, 0, PyQt5.QtCore.Qt.AlignCenter)
			
			# 添加到滑块布局
			滑块布局.addLayout(滑块容器)
		左侧布局.addLayout(标题布局)
		左侧布局.addLayout(滑块布局)
		
		# 右侧区域（显示区）
		右侧面板 = PyQt5.QtWidgets.QWidget()
		右侧布局 = PyQt5.QtWidgets.QVBoxLayout(右侧面板)
		右侧布局.setSpacing(20)
		
		# 上方提示区
		信息面板 = PyQt5.QtWidgets.QFrame()
		信息面板.setFrameShape(PyQt5.QtWidgets.QFrame.StyledPanel)
		信息面板.setMinimumHeight(150)
		信息布局 = PyQt5.QtWidgets.QVBoxLayout(信息面板)
		信息布局.setSpacing(20)

		标题布局   = PyQt5.QtWidgets.QHBoxLayout()
		数字框布局 = PyQt5.QtWidgets.QHBoxLayout()
		for 条目 in ['Kp', 'Ki', 'Kd']:
			标题标签 = PyQt5.QtWidgets.QLabel(条目)
			标题标签.setFont(PyQt5.QtGui.QFont("Consolas", 20))
			标题标签.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
			标题布局.addWidget(标题标签)

			数字框控件 = PyQt5.QtWidgets.QDoubleSpinBox()
			数字框控件.setRange(0, 初始范围)
			数字框控件.setValue(0)
			数字框控件.setDecimals(4)
			数字框控件.setFont(PyQt5.QtGui.QFont("Times New Roman" , 20))
			数字框控件.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

			# 将滑块和标签存储到字典
			self.PID控件管理字典[条目]["数字框控件"] = 数字框控件

			# 添加到容器
			数字框布局.addWidget(数字框控件, 0, PyQt5.QtCore.Qt.AlignCenter)
		信息布局.addLayout(标题布局)
		信息布局.addLayout(数字框布局)
		
		# 下方颜色显示区 - 使用QGraphicsView
		self.显示区 = PyQt5.QtWidgets.QGraphicsView()
		self.显示区.setRenderHint(PyQt5.QtGui.QPainter.Antialiasing)
		
		# 创建图形场景
		self.场景 = PyQt5.QtWidgets.QGraphicsScene()
		self.显示区.setScene(self.场景)

		# 初始黑色图像
		self.图像显示(numpy.zeros((self.显示区.height() - 2, self.显示区.width() - 2, 3), dtype=numpy.uint8))

		# 添加到右侧布局
		右侧布局.addWidget(信息面板)
		右侧布局.addWidget(self.显示区, 1)
		
		# 将左右面板添加到主布局
		主布局.addWidget(左侧面板)
		主布局.addWidget(右侧面板, 1)
		
		# 设置定时器更新显示
		self.定时器 = PyQt5.QtCore.QTimer(self)
		num_refresh = lambda :self.刷新数值()
		self.定时器.timeout.connect(num_refresh)
		self.定时器.start(100)  # 每100毫秒刷新一次

	def 获取数值(self, 变量名称: typing.Literal["Kp","Ki","Kd"]):
		return self.PID控件管理字典[变量名称]["当前值"]

	def 刷新数值(self):
		for 条目 in self.PID控件管理字典.keys():
			# 刷新范围
			上限设置 = self.PID控件管理字典[条目]["上限控件"]
			滑块     = self.PID控件管理字典[条目]["滑块控件"]
			数字框   = self.PID控件管理字典[条目]["数字框控件"]
			下限设置 = self.PID控件管理字典[条目]["下限控件"]
			
			上限 = 上限设置.value()
			下限 = 下限设置.value()
			滑条上限 = int(上限 * self.滑条精密度)
			滑条下限 = int(下限 * self.滑条精密度)
			上限 = 滑条上限 / self.滑条精密度
			下限 = 滑条下限 / self.滑条精密度

			滑块.setRange(滑条下限, 滑条上限)
			数字框.setRange(下限,上限)
			上限设置.setRange(下限 + 1, 1000)
			下限设置.setRange(-1000,    上限 - 1)

			# 刷新数值
			当前值 = self.PID控件管理字典[条目]["当前值"]
			滑块值 = self.PID控件管理字典[条目]["滑块控件"].value() / self.滑条精密度
			数框值 = self.PID控件管理字典[条目]["数字框控件"].value()
			if   ((当前值 == 滑块值) and (当前值 == 数框值)):
				# 无修改情况，无需更新
				pass
			elif (当前值 != 滑块值):
				数字框.setValue(滑块值)
				self.PID控件管理字典[条目]["当前值"] = 滑块值
			elif (当前值 != 数框值):
				滑块.setValue(int(数框值 * self.滑条精密度))
				self.PID控件管理字典[条目]["当前值"] = 数框值
			else:
				raise ValueError("未知情况，{}：({}, {}, {})".format(条目, 当前值, 滑块值, 数框值))

	def 图像显示(self, 图像):
		高度, 长度, 通道数 = 图像.shape
		缩放比例 = min(
			(self.显示区.width()  - 2)  / 长度,
			(self.显示区.height() - 2)  / 高度,
		)
		图像 = cv2.resize(图像, dsize=None, fx=缩放比例, fy=缩放比例)
		高度, 长度, 通道数 = 图像.shape

		单行字节数 = 通道数 * 长度
		QT图像 = PyQt5.QtGui.QImage(
			图像.data, 
			长度,
			高度,
			单行字节数, 
			PyQt5.QtGui.QImage.Format_BGR888
		)
		QT点阵     = PyQt5.QtGui.QPixmap.fromImage(QT图像)
		像素图元   = PyQt5.QtWidgets.QGraphicsPixmapItem(QT点阵)

		# 清除场景并添加新图像
		self.场景.clear()
		self.场景.addItem(像素图元)

	def 定时器绑定(self, 函数):
		func = lambda: 函数()
		self.定时器.timeout.connect(func)
	
	def 定时器开始(self, 周期ms = 100):
		self.定时器.start(周期ms)