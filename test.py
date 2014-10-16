from copy import deepcopy
class Foo():
	def __init__(self, aaa=[]):
		print aaa
		self.a = deepcopy(aaa)

f1 = Foo()
f1.a.append("stuff")
f2 = Foo()