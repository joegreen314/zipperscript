import unittest
import zipperscript as z
from collections import namedtuple

class testZipperscript:

	def setup(self):
		print ("Running setup")
		self.root = "/Users/joegreen/Developer/Zipper/Test/ZipperTest2"
		self.vehicle = "vehicle"
		self.show_gui = False

	def teardown(self):
		print ("Running teardown")

	def create_test_files(self, files):
		#files: named tuple of named tuples and strings, representing directories and files.
		


	def test_test(self):
		route1 = D("ROUTE01", [
				f("ROUTE01.txt"),
				f("ROUTE01.rtf"),
				f("ROUTE01.rut"),
				f("ROUTE01.gps"),
				f("ROUTE01.raw"),
				f("ROUTE01.log"),
				f("ROUTE01.rdf"),
				f("ROUTE01.rsp"),
				f("ROUTE01.hdlg"),
				f("ROUTE01.iri"),
				f("ROUTE01.badext")])
		pospac1 = d("1234567_1234", [route1, f("1234567_1234.000")])
		date1 = d("Todays_date", [pospac1])

		self.create_test_files(self, self.root, date1)
		z.ZipperScript(self.root, self.vehicle, self.show_gui)

class F(nametuple):
	def __init__(self, name, contents = ""):
		self.name = name
		self.contents = contents

class D(namedtuple):
	def __init__(self, name, contents):
		self.name = name
		self.contents = contents
