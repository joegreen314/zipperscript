import unittest
import zipperscript

class testZipperscript:

	def setup(self):
		print ("Running setup")
		self.root = "/Users/joegreen/Developer/Zipper/Test/ZipperTest2"
		self.vehicle = "vehicle"
		self.show_gui = True

	def teardown(self):
		print ("Running teardown")

	def test_test():
		Zipperscript(self.root, self.vehicle, self.show_gui)