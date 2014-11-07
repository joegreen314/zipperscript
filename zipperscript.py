from __future__ import division
import easygui as eg
import os, zlib, re, datetime, getpass, tkMessageBox, sys, traceback
import zipfile as z
import Tkinter as tk
from tkFileDialog import askdirectory
from optparse import OptionParser

def pretty_size(self, bytes):
    factor_suffix = [
    (1024 ** 5, 'PB'),
    (1024 ** 4, 'TB'), 
    (1024 ** 3, 'GB'), 
    (1024 ** 2, 'MB'), 
    (1024 ** 1, 'KB'),
    (1024 ** 0, 'B'),
    ]

class Output_Writer:
    def __init__(self):
        self.prelog = ""
        self.log = False
        self.frame_to_update = 0
        self.label_to_change = 0
        self.std_out = sys.stdout
        self.last_gui_update = datetime.datetime.now()

    def add_output_gui(self, frame_to_update, label_to_change):
        self.frame_to_update = frame_to_update
        self.label_to_change = label_to_change

    def add_log_file(self, path):
        self.log = open(path, "w+")

    def write(self, text):
        self.std_out.write(text)

        if self.log:
            if self.prelog:
                self.log.write(self.prelog)
                self.prelog = False
            self.log.write(text)
        else:
            self.prelog = self.prelog + str(text)

        if self.frame_to_update:
            gui_log = self.label_to_change.get()
            self.label_to_change.set(gui_log[-10000:] + str(text))
            if (datetime.datetime.now() - self.last_gui_update).total_seconds() > 1:
                self.frame_to_update.update()
                self.last_gui_update = datetime.datetime.now()

    def get_time(self):
        now = datetime.datetime.now()
        return now.strftime("%H:%M:%S")

    def close(self):
        self.log.close()
        sys.stdout = sys.__stdout__

