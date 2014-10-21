from __future__ import division
import unittest, string, random
import zipperscript as z
import shutil, zipfile, os, sys, copy
from collections import namedtuple

class testZipperscript:

    def setup(self):
        print ("Running setup")
        self.root = "/Users/joegreen/Developer/Zipper/Test"
        self.vehicle = "vehicle"
        self.show_gui = False

        self.root = os.path.join(self.root, "tmptest")
        self.in_path = os.path.join(self.root, "in_files")
        self.zipper_output_path = os.path.join(self.root, "Zipperscript_Output")
        self.out_path = os.path.join(self.root, "out_files")

        if os.path.exists(self.root):
            print self.root + " already exists.  Deleting it.  CHANGE THIS!"
            shutil.rmtree(self.root)
        os.mkdir(self.root)

        if os.path.exists(self.in_path):
            print self.in_path +" already exists"
        else:
            os.mkdir(self.in_path)

    def teardown(self):
        print ("Running teardown")
        #shutil.rmtree(self.root)


    def create_files(self, path, directory):
        os.mkdir(os.path.join(path, directory.name))
        for obj in directory.contents:
            #print "Looking at " + obj.name + obj.__class__.__name__
            if obj.__class__.__name__ == "D":
                self.create_files(os.path.join(path, directory.name), obj)
            elif obj.__class__.__name__ == "F":
                with open(os.path.join(path, directory.name, obj.name), 'w+') as f:
                    f.write(obj.contents)

    def unzip(self, in_files, out_files):
        if not os.path.exists(out_files):
            os.mkdir(out_files)
        for f in os.listdir(in_files):
            if f.endswith(".zip"):
                with zipfile.ZipFile(os.path.join(in_files, f)) as zf:
                    zf.extractall(out_files)

    def get_files(self, path):
        directory = D(os.path.split(path)[1], [])
        for obj in os.listdir(path):
            obj_path = os.path.join(path, obj)
            if os.path.isdir(obj_path):
                new_dir = self.get_files(obj_path)
                directory.contents.append(new_dir)
            else:
                new_file=""
                with open(obj_path, 'r') as f:
                    new_file = F(obj, f.read())
                directory.contents.append(new_file)
        return directory

    def rand_str(self, length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

    def build_route(self, route_name, frames, fullsize_files = False, include_files = None):
        #Implement fullsize files
        if include_files is None:
            include_files = ["jpg", "fis", "txt", "rtf", "rut", "gps", "raw", "log",\
                    "rdf", "rsp", "hdl", "hdlg", "hdli", "hdls", "iri"]
        else:
            include_files = copy.copy(include_files)
        route_contents = []
        image_root_dir_contents = []
        hdl_contents = []
        if "jpg" in include_files:
            include_files.remove("jpg")
            image_dir = []
            for x in xrange(0, 1 + frames//100):
                if (x+1)*100 < frames:
                    image_dir.append(D("Dir_" + str(x).zfill(3),\
                            [F("F_" + str(x).zfill(5) + ".jpg")\
                            for x in xrange((x*100) + 1, (x + 1)*100)]))
                else:
                    image_dir.append(D("Dir_" + str(x).zfill(3),\
                            [F("F_" + str(x).zfill(5) + ".jpg") for x in xrange((x*100) + 1, frames+1)]))

            front_im_dir = D("Front", image_dir)
            right_im_dir = D("Right", image_dir)
            left_im_dir = D("Left", image_dir)

            image_root_dir_contents.extend([front_im_dir, right_im_dir, left_im_dir])

        if "fis" in include_files:
            include_files.remove("fis")
            lcms_dir = D("LCMS", [F("F_" + str(x).zfill(6) + ".fis") for x in xrange(1, frames+1)])
            image_root_dir_contents.append(lcms_dir)

        if len(image_root_dir_contents)>0:
            image_root_dir = D(route_name, image_root_dir_contents)
            route_contents.append(image_root_dir)

        for hdl_type in ["hdl", "hdlg", "hdli", "hdls"]:
            if hdl_type in include_files:
                include_files.remove(hdl_type)
                hdl_contents.append(F(route_name + "." + hdl_type))

        if len(hdl_contents)>0:
            route_contents.append(D(route_name + ".hdl", hdl_contents))

        for file_type in include_files:
            route_contents.append(F(route_name + "." + file_type))

        route = D(route_name, route_contents)
        return route

    def test_test(self):
        print self.build_route("Hi", 10)


    def test_no_files(self):
        date1 = D("Empty_date_dir", [])
        self.create_files(self.in_path, date1)
        z.ZipperScript(self.in_path, self.vehicle, self.show_gui)
        self.unzip(self.zipper_output_path, self.out_path)
        zipper_output = self.get_files(self.out_path)


    def test_crit_file(self):
        route1 = D("ROUTE01", [
                F("ROUTE01.txt"),
                F("ROUTE01.rtf"),
                F("ROUTE01.rut"),
                F("ROUTE01.gps"),
                F("ROUTE01.raw"),
                F("ROUTE01.log"),
                F("ROUTE01.rdf"),
                F("ROUTE01.rsp"),
                F("ROUTE01.hdlg"),
                F("ROUTE01.iri")])
        pospac1 = D("1234567_1234", [route1, F("1234567_1234.000")])
        date1 = D("Todays_date", [pospac1])
        #print date1

        self.create_files(self.in_path, date1)
        z.ZipperScript(self.in_path, self.vehicle, self.show_gui)
        self.unzip(self.zipper_output_path, self.out_path)
        zipper_output = self.get_files(self.out_path)
        #print zipper_output

        crit_route1 = D("ROUTE01", [
                F("ROUTE01.txt"),
                F("ROUTE01.rtf"),
                F("ROUTE01.gps"),
                F("ROUTE01.log")])
        crit_pospac1 = D("1234567_1234", [crit_route1])
        crit_date1 = D("Todays_date", [crit_pospac1])

        for obj in zipper_output.contents:
            if obj.name.endswith("Critical"):
                print "Zipper_output of critical ", obj.contents[0]
                print "Should match this output", crit_date1
                assert obj.contents[0] == crit_date1


    def test_valid_file(self):

        lrs_files = ["gps", "log", "rdf", "rsp"]
        pave_files = ["gps", "rsp", "fis", "log", "rdf", "txt"] #also need first route's images
        distress_files = pave_files #also need first route's images
        vcm_files = ["gps", "raw", "log", "rdf", "txt",\
                "hdl", "hdlg", "hdli", "hdls"] #need first route's images
        asset_files = vcm_files #also need first route's images
        images = ["jpg"]


        pospac1 = D("1234567_1234", [ 
                self.build_route("LRS_stuff_1", 200),
                self.build_route("PAVE_stuff_1", 20),
                self.build_route("DISTRESS_stuff_1", 20),
                self.build_route("VCM_stuff_R_1", 5),
                self.build_route("VCM_stuff_L_1", 5),
                self.build_route("VCM_stuff_L_2", 5),
                self.build_route("VCM_stuff_L_3", 5),
                self.build_route("ASSET_stuff_R_1", 5),
                self.build_route("ASSET_stuff_R_2", 5),
                self.build_route("ASSET_stuff_R_3", 5),
                self.build_route("ASSET_stuff_L_1", 5),
                F("1234567_1234.000")])
        date1 = D("Todays_date", [pospac1])

        self.create_files(self.in_path, date1)
        z.ZipperScript(self.in_path, self.vehicle, self.show_gui)
        self.unzip(self.zipper_output_path, self.out_path)
        zipper_output = self.get_files(self.out_path)

        valid_pospac1 = D("1234567_1234", [ 
                self.build_route("LRS_stuff_1", 200, include_files = lrs_files),
                self.build_route("PAVE_stuff_1", 20, include_files = pave_files + images),
                self.build_route("DISTRESS_stuff_1", 20, include_files = distress_files + images),
                self.build_route("VCM_stuff_R_1", 5, include_files = vcm_files + images),
                self.build_route("VCM_stuff_L_1", 5, include_files = vcm_files + images),
                self.build_route("VCM_stuff_L_2", 5, include_files = vcm_files),
                self.build_route("VCM_stuff_L_3", 5, include_files = vcm_files),
                self.build_route("ASSET_stuff_R_1", 5, include_files = asset_files + images),
                self.build_route("ASSET_stuff_R_2", 5, include_files = asset_files),
                self.build_route("ASSET_stuff_R_3", 5, include_files = asset_files),
                self.build_route("ASSET_stuff_L_1", 5, include_files = asset_files + images),
                F("1234567_1234.000")])
        valid_date1 = D("Todays_date", [valid_pospac1])

        for obj in zipper_output.contents:
            if obj.name.endswith("Validations"):
                #print "Zipper_output of validation dir ", obj.contents[0]
                #print "Should match this output", valid_date1
                assert obj.contents[0] == valid_date1

class D():
    def __init__(self, name, contents):

        self.name = name
        self.contents = contents

    def __str__(self):
        output = "< D: " + str(self.name) + "|"
        for obj in self.contents:
            #print output + "!@#$" + obj.name
            output = output + " " + str(obj)
        output = output + ">"
        return str(output)

    def __eq__(self, other):
        return self.equals(other, 0)

    def equals(self, other, depth):
        #try:
        output = True
        for obj1 in self.contents:
            found_a_match = False
            for obj2 in other.contents:
                if obj1.equals(obj2, depth + 1):
                    found_a_match = True
                    print " " * 2 * depth + "Found match!"
                    break
            if not found_a_match:
                print " " * 2 * depth + "Files don't match. " + self.name + " contains " + obj1.name
                output = False
                break

        for obj1 in other.contents:
            found_a_match = False
            for obj2 in self.contents:
                if obj2.equals(obj1, depth + 1):
                    found_a_match = True
                    print " " * 2 * depth + "Found match!"
                    break
            if not found_a_match:
                print " " * 2 * depth + "Files don't match. " + other.name + " contains " + obj1.name
                output = False
                break
        if not (isinstance(other, self.__class__) and self.name == other.name):
            output = output and isinstance(other, self.__class__) and self.name == other.name
        output = output and isinstance(other, self.__class__) and self.name == other.name
        print " " * 2 * depth + "Checking " + self.name + " and " + other.name + " Returning: " + str(output)
        return output

        """except:
            return False
            print "FAILLLURE"""

class F(D):
    def __init__(self, name, contents = ""):
        self.name = name
        self.contents = contents


    def __str__(self):
        output = "< F: " + str(self.name) + "|"
        for obj in self.contents:
            output = output + " " + str(obj)
        output = output + ">"
        return output


    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__) and\
                    self.name == other.name and self.contents == other.contents:
                return True
            else:
                #print "oh jeez", isinstance(other, self.__class__), self.name == other.name, self.contents == other.contents
                return False
        except:
            print "goddamnit!!!"
            return False


