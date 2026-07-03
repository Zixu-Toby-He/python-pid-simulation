import abc

import sys
import PyQt5.QtWidgets
import PyQt5.QtCore
import PyQt5.QtGui


import matplotlib.pyplot
import matplotlib.backends.backend_agg
import numpy
import cv2

class 物理系统(abc.ABC):
	def __init__(self, 物理量初值, *args, **kwargs):
		self.物理量 = 物理量初值
	@abc.abstractmethod
	def 系统演化(self, 输入参数, 演化时间):
		pass
	def 测量(self):
		return self.物理量

class 零延迟传递系统(物理系统):
	def __init__(self, 物理量初值, *args, **kwargs):
		super().__init__(物理量初值 = 物理量初值)
	def 系统演化(self, 输入参数, 演化时间):
		self.物理量 = 输入参数
	def 测量(self):
		return self.物理量

class 延迟传递系统(物理系统):
	def __init__(self, 物理量初值, 计时周期, *args, **kwargs):
		super().__init__(物理量初值 = 物理量初值)
		self.计时     = 0
		self.计时周期 = 计时周期
	def 系统演化(self, 输入参数, 演化时间):
		self.计时 += 演化时间
		if (self.计时 > self.计时周期):
			self.计时 -= self.计时周期
			self.物理量 = 输入参数
	def 测量(self):
		return self.物理量

class 积分系统(物理系统):
	def __init__(self, 物理量初值, *args, **kwargs):
		super().__init__(物理量初值 = 物理量初值)
	def 系统演化(self, 输入参数, 演化时间):
		self.物理量 += (输入参数 * 演化时间)
	def 测量(self):
		return self.物理量

class 耗散积分系统(物理系统):
	def __init__(self, 物理量初值, 耗散系数, *args, **kwargs):
		super().__init__(物理量初值 = 物理量初值)
		self.耗散系数 = 耗散系数
	def 系统演化(self, 输入参数, 演化时间):
		self.物理量  += (输入参数 - self.耗散系数 * self.物理量) * 演化时间
	def 测量(self):
		return self.物理量