class Zip:
    def __init__(self, path, root_name, vehicle_name, identifier_name, priority=False):

        if priority:
            priority_underscores = "___"
        else:
            priority_underscores = ""
        self.zip_number = 0 #Will be incremented if zipfile already exists
        self.zip_name = "%s%s_%s_%s_%i" % (priority_underscores,
                root_name, vehicle_name, identifier_name, self.zip_number)
        self.zip_path = os.path.join(path, self.zip_name + ".zip")

        while os.path.isfile(self.zip_path):
            print "%s already exists! Incrementing zip_number" % self.zip_path
            self.zip_number = self.zip_number + 1
            self.zip_name = "%s%s_%s_%s_%i" % (priority_underscores,
                    root_name, vehicle_name, identifier_name, self.zip_number)
            self.zip_path = os.path.join(path, self.zip_name + ".zip")

        self.zip = False #Won't create zipfiles until we need them, to prevent empty zips
        self.files_zipped_count = 0
        print "Initialized zip file: ", self.zip_name

    def create_zip_file(self):
        print "Creating zip file: " + self.zip_path
        self.zip = z.ZipFile(self.zip_path, "w", z.ZIP_DEFLATED, allowZip64=True)

    def close(self):
        self.zip.close()

    def zip_route(self, abs_root_path, rel_route_path, file_types):
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

        if not self.zip:
            self.create_zip_file()

        if file_types:
            route_path = os.path.join(abs_root_path, rel_route_path)
            print "Searching " + str(route_path)
            print "\tfor any files ending in " + str(file_types)
            files_written = 0

            for dirpath, dirs, files in os.walk(route_path, topdown=True):
                for f in files:
                    for t in file_types:
                        if f[-len(t):].lower() == t:
                            file_path = os.path.join(dirpath, f)
                            self.write_to_zip(file_path, file_path[len(abs_root_path)+1:])
                            files_written = files_written + 1
                            break
            print "\tAdded %d file(s) to zip." % files_written

    def write_to_zip(self, source_path, rel_dest_path):
        """Adds a single file to zip_file

        Parameters
        ----------
        file_path : str
            Path to file to be zipped
        marker : str
            Marker which will be added to end root directory's name.
        """
        self.do_not_compress = [".fis"]
        if not self.zip:
            self.create_zip_file()

        dest = os.path.join(self.zip_name, rel_dest_path)
        self.files_zipped_count = self.files_zipped_count + 1
        if os.path.splitext(source_path)[1] in self.do_not_compress:
            self.zip.write(source_path, dest, z.ZIP_STORED)
        else:
            self.zip.write(source_path, dest, z.ZIP_DEFLATED)

    def print_summary(self):
        if self.zip:
            self.close()
            uncompressed_size = 0
            compressed_size = 0
            sizes_by_ext = [] #[ext, total compressed size, total uncompressed size] for all files
            for zi in self.zip.infolist():
                uncompressed_size = uncompressed_size + zi.file_size
                compressed_size = compressed_size + zi.compress_size
                file_ext = os.path.splitext(zi.filename)[1]
                if not file_ext:
                    break
                if file_ext in [x[0] for x in sizes_by_ext]:
                    index = [x[0] for x in sizes_by_ext].index(file_ext)
                    sizes_by_ext[index][1] = sizes_by_ext[index][1] + zi.compress_size
                    sizes_by_ext[index][2] = sizes_by_ext[index][2] + zi.file_size
                    sizes_by_ext[index][3] = sizes_by_ext[index][3] + 1
                else:
                    sizes_by_ext.append([file_ext, zi.compress_size, zi.file_size, 1])
            print "%s\t%s\t(%s)" % (self.zip_name,
                    self.pretty_size(compressed_size),
                    self.percentage_compressed(compressed_size, uncompressed_size))
            print "\tFiletype breakdown: "
            for [file_ext, c_size, u_size, num] in sorted(sizes_by_ext, key=lambda x:x[1], reverse=True):
                if u_size == 0:
                    break
                if file_ext in self.do_not_compress:
                    print "\t%s\t%s\t(Not compressed)" % (file_ext,
                            self.pretty_size(c_size))
                else:
                    print "\t%s\t%s\t(%s)" % (file_ext,
                            self.pretty_size(c_size),
                            self.percentage_compressed(c_size, u_size))

    def print_contents(self):
        if self.zip:
            print "\t%s" % self.zip_name
            for i in self.zip.infolist():
                    print "\t\t%s\t%s" % (i.filename,
                            self.pretty_size(i.compress_size))

    def percentage_compressed(self, compressed_size, uncompressed_size):
        if uncompressed_size == 0:
            output = 0
        else:
            output = 100 * (1 - compressed_size/uncompressed_size)
            if output < 0:
                output = 0
        return "%.2g%% compressed" % output

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


