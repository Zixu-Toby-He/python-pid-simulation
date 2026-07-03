import sys
import PyQt5.QtWidgets
import PyQt5.QtCore
import PyQt5.QtGui

import numpy
import cv2

import 物理系统
import 控制系统
import 窗口界面

class 功能窗口:
	def __init__(self):
		self.窗口 = 窗口界面.PID窗口()
		self.物理量初值 = 0
		self.目标测量值 = 3200
		self.物理系统 = 物理系统.辐射耗散系统(
			物理量初值     = self.物理量初值,
			热辐射系数     = 7.247258732997091e-09,
			绝对零度电压值 = -3731.5,
			功率比例系数   = 103.16000577334333
		)

		self.Kp = self.窗口.获取数值("Kp")
		self.Ki = self.窗口.获取数值("Ki")
		self.Kd = self.窗口.获取数值("Kd")

		self.控制系统 = 控制系统.基础PID控制系统(
			Kp           = self.Kp,
			Ki           = self.Ki,
			Kd           = self.Kd,
			物理系统初态 = self.物理系统,
			目标测量值   = self.目标测量值
		)
		self.窗口.定时器绑定(self.控制模拟)
		self.窗口.定时器开始()
		self.窗口.show()

	def 控制模拟(self):
		self.窗口.刷新数值()
		if (
			(
				self.Kp,
				self.Ki,
				self.Kd,
			)
			!=
			(
				self.窗口.获取数值("Kp"),
				self.窗口.获取数值("Ki"),
				self.窗口.获取数值("Kd"),
			)
		):
			self.Kp = self.窗口.获取数值("Kp")
			self.Ki = self.窗口.获取数值("Ki")
			self.Kd = self.窗口.获取数值("Kd")
			self.物理系统 = 物理系统.辐射耗散系统(
				物理量初值     = self.物理量初值,
				热辐射系数     = 37.6045e-12,
				绝对零度电压值 = -1559.0446,
				功率比例系数   = 5.0139
			)
			self.控制系统 = 控制系统.基础PID控制系统(
				Kp           = self.Kp,
				Ki           = self.Ki,
				Kd           = self.Kd,
				物理系统初态 = self.物理系统,
				目标测量值   = self.目标测量值
			)
			曲线图 = self.控制系统.生成测量量变化曲线(控制精细度 = 100)
			self.窗口.图像显示(曲线图)
		else:
			# 数值未更新，无需刷新显示
			pass


if __name__ == "__main__":
	应用 = PyQt5.QtWidgets.QApplication(sys.argv)
	功能窗口对象 = 功能窗口()
	sys.exit(应用.exec_())