class PID控制系统:
	def __init__(self, Kp, Ki, Kd, 物理系统初态, 目标测量值):
		self.Kp = Kp
		self.Ki = Ki
		self.Kd = Kd
		self.物理系统   = 物理系统初态
		self.目标测量值 = 目标测量值
	def 生成控制曲线图(self, 结束时刻 = 4, 控制精细度 = 64, 打点 = False):
		间隔数 = 控制精细度 * 结束时刻
		时间轴 = numpy.linspace(0, 4, 间隔数 + 1)
		
		比例 = numpy.empty(shape=(间隔数 + 1,), dtype=numpy.float64)
		积分 = numpy.empty(shape=(间隔数 + 1,), dtype=numpy.float64)
		微分 = numpy.empty(shape=(间隔数 + 1,), dtype=numpy.float64)
		状态 = numpy.empty(shape=(间隔数 + 1,), dtype=numpy.float64)

		状态[0] = self.物理系统.测量() # 初始过程变量
		比例[0] = self.目标测量值 - 状态[0]
		积分[0] = 0
		微分[0] = 0

		for j in range(1, 间隔数 + 1):
			时间间隔 = 时间轴[j] - 时间轴[j - 1]  # 时间步长

			比例[j] = self.目标测量值 - 状态[j - 1]
			积分[j] = 积分[j - 1] + (比例[j - 1] + 比例[j]) * 时间间隔 / 2
			微分[j] = (比例[j] - 比例[j - 1]) / 时间间隔

			PID输出  = self.Kp * 比例[j] + self.Ki * 积分[j] + self.Kd * 微分[j]
			
			if (PID输出 < 0):
				PID输出 = 0

			self.物理系统.系统演化(PID输出, 时间间隔) # 传递函数
			状态[j] = self.物理系统.测量()

		matplotlib.pyplot.plot(时间轴, 状态)
		if 打点:
			matplotlib.pyplot.scatter(时间轴, 状态)
		matplotlib.pyplot.plot((0, 结束时刻), (self.目标测量值, self.目标测量值), linestyle="--")

		初始状态 = 状态[0]
		目标状态 = self.目标测量值
		y上限 = max(5 * 初始状态 - 目标状态,5 * 目标状态 - 初始状态) / 4
		y下限 = min(5 * 初始状态 - 目标状态,5 * 目标状态 - 初始状态) / 4

		matplotlib.pyplot.ylim(y下限, y上限)

		# 将图形渲染到内存中的画布
		画布 = matplotlib.backends.backend_agg.FigureCanvasAgg(matplotlib.pyplot.gcf())
		画布.draw()  # 执行绘制操作
		图片RGBA = numpy.array(画布.buffer_rgba())
		图片BGR  = cv2.cvtColor(图片RGBA, cv2.COLOR_RGBA2BGR)  # RGB转BGR
		matplotlib.pyplot.cla()
		return 图片BGR

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
		
		self.信息标签 = PyQt5.QtWidgets.QLabel()
		self.信息标签.setFont(PyQt5.QtGui.QFont("Consolas", 20))
		self.信息标签.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
		信息布局.addWidget(self.信息标签)
		
		# 下方颜色显示区 - 使用QGraphicsView
		self.颜色显示区 = PyQt5.QtWidgets.QGraphicsView()
		self.颜色显示区.setRenderHint(PyQt5.QtGui.QPainter.Antialiasing)
		
		# 创建图形场景
		self.场景 = PyQt5.QtWidgets.QGraphicsScene()
		self.颜色显示区.setScene(self.场景)

		# 初始黑色图像
		self.当前图像 = numpy.zeros((700, 850, 3), dtype=numpy.uint8)
		self.图像显示()
		
		# 添加到右侧布局
		右侧布局.addWidget(信息面板)
		右侧布局.addWidget(self.颜色显示区, 1)
		
		# 将左右面板添加到主布局
		主布局.addWidget(左侧面板)
		主布局.addWidget(右侧面板, 1)
		
		# 设置定时器更新显示
		self.定时器 = PyQt5.QtCore.QTimer(self)
		display = lambda :self.刷新()
		self.定时器.timeout.connect(display)
		self.定时器.start(100)  # 每100毫秒刷新一次

	def 刷新(self):
		self.绘图更新()
		self.滑条状态更新()


	def 滑条状态更新(self):
		for 条目 in self.PID控件管理字典.keys():
			上限设置 = self.PID控件管理字典[条目]["上限控件"]
			滑块     = self.PID控件管理字典[条目]["滑块控件"]
			下限设置 = self.PID控件管理字典[条目]["下限控件"]
			上限 = 上限设置.value()
			下限 = 下限设置.value()
			滑条上限 = int(上限 * self.滑条精密度)
			滑条下限 = int(下限 * self.滑条精密度)
			上限 = 滑条上限 / self.滑条精密度
			下限 = 滑条下限 / self.滑条精密度
			滑块.setRange(滑条下限, 滑条上限)
			上限设置.setRange(下限 + 1, 1000)
			下限设置.setRange(-1000,    上限 - 1)


	def 图像显示(self):
		"""将OpenCV图像显示在QGraphicsView中"""
		# 将OpenCV图像转换为Qt图像
		高度, 宽度, 通道 = self.当前图像.shape
		单行字节数 = 通道 * 宽度
		QT图像 = PyQt5.QtGui.QImage(
			self.当前图像.data, 
			宽度, 
			高度, 
			单行字节数, 
			PyQt5.QtGui.QImage.Format_BGR888
		)
		QT点阵     = PyQt5.QtGui.QPixmap.fromImage(QT图像)
		像素图元   = PyQt5.QtWidgets.QGraphicsPixmapItem(QT点阵)
		
		# 清除场景并添加新图像
		self.场景.clear()
		self.场景.addItem(像素图元)

	def 绘图更新(self):
		新值 = (
			self.PID控件管理字典["Kp"]["滑块控件"].value() / self.滑条精密度,
			self.PID控件管理字典["Ki"]["滑块控件"].value() / self.滑条精密度,
			self.PID控件管理字典["Kd"]["滑块控件"].value() / self.滑条精密度,
		)

		旧值 = (
			self.PID控件管理字典["Kp"]["当前值"],
			self.PID控件管理字典["Ki"]["当前值"],
			self.PID控件管理字典["Kd"]["当前值"]
		)

		if (新值 == 旧值):
			return
		else:
			Kp, Ki, Kd = 新值
			self.PID控件管理字典["Kp"]["当前值"] = Kp
			self.PID控件管理字典["Ki"]["当前值"] = Ki
			self.PID控件管理字典["Kd"]["当前值"] = Kd
			
			# 更新提示区文本
			信息文本  = f"Kp: {Kp}         Ki: {Ki}         Kd: {Kd}"
			self.信息标签.setText(信息文本)
			
			初始状态   = 0
			目标测量值 = 1
			物理系统   = 延迟传递系统(初始状态, 计时周期 = 0.125)
			#物理系统   = 零延迟传递系统(初始状态)
			控制系统   = PID控制系统(Kp, Ki, Kd, 物理系统, 目标测量值)
			self.当前图像 = 控制系统.生成控制曲线图()

			缩放比例 = min(
				(self.颜色显示区.width()  - 2)  / self.当前图像.shape[1],
				(self.颜色显示区.height() - 2)  / self.当前图像.shape[0]
			)
			self.当前图像 = cv2.resize(self.当前图像, dsize=None, fx=缩放比例, fy=缩放比例)
			# 更新图像显示
			self.图像显示()

if __name__ == "__main__":
	应用 = PyQt5.QtWidgets.QApplication(sys.argv)
	窗口 = PID窗口()
	窗口.show()
	sys.exit(应用.exec_())