class ZipperScript:
    def __init__(self, root, vehicle, show_gui):
        """Inits ZipperScript.  Creates zip_file from data collected.  If
        validation data is present, will create a separate zip file with
        validation data.  Also creates a third zip file with any gps, rtf and
        txt files found."""

        self.output_writer = Output_Writer()
        self.original_stdout = sys.stdout
        sys.stdout = self.output_writer

        self.launcher_start = datetime.datetime.now()
        self.prelog = ""
        
        self.show_gui = show_gui
        if root:
            self.root = root
        else:
            self.root=""

        if vehicle:
            self.vehicle = vehicle
        else:
            self.vehicle = ""

        if self.show_gui:
            self.gui = tk.Tk()
            self.gui.wm_title("ZipperScript Launcher")
            self.frame = tk.Frame(self.gui, borderwidth=5)
            self.frame.grid()

            self.menu = tk.Frame(self.frame, borderwidth=5)
            self.menu.grid(sticky = tk.E)
            tk.Label(self.menu, text="Date Directory Path").grid(row=0)
            tk.Label(self.menu, text="Vehicle Name").grid(row=1)

            self.enter_root = tk.Entry(self.menu, width = 60, disabledbackground="grey")
            self.enter_root.insert(0, self.root)
            self.enter_root.grid(row=0, column=1)

            self.enter_vehicle = tk.Entry(self.menu, text=self.vehicle, width = 60, disabledbackground="grey")
            self.enter_vehicle.insert(0, self.vehicle)
            self.enter_vehicle.grid(row=1, column=1)
            self.enter_vehicle.bind("<Return>", self.start_button_cmd)

            self.browse_button = tk.Button(self.menu, text = "Browse...", command=self.browse_button_cmd)
            self.browse_button.grid(row=0, column=2)

            self.start_button = tk.Button(self.menu, text = "Start Zipperscript", command=self.start_button_cmd)
            self.start_button.grid(row=1, column=2)

            self.log_display = tk.StringVar()
            tk.Label(self.frame, textvariable = self.log_display, height=40, width=120, bg="black", fg="white", borderwidth=5, anchor = tk.SW, justify = tk.LEFT).grid(row=2, sticky=tk.E)
            self.output_writer.add_output_gui(self.frame, self.log_display)

        print "***** ZIPPERSCRIPT LOG *****"
        print "Zipperscript Launcher opened at " + str(self.launcher_start)
        print "This output will be written to a log file when zipperscript is started for " + \
                    "troubleshooting purposes.  Include it in the FTP upload"

        if self.show_gui:
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
            self.enter_vehicle.focus_set()
            self.gui.mainloop()
        else:
            self.run_zipperscript()

    def browse_button_cmd(self):
        out = askdirectory(title = "Choose date directory")
        if out:
            self.enter_root.delete(0, tk.END)
            self.enter_root.insert(0, str(out))

    def start_button_cmd(self, event=None):
        if not os.path.isdir(self.enter_root.get()):
            print "ERROR: Invalid directory: " + self.enter_root.get()
        if not self.enter_vehicle.get():
            print "ERROR: No Vehicle Name entered."

        if os.path.isdir(self.enter_root.get()) and self.enter_vehicle.get():
            self.enter_root.config(state=tk.DISABLED)
            self.enter_vehicle.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.DISABLED)

            self.root = self.enter_root.get()
            self.vehicle = self.enter_vehicle.get()

            try:
                self.run_zipperscript()

            except Exception as e:
                print traceback.format_exc()
                if self.show_gui:
                    tkMessageBox.showinfo("Error", "Error: Send log file to Digilog support")

        self.output_writer.close()
        if self.show_gui:
            self.gui.destroy()


    def run_zipperscript(self):
        self.start = datetime.datetime.now()
        print "\n***** ZIPPERSCRIPT STARTED *****"
        self.vehicle = re.sub(r'[^a-zA-Z0-9]','_', self.vehicle)
        print "Replacing non-alpha numeric characters in vehicle name with '_'."

        self.output_dir_name = "Zipperscript_Output"
        self.output_dir_path = os.path.join(os.path.split(self.root)[0], self.output_dir_name)
        if not os.path.exists(self.output_dir_path):
            os.makedirs(self.output_dir_path)

        log_name = os.path.join(self.output_dir_path,
                "zipperscript_log_" + self.vehicle + "_" + self.start.strftime("%y%m%d%H%M%S") + ".txt")
        self.output_writer.add_log_file(log_name)

        self.files_zipped_count = 0
        print "Date Directory entered: " + self.root
        print "Vehicle Name entered: " + self.vehicle
        self.route_paths = []
        self.pospacs = []
        self.dmi_cal = []
        # find route_paths, pospacs and dmi_cal files
        self.find_route_directories()

        collection_zip = Zip(self.output_dir_path, os.path.split(self.root)[1], self.vehicle, "Collection")
        validation_zip = Zip(self.output_dir_path, os.path.split(self.root)[1], self.vehicle, "Validation")
        critical_zip = Zip(self.output_dir_path, os.path.split(self.root)[1], self.vehicle, "Critical", priority = True)

        self.zip_validations(validation_zip)
        self.zip_collection_routes(collection_zip)

        print "\n***** STARTING CRITICAL ZIP *****"
        critical_zip.zip_route(self.root, "", [".txt", ".rtf" ,".gps", ".log"])

        print "\n***** ZIP COMPLETE *****"
        print "Files included:"

        collection_zip.print_contents()
        validation_zip.print_contents()
        critical_zip.print_contents()

        print "\n***** ZIP SUMMARY *****"
        collection_zip.print_summary()
        validation_zip.print_summary()
        critical_zip.print_summary()

        end = datetime.datetime.now()
        self.files_zipped_count = self.files_zipped_count + collection_zip.files_zipped_count + validation_zip.files_zipped_count
        print "Total files zipped: " + str(self.files_zipped_count)
        print "Total time for zip: " + str(end - self.start)
        if self.show_gui:
            self.frame.update()

        if(self.show_gui):
            tkMessageBox.showinfo("Zip Complete", \
                    "Success!  Zipped %s files in %s seconds.  Files are located at %s" % \
                    (str(self.files_zipped_count), str((end - self.start).total_seconds()),\
                    os.path.join(os.path.split(self.root)[0], self.output_dir_name)))    
        

    def find_route_directories(self):
        """
        Finds the absolute path to all route directories and POSPAC session
        files, and dmi_cal text files.  These paths are saved in
        self.route_paths, self.pospacs and self.dmi_cal respectively.  Any
        directory containing a ".log" file will be considered a route directory
        and added to the list."""
        print "\n***** SEARCHING FOR ROUTE DIRECTORIES *****"
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
            print "Found routes: "
            for route_path in self.route_paths:
                print "\t" + str(route_path)
        else:
            print "No route directories found."

        if(len(self.pospacs)!=0):
            print "Found POSPAC session files: "
            for pospac in self.pospacs:
                print "\t" + str(pospac)
        else:
            print "No POSPAC session files found."

        if(len(self.dmi_cal)!=0):
            print "Found DMI_Cal files: "
            for cal in self.dmi_cal:
                print "\t" + str(cal)
        else:
            print "No DMI_Cal files found."

    def zip_validations(self, zip_file):
        """Checks list of route files for names with validation tag.  If any are
        found, creates validation zip and zips up the correct files and removes
        the route from self.route_paths."""
        pospac_to_add = []
        already_added_images = []

        #The list below removes items from the list as it iterates through it,
        #so we're iterating over a copy
        for p in list(self.route_paths):
            rel_route_path = p[len(self.root)+1:]
            f = os.path.split(p)[1]

            if f[0:3].upper() == "LRS":
                self.route_paths.remove(p)
                zip_file.zip_route(self.root, rel_route_path,
                    [".gps", ".fea", ".raw", ".log", ".rdf", ".rsp"])
                #NEED ONLY FIRST ROUTE OF IMAGES
                if(f[:-2] not in already_added_images):
                    already_added_images.append(f[:-2])
                    zip_file.zip_route(self.root, rel_route_path,[".jpg"])
                for dmi_path in self.dmi_cal:
                    rel_dest_path = dmi_path[len(self.root)+1:]
                    zip_file.write_to_zip(dmi_path, rel_dest_path)

            elif f[0:5].upper() == "ASSET" or f[0:3].upper() == "VCM":
                self.route_paths.remove(p)
                zip_file.zip_route(self.root, rel_route_path,
                    [".gps", ".fea", ".raw", ".hdl", ".log", ".rdf", ".hdlg", ".hdli", ".hdls", ".txt"])
                #NEED ONLY FIRST ROUTE OF IMAGES
                if(f[:-2] not in already_added_images):
                    already_added_images.append(f[:-2])
                    zip_file.zip_route(self.root, rel_route_path, [".jpg"])
                #NEED TO FIND POSPAC
                for POSPAC in self.pospacs:
                    pospacdir = os.path.split(POSPAC)[0]
                    if(re.search(pospacdir,p) and POSPAC not in pospac_to_add):
                        pospac_to_add.append(POSPAC)

            elif f[0:4].upper() == "PAVE" or f[0:8].upper() == "DISTRESS":
                self.route_paths.remove(p)
                zip_file.zip_route(self.root, rel_route_path,
                            [".gps", ".fea", ".raw", ".rsp", ".fis", ".log", ".rdf", ".txt"])
                #NEED ONLY FIRST ROUTE OF IMAGES
                if(f[:-2] not in already_added_images):
                    already_added_images.append(f[:-2])
                    zip_file.zip_route(self.root, rel_route_path, [".jpg"])

            elif f[0:3].upper() == "GPS":
                self.route_paths.remove(p)
                zip_file.zip_route(self.root, rel_route_path, [".gps", ".fea", ".raw", ".jpg", ".log"])
                #NEED TO FIND POSPAC
                for POSPAC in self.pospacs:
                    pospacdir = os.path.split(POSPAC)[0]
                    if(re.search(pospacdir,p) and POSPAC not in pospac_to_add):
                        pospac_to_add.append(POSPAC)

            elif f[0:6].upper() == "THIRTY":
                self.route_paths.remove(p)
                zip_file.zip_route(self.root, rel_route_path, [".gps", ".fea", ".raw", ".jpg", ".log"])
                #NEED TO FIND POSPAC
                for POSPAC in self.pospacs:
                    pospacdir = os.path.split(POSPAC)[0]
                    if(re.search(pospacdir,p) and POSPAC not in pospac_to_add):
                        pospac_to_add.append(POSPAC)

        for p in pospac_to_add:
            rel_dest_path = p[len(self.root)+1:]
            zip_file.write_to_zip(p, rel_dest_path)

    def zip_collection_routes(self, zip_file):
        """Zips up regular collection route files."""
        print "\n***** STARTING COLLECTION ZIP *****"
        for p in self.route_paths: #zip all non-image files in route directories
            rel_route_path = p[len(self.root)+1:]
            zip_file.zip_route(self.root, rel_route_path, \
                    [".txt", ".pdf", ".rut", ".gps", ".raw", ".log", \
                    ".rdf", ".rsp", ".hdlg", ".erd", ".iri", ".fea"])
        for p in self.pospacs: #zip POSPAC session files
            rel_dest_path = p[len(self.root)+1:]
            zip_file.write_to_zip(p, rel_dest_path)
        for p in self.dmi_cal: #zip any dmi_cal files
            rel_dest_path = p[len(self.root)+1:]
            zip_file.write_to_zip(p, rel_dest_path)
        #zip any other files in root directory (ignore POSPAC and dmi_cal)
        for f in os.listdir(self.root): 
            if (os.path.isfile(f) and f[-4:] != ".000" and 
                    f != ".DS_Store" and 
                    (f[-4:] != ".txt" or f[0:7] != "dmi_cal")):
                file_path = os.path.join(self.root, f)
                zip_file.write_to_zip(file_path, f)

        self.zip_feature_tag_images(zip_file) #zip images near featureTags
        self.zip_images(zip_file) #zip sample images and FIS
        #Add all images created in past 24 hours from Desktop/DVX pictures
        dvx_pictures_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'DVX pictures')
        self.zip_new_files_from_dir(zip_file, dvx_pictures_path, "Focus Images")
        error_report_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Error_Archive')
        self.zip_new_files_from_dir(zip_file, error_report_path, "Error Reporter Files")

    def zip_feature_tag_images(self, zip_file):
        """Adds image near feature tags to the zip file.  All even images within
        10 frames will be added to the zip file.  In the event of two feature
        tags being close together, the same images will not be zipped up twice.
        """
        print "\n***** ADDING FEATURE TAG IMAGES *****"
        found_feature_tags = False
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
                        if feature_tag_frames:
                            found_feature_tags = True
                            print "Found feature tags in %s:" % p
                            print "\t", feature_tag_frames

                        #ADD EVEN IMAGE NUMBERS WITHIN 6 TO image_frames_to_add
                        for frame in feature_tag_frames:
                            frame = frame // 2 * 2 #round down to closest even number
                            for i in xrange(-10, 12, 2):

                                if frame + i not in image_frames_to_add:
                                    image_frames_to_add.append(frame + i)
                        for i in xrange(len(image_frames_to_add)):
                            image_frames_to_add[i] = str(image_frames_to_add[i]).zfill(5) + ".jpg"
                        rel_route_path = p[len(self.root)+1:]
                        zip_file.zip_route(self.root, rel_route_path, image_frames_to_add)
        if not found_feature_tags:
            print "\tNo feature tags found."

    def zip_images(self, zip_file):
        """Adds sample images to the zip file.  Routes with burn or bounce in
        the name are ignored.  The closest three routes to 7am, noon and 6pm
        will be chosen.  The first, sixth and eleventh frame from the beginning
        and end of these routes will be included.
        """
        print "\n***** ADDING SAMPLE IMAGES *****"
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
                        print "Bad log file: " + f + "  Removing route from route list."
                        self.route_paths.remove(p)
                    break

        #SELECT SAMPLE ROUTES BASED ON TIME SHOT
        morning_time = datetime.datetime.strptime("7:00:00", "%H:%M:%S")
        evening_time = datetime.datetime.strptime("18:00:00", "%H:%M:%S")
        midday_time = datetime.datetime.strptime("12:00:00", "%H:%M:%S")
        morning_routes = self.get_routes_shot_closest_to_time(time, morning_time)
        evening_routes = self.get_routes_shot_closest_to_time(time, evening_time)
        midday_routes = self.get_routes_shot_closest_to_time(time, midday_time)

        print "Selected %s sample morning routes:" % len(morning_routes)
        for r in morning_routes:
            print r

        print "Selected %s sample midday routes:" % len(midday_routes)
        for r in midday_routes:
            print r

        print "Selected %s sample evening routes:" % len(evening_routes)
        for r in evening_routes:
            print r

        #combine lists without duplicates
        route_sample = morning_routes + \
                list(set(evening_routes)-set(morning_routes))
        route_sample = route_sample + \
                list(set(midday_routes)-set(route_sample))

        #ZIP First, 5th and 9th image from beginning and end of routes
        startImages = ["00001.jpg", "00006.jpg", "00011.jpg"]


        for route in route_sample:
            end_images=[str(lastFrame[route]).zfill(5) + ".jpg", \
                    str(lastFrame[route] - 5).zfill(5) + ".jpg", \
                    str(lastFrame[route] - 10).zfill(5) + ".jpg"]
            images = startImages + list(set(end_images) - set(startImages))

            rel_route_path = route[len(self.root)+1:]
            zip_file.zip_route(self.root, rel_route_path, images)

        #Grab three FIS files from three routes
        print "\n***** ADDING FIS FILES *****"
        FISImages = ["000001.fis", "000006.fis", "000011.fis"]
        if morning_routes:
            rel_route_path = morning_routes[0][len(self.root)+1:]
            zip_file.zip_route(self.root, rel_route_path, FISImages)

        if midday_routes:
            rel_route_path = midday_routes[0][len(self.root)+1:]
            zip_file.zip_route(self.root, rel_route_path, FISImages)

        if evening_routes:
            rel_route_path = evening_routes[0][len(self.root)+1:]
            zip_file.zip_route(self.root, rel_route_path, FISImages)

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

    def zip_new_files_from_dir(self, zip_file, src_dir, dest_dir):
        size_limit = 15*1000*1000 #Files bigger than this will be ignored
        print "Searching %s for files written within last 24 hours." % src_dir
        if os.path.isdir(src_dir):
            seconds_in_a_day = 86400
            pictures_added_count = 0
            for f in os.listdir(src_dir):
                file_path = os.path.join(src_dir, f)
                creation_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if (self.start - creation_date).total_seconds() < seconds_in_a_day:
                    dest_path = os.path.join(dest_dir, f)
                    if os.path.getsize(file_path) < size_limit:
                        zip_file.write_to_zip(file_path, dest_path)
                        pictures_added_count = pictures_added_count + 1
                    else:
                        "\tIgnoring file larger than %s: %s" % (pretty_size(size_limit), file_path)
            print "\t%d files found" % pictures_added_count
        else:
            print "\t%s does not exist" % src_dir


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