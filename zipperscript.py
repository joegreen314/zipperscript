from __future__ import division
import easygui as eg
import os, zlib, re, datetime, getpass, tkMessageBox, sys
import zipfile as z
import Tkinter as tk
from tkFileDialog import askdirectory
from optparse import OptionParser

class ZipperScript():

    def __init__(self, root, vehicle, show_gui):
        """Inits ZipperScript.  Creates zip_file from data collected.  If
        validation data is present, will create a separate zip file with
        validation data.  Also creates a third zip file with any gps, rtf and
        txt files found."""

        self.show_gui = show_gui
        self.gui = tk.Tk() #GUI Stuff
        self.gui.withdraw() #Don't want a main window

        if root:
            self.root = root
        elif self.show_gui:
            self.root = askdirectory(title = "Choose date directory")
        else:
            print("Error. No root specified and GUI is suppressed")

        if(self.root):
            if vehicle:
                #vehicle name specificied in argv
                self.run_zipperscript(vehicle)
            elif self.show_gui:
                #vehicle name not speficied, prompt user for name
                self.get_user_input("Enter Vehicle Name", self.run_zipperscript)
            else:
                #Message boxes disabled.  Use default name
                self.run_zipperscript("vehicle_name")
        else:
            self.gui.destroy()
            sys.exit(1)


    def get_user_input(self, message, next_step):

        def OK(user_input):
            window.iconify()
            window.destroy()
            user_input = re.sub(r'\W+', '', user_input)
            next_step(user_input)

        window = tk.Toplevel()
        window.title(message)
        L1 = tk.Label(window, text=message)
        L1.pack(side = tk.LEFT)
        E1 = tk.Entry(window, bd =5)
        E1.pack(side = tk.LEFT)
        window.bind(sequence = "<Return>", func = lambda d: OK(E1.get()))
        B1 = tk.Button(window, text="OK", command = lambda: OK(E1.get()))
        B1.pack(side = tk.LEFT)
        window.lift()
        window.iconify()
        window.deiconify()
        E1.focus()
        window.mainloop()


    def run_zipperscript(self, vehicle_name):
        self.vehicle = vehicle_name
        # create log file for troubleshooting
        start = datetime.datetime.now()
        output_dir_name = "Zipperscript_Output"

        self.output_dir_path = os.path.join(os.path.split(self.root)[0], output_dir_name)
        if not os.path.exists(self.output_dir_path):
            os.makedirs(self.output_dir_path)

        log_name = os.path.join(self.output_dir_path,
                "zipperscript_log_" + self.vehicle + "_" + start.strftime("%y%m%d%H%M%S") + ".txt")
        self.log = open(log_name, "w+")
        if self.log:
            self.files_zipped_count = 0
            self.print_out("Zipperscript log " + str(start))
            self.print_out("This file created when zipperscript is run for " + \
                    "troubleshooting purposes.  Include it in the FTP upload")
            self.print_out("User has selected " + str(self.root))
            self.output_dir_name = "Zipperscript_Output"
            self.route_paths = []
            self.pospacs = []
            self.dmi_cal = []
            # find route_paths, pospacs and dmi_cal files
            self.find_route_directories()

            self.zip_file_val = 0
            self.zip_val_name = 0
            self.zip_val_path = 0
            self.zip_validations()

            #Zip up collection data
            zip_file_name = os.path.split(self.root)[1] \
                    + "_" + self.vehicle + "_Collection.zip"
            zip_file_path = os.path.join(os.path.split(self.root)[0],
                    self.output_dir_name, zip_file_name)
            zip_file_collection = z.ZipFile(zip_file_path, "w", z.ZIP_DEFLATED, allowZip64=True)
            self.zip_collection_routes(zip_file_collection)

            #Zip up gps and txt files
            self.print_out("\n***** STARTING CRITICAL ZIP *****")
            zip_crit_name = "___" + os.path.split(self.root)[1] \
                    + "_" + self.vehicle + "_Critical.zip"
            zip_crit_path = os.path.join(os.path.split(self.root)[0],
                    self.output_dir_name, zip_crit_name)
            zip_file_crit = z.ZipFile(zip_crit_path, "w", z.ZIP_DEFLATED, allowZip64=True)
            self.zip_route(zip_file_crit, self.root, [".txt", ".rtf" ,".gps", ".log"], \
                    "_" + self.vehicle + "_Critical")
            self.print_out("\n***** ZIP COMPLETE *****")
            self.print_out("Files zipped:")
            zip_file_crit.close()
            for i in zip_file_crit.infolist():
                self.print_out("\t%s\t%s" % (i.filename, self.pretty_size(i.compress_size)))

            zip_file_collection.close()
            for i in zip_file_collection.infolist():
                self.print_out("\t%s\t%s" % (i.filename, self.pretty_size(i.compress_size)))

            if(self.zip_val_name):
                self.zip_file_val.close()
                for i in self.zip_file_val.infolist():
                    self.print_out("\t%s\t%s" % \
                        (i.filename, self.pretty_size(i.compress_size)))
            self.print_out("")

            self.print_out("%s\t%s" % \
                    (zip_crit_name, self.pretty_size(os.path.getsize(zip_crit_path))))
            end = datetime.datetime.now()
            self.print_out("%s\t%s" % \
                    (zip_file_name, self.pretty_size(os.path.getsize(zip_file_path))))
            if(self.zip_val_name):
                self.print_out("%s\t%s" % \
                    (self.zip_val_name, self.pretty_size(os.path.getsize(self.zip_val_path))))
            self.print_out("Total files zipped: " + str(self.files_zipped_count))
            self.print_out("Total time for zip: " + str(end - start))
            self.log.close()

            if(self.show_gui):
                tkMessageBox.showinfo("Zip Complete", \
                        "Success!  Zipped %s files in %s seconds.  Files are located at %s" % \
                        (str(self.files_zipped_count), str((end - start).total_seconds()),\
                        os.path.join(os.path.split(self.root)[0], self.output_dir_name)))    
        else:
            print "Could not create log file.  Exiting"
            sys.exit(1)
        self.gui.destroy()
        #sys.exit(0)


    def print_out(self, output):
        try:
            self.log.write(str(self.get_time()) + " " + str(output) + "\n")
            print self.get_time(), output
        except IOError:
            pass

    def get_time(self):
        now = datetime.datetime.now()
        return now.strftime("%H:%M:%S")

    def find_route_directories(self):
        """
        Finds the absolute path to all route directories and POSPAC session
        files, and dmi_cal text files.  These paths are saved in
        self.route_paths, self.pospacs and self.dmi_cal respectively.  Any
        directory containing a ".log" file will be considered a route directory
        and added to the list."""
        self.print_out("\n***** SEARCHING FOR ROUTE DIRECTORIES *****")
        for dirpath, dirs, files in os.walk(self.root, topdown = True):
            for f in files:
                if f[-4:] == ".000":
                    self.pospacs.append(os.path.join(dirpath, f))
                elif f[-4:] == ".log":
                    self.route_paths.append(dirpath)
                    break
                elif f[-4:] == ".txt" and f[0:7].lower() == "dmi_cal":
                    self.dmi_cal.append(os.path.join(dirpath, f))

        if (len(self.route_paths)!=0):
            self.print_out("Found routes: ")
            for route_path in self.route_paths:
                self.print_out("\t" + str(route_path))
        else:
            self.print_out("No route directories found")

        if(len(self.pospacs)!=0):
            self.print_out("Found POSPAC session files: ")
            for pospac in self.pospacs:
                self.print_out("\t" + str(pospac))
        else:
            self.print_out("No POSPAC session files found")

        if(len(self.dmi_cal)!=0):
            self.print_out("Found DMI_Cal files: ")
            for cal in self.dmi_cal:
                self.print_out("\t" + str(cal))
        else:
            self.print_out("No DMI_Cal files found")



    def zip_validations(self):
        """Checks list of route files for names with validation tag.  If any are
        found, creates validation zip and zips up the correct files and removes
        the route from self.route_paths."""
        marker = "_" + self.vehicle + "_Validations"
        pospac_to_add = []
        already_added_images = []

        #The list below removes items from the list as it iterates through it,
        #so we're iterating over a copy
        for p in list(self.route_paths):
            f = os.path.split(p)[1]
            if f[0:3].upper() == "LRS":
                if not self.zip_file_val:
                    self.create_validation_zip()
                self.route_paths.remove(p)
                self.zip_route(self.zip_file_val, p, \
                    [".gps", ".log", ".rdf", ".rsp"], marker)
                #NEED ONLY FIRST ROUTE OF IMAGES
                if(f[:-2] not in already_added_images):
                    already_added_images.append(f[:-2])
                    self.zip_route(self.zip_file_val, p, [".jpg"], marker)
                for p in self.dmi_cal:
                    self.write_to_zip(self.zip_file_val, p, marker)

            elif f[0:5].upper() == "ASSET" or f[0:3].upper() == "VCM":
                if not self.zip_file_val:
                    self.create_validation_zip()
                self.route_paths.remove(p)
                self.zip_route(self.zip_file_val, p, \
                    [".gps", ".raw", ".hdl", ".log", ".rdf", ".hdlg", ".hdli", ".hdls", ".txt"], marker)
                #NEED ONLY FIRST ROUTE OF IMAGES
                if(f[:-2] not in already_added_images):
                    already_added_images.append(f[:-2])
                    self.zip_route(self.zip_file_val, p, [".jpg"], marker)
                #NEED TO FIND POSPAC
                for POSPAC in self.pospacs:
                    pospacdir = os.path.split(POSPAC)[0]
                    if(re.search(pospacdir,p) and POSPAC not in pospac_to_add):
                        pospac_to_add.append(POSPAC)

            elif f[0:4].upper() == "PAVE" or f[0:8].upper() == "DISTRESS":
                if not self.zip_file_val:
                    self.create_validation_zip()
                self.route_paths.remove(p)
                self.zip_route(self.zip_file_val, p, 
                            [".gps", ".rsp", ".fis", ".log", ".rdf", ".txt"], marker)
                #NEED ONLY FIRST ROUTE OF IMAGES
                if(f[:-2] not in already_added_images):
                    already_added_images.append(f[:-2])
                    self.zip_route(self.zip_file_val, p, [".jpg"], marker)

            elif f[0:3].upper() == "GPS":
                if not self.zip_file_val:
                    self.create_validation_zip()
                self.route_paths.remove(p)
                self.zip_route(self.zip_file_val, p, [".gps", ".raw", ".jpg", ".log"], marker)
                #NEED TO FIND POSPAC
                for POSPAC in self.pospacs:
                    pospacdir = os.path.split(POSPAC)[0]
                    if(re.search(pospacdir,p) and POSPAC not in pospac_to_add):
                        pospac_to_add.append(POSPAC)

            elif f[0:6].upper() == "THIRTY":
                if not self.zip_file_val:
                    self.create_validation_zip()
                self.route_paths.remove(p)
                self.zip_route(self.zip_file_val, p, [".gps", ".raw", ".jpg", ".log"], marker)
                #NEED TO FIND POSPAC
                for POSPAC in self.pospacs:
                    pospacdir = os.path.split(POSPAC)[0]
                    if(re.search(pospacdir,p) and POSPAC not in pospac_to_add):
                        pospac_to_add.append(POSPAC)

        for p in pospac_to_add:
            self.write_to_zip(self.zip_file_val, p, marker)


    def create_validation_zip(self):
        """Called from zip_validations if any routes with validation tags are
        found.  Creates validation file and zips up valdiations."""
        self.print_out("\n***** STARTING VALIDATION ZIP *****")
        self.zip_val_name = os.path.split(self.root)[1] + \
                "_" + self.vehicle + "_Validations.zip"
        self.zip_val_path = os.path.join(os.path.split(self.root)[0],
                self.output_dir_name, self.zip_val_name)
        self.zip_file_val = z.ZipFile(self.zip_val_path, "w",
                        z.ZIP_DEFLATED, allowZip64 = True)

    def zip_collection_routes(self, zip_file):
        """Zips up regular collection route files."""
        self.print_out("\n***** STARTING COLLECTION ZIP *****")
        marker = "_" + self.vehicle + "_Collection"
        for p in self.route_paths: #zip all non-image files in route directories
            self.zip_route(zip_file, p, \
                    [".txt", ".pdf", ".rut", ".gps", ".raw", ".log", \
                    ".rdf", ".rsp", ".hdlg", ".erd", ".iri", ".fea"], marker)
        for p in self.pospacs: #zip POSPAC session files
            self.write_to_zip(zip_file, p, marker)
        for p in self.dmi_cal: #zip any dmi_cal files
            self.write_to_zip(zip_file, p, marker)
        #zip any other files in root directory (ignore POSPAC and dmi_cal)
        for f in os.listdir(self.root): 
            if os.path.isfile(f) and f[-4:] != ".000" and \
                    (f[-4:] != ".txt" or f[0:7] != "dmi_cal"):
                self.write_to_zip(zip_file, os.path.join(self.root, f), marker)

        self.zip_feature_tag_images(zip_file) #zip images near featureTags
        self.zip_images(zip_file) #zip sample images and FIS

    def zip_route(self, zip_file, route_path, file_types, marker):
        """Searches for and zips all files in route directory with path ending
        in 'file_types'.

        Parameters
        ----------
        routePath : str
            Absolute file path of route directory to zip
        file_types : list of str
            Paths ending in this string will be added to the zip file.  Does 
            not need to be extensions.  Name is misleading.
        marker : str
            Marker which will be added to end root directory's name."""

        if len(file_types)!=0:
            self.print_out("Searching " + str(route_path) + \
                    " for any files ending in " + str(file_types))
            files_written = 0

            for dirpath, dirs, files in os.walk(route_path, topdown=True):
                for f in files:
                    for t in file_types:
                        if f[-len(t):].lower() == t:
                            self.write_to_zip(zip_file, os.path.join(dirpath, f), marker)
                            files_written = files_written + 1
                            break
            self.print_out("\tAdded %d file(s) to zip" % files_written)

    def write_to_zip(self, zip_file, file_path, marker):
        """Adds a single file to zip_file

        Parameters
        ----------
        file_path : str
            Path to file to be zipped
        marker : str
            Marker which will be added to end root directory's name.
        """
        dest = os.path.join(os.path.split(self.root)[1] + marker, \
                file_path[len(self.root) + 1:])
        if(zip_file):
            self.files_zipped_count = self.files_zipped_count + 1
            zip_file.write(file_path, dest)

    def zip_feature_tag_images(self, zip_file):
        """Adds image near feature tags to the zip file.  All even images within
        10 frames will be added to the zip file.  In the event of two feature
        tags being close together, the same images will not be zipped up twice.
        """
        self.print_out("\n***** ADDING FEATURE TAG IMAGES *****")
        marker = "_" + self.vehicle + "_Collection"
        for p in self.route_paths:
            for f in os.listdir(p):
                if f[-4:].lower() == ".fea":
                    feature_tag_frames = []
                    image_frames_to_add = []

                    #GET FRAME NUMBERS FROM FEATURE FILE
                    with open(os.path.join(p, f), "r") as fea:
                        fea_lines = fea.readlines()
                        for line in fea_lines[1:]:
                            feature_tag_frames.append(int(line[0:5]))

                        #ADD EVEN IMAGE NUMBERS WITHIN 6 TO image_frames_to_add
                        for frame in feature_tag_frames:
                            frame = frame // 2 * 2 #round down to closest even number
                            for i in xrange(-10, 12, 2):

                                if frame + i not in image_frames_to_add:
                                    image_frames_to_add.append(frame + i)
                        for i in xrange(len(image_frames_to_add)):
                            image_frames_to_add[i] = str(image_frames_to_add[i]).zfill(5) + ".jpg"
                        self.zip_route(zip_file, p, image_frames_to_add, marker)

    def zip_images(self, zip_file):
        """Adds sample images to the zip file.  Routes with burn or bounce in
        the name are ignored.  The closest three routes to 7am, noon and 6pm
        will be chosen.  The first, sixth and eleventh frame from the beginning
        and end of these routes will be included.
        """
        self.print_out("\n***** ADDING SAMPLE IMAGES *****")
        marker = "_" + self.vehicle + "_Collection"
        #IGNORE BURN AND BOUNCE ROUTES
        for p in list(self.route_paths):
            route_name = os.path.split(p)[1].lower()
            if re.search("burn", route_name) or re.search("bounce", route_name):
                self.route_paths.remove(p)

        #GET ROUTE TIMES FROM LOG FILE
        time = {}
        lastFrame = {}

        for p in list(self.route_paths):
            for f in os.listdir(p):
                if f[-4:]== ".log":
                    log_lines = open(os.path.join(p, f), "r").readlines()
                    if len(log_lines):
                        t = log_lines[0][-16 : -8]
                        time[p] = datetime.datetime.strptime(t, "%H:%M:%S")
                        lastFrame[p] = int(log_lines[-1][0 : 5])
                    else:
                        self.print_out("Bad log file: " + f + "  Removing route from route list")
                        self.route_paths.remove(p)
                    break

        #SELECT SAMPLE ROUTES BASED ON TIME SHOT
        morning_time = datetime.datetime.strptime("7:00:00", "%H:%M:%S")
        evening_time = datetime.datetime.strptime("18:00:00", "%H:%M:%S")
        midday_time = datetime.datetime.strptime("12:00:00", "%H:%M:%S")
        morning_routes = self.get_routes_shot_closest_to_time(time, morning_time)
        evening_routes = self.get_routes_shot_closest_to_time(time, evening_time)
        midday_routes = self.get_routes_shot_closest_to_time(time, midday_time)

        #combine lists without duplicates
        route_sample = morning_routes + \
                list(set(evening_routes)-set(morning_routes))
        route_sample = route_sample + \
                list(set(midday_routes)-set(route_sample))

        #ZIP First, 5th and 9th image from beginning and end of routes
        startImages = ["00001.jpg", "00006.jpg", "00011.jpg"]
        self.print_out(route_sample)

        for route in route_sample:
            end_images=[str(lastFrame[route]).zfill(5) + ".jpg", \
                    str(lastFrame[route] - 5).zfill(5) + ".jpg", \
                    str(lastFrame[route] - 10).zfill(5) + ".jpg"]
            images = startImages + list(set(end_images) - set(startImages))

            self.zip_route(zip_file, route, images, marker)

        #Grab three FIS files from three routes
        self.print_out("\n***** ADDING FIS FILES *****")
        FISImages = ["000001.fis", "000006.fis", "000011.fis"]
        if morning_routes:
            self.zip_route(zip_file, morning_routes[0], FISImages, marker)

        if midday_routes:
            self.zip_route(zip_file, midday_routes[0], FISImages, marker)

        if evening_routes:
            self.zip_route(zip_file, evening_routes[0], FISImages, marker)

    def get_routes_shot_closest_to_time(self, routeTime, ideal_time):
        """Returns a list of paths to the three routes shot closest to a
        specified time.

        Parameters
        ----------
        routeTime : dictionary of datetimes
            Dictionary of datetimes corresponding to when each route was shot
        ideal_time : datetime
            Routes returned will be as close as possible to this time
        """
        MAX_TIME = datetime.datetime.strptime("1999", "%Y")
        best_times = [MAX_TIME] * 3
        best_routes = [0] * 3

        for route in self.route_paths:
            if abs(routeTime[route] - ideal_time).total_seconds() < \
                    abs(best_times[0] - ideal_time).total_seconds():
                best_times[2] = best_times[1]
                best_times[1] = best_times[0]
                best_times[0] = routeTime[route]
                best_routes[2] = best_routes[1]
                best_routes[1] = best_routes[0]
                best_routes[0] = route

            elif abs(routeTime[route] - ideal_time).total_seconds() < \
                    abs(best_times[1] - ideal_time).total_seconds():
                best_times[2] = best_times[1]
                best_times[1] = routeTime[route]
                best_routes[2] = best_routes[1]
                best_routes[1] = route

            elif abs(routeTime[route] - ideal_time).total_seconds() < \
                    abs(best_times[2] - ideal_time).total_seconds():
                best_times[2] = routeTime[route]
                best_routes[2] = route

        for route in list(best_routes):
            if not route:
                best_routes.remove(route)
        return best_routes

    def pretty_size(self, bytes):
        factor_suffix = [
        (1024 ** 5, 'PB'),
        (1024 ** 4, 'TB'), 
        (1024 ** 3, 'GB'), 
        (1024 ** 2, 'MB'), 
        (1024 ** 1, 'KB'),
        (1024 ** 0, 'B'),
        ]

        for factor, suffix in factor_suffix:
            if bytes>=factor:
                return "%.3g %s" % (bytes/factor, suffix)

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-s", action="store_false", dest="show_gui", default = True,
            help = "suppress UI messages")
    parser.add_option("--root", action="store", dest="root", default = False,
            help = "date directory to be searched")
    parser.add_option("--vehicle", action="store", dest="vehicle", default = False,
            help = "vehicle name")
    (options, args) = parser.parse_args()

    if args:
        root = args[0]
    else:
        root = options.root

    ZipperScript(root, options.vehicle, options.show_gui)