import abc

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


# 服务于激光焊接焊盘加热
class 辐射耗散系统(物理系统):
	"""
	公式：d/dt (T - T_0) = pp * v_in - sigma * (T - T_0)**4
	物理量：温度电压
	"""
	def __init__(
			self,
			物理量初值,     # 单位：mV
			热辐射系数,     # sigma
			绝对零度电压值, # T_0
			功率比例系数,   # pp
			*args,
			**kwargs
		):
		super().__init__(物理量初值 = 物理量初值)
		self.sigma = 热辐射系数
		self.T_0   = 绝对零度电压值
		self.pp    = 功率比例系数
	@property
	def 温度(self):
		return self.物理量
	@温度.setter
	def 温度(self, 温度):
		self.物理量 = 温度
	def 系统演化(self, 输入参数, 演化时间):
		K1 = self.获取导数(self.温度,                     输入参数)
		K2 = self.获取导数(self.温度 + K1 * 演化时间 / 2, 输入参数)
		K3 = self.获取导数(self.温度 + K2 * 演化时间 / 2, 输入参数)
		K4 = self.获取导数(self.温度 + K3 * 演化时间    , 输入参数)
		self.温度 += (K1 + 2 * K2 + 2 * K3 + K4) * 演化时间 / 6
	def 获取导数(self, 温度, 激光电压):
		温度 = 温度 - self.T_0
		return self.pp * 激光电压 - self.sigma * 温度**4
	def 测量(self):
		return self.物理量
