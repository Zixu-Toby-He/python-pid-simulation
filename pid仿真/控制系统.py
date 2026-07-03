import numpy
import cv2
import matplotlib.pyplot
import matplotlib.backends.backend_agg

class 基础PID控制系统:
	def __init__(self, Kp, Ki, Kd, 物理系统初态, 目标测量值):
		self.Kp = Kp
		self.Ki = Ki
		self.Kd = Kd
		self.物理系统   = 物理系统初态
		self.初始测量值 = 物理系统初态.测量()
		self.目标测量值 = 目标测量值
	def 生成测量量变化数据(self, 结束时刻 = 4, 控制精细度 = 64):
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
		
		return 时间轴, 状态

	def 生成测量量变化曲线(self, 结束时刻 = 4, 控制精细度 = 64, 打点 = False):
		时间轴, 状态 = self.生成测量量变化数据(
			结束时刻   = 结束时刻,
			控制精细度 = 控制精细度
		)

		matplotlib.pyplot.plot(时间轴, 状态)
		if 打点:
			matplotlib.pyplot.scatter(时间轴, 状态)
		matplotlib.pyplot.plot((0, 结束时刻), (self.目标测量值, self.目标测量值), linestyle="--")

		初始状态 = self.初始测量值
		目标状态 = self.目标测量值
		y上限 = max(5 * 初始状态 - 目标状态, 5 * 目标状态 - 初始状态) / 4
		y下限 = min(5 * 初始状态 - 目标状态, 5 * 目标状态 - 初始状态) / 4
		matplotlib.pyplot.ylim(y下限, y上限)

		# 将图形渲染到内存中的画布
		画布 = matplotlib.backends.backend_agg.FigureCanvasAgg(matplotlib.pyplot.gcf())
		画布.draw()  # 执行绘制操作
		图片RGBA = numpy.array(画布.buffer_rgba())
		图片BGR  = cv2.cvtColor(图片RGBA, cv2.COLOR_RGBA2BGR)  # RGB转BGR
		matplotlib.pyplot.clf()
		return 图片BGR
