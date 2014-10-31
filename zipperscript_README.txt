Zipperscript
Version: 4.0.56
Last updated: 10-30-2014
Author: Joe Green

Changelog:

4.0.56 Fixed bug where zipperscript would overwrite files if run more than once a day
4.0.55 All validation routes will include RAW and FEA files.  GUI shows log file and other improvements.
4.0.54 First LRS run will include camera images.
4.0.53 Added up to nine FIS files to collection zip.  Fixed bug where routes named burn/bounce were not being ignored
4.0.00 Zipperscript rewritten from applescript version

Purpose:
This script has been written in python to replace the applescript zipperscript written by technology, so that it can be more easily edited.  The zipperscript zips up a sample of data collected to be uploaded to the FTP server and reviewed by the collection team.  It should be located in every collection vehicle on the desktop and should be used at the end of any day where data is collected.

Using the Zipper Script:
To start the zipperscript, the user either double clicks on the zipperscript icon, or drags the date directory to be zipped onto the zipperscript icon.  A window should appear.  The user then enters the date directory and vehicle name and clicks "Start Zipperscript".  The user will wait for a “success” dialog to appear.  This may take several minutes.

Output files:
The zipper script will make up to three zip files in the same directory as the root directory selected.  It will also make a log file that should be useful for troubleshooting purposes.  The logfile is named zipperscript_log_VEHICLE_DATETIME.txt and should be uploaded along with the zip files.

1)  DATE_VEHICLE_Collection.zip
	DMI_Cal files
	POSPAC session files
	Any other files in root directory chosen by user (should be date directory)
	From routes folders:
		.txt
		.pdf
		.rut
		.gps
		.raw
		.log
		.rdf
		.rsp
		.hdlg
		.erd
		.iri
		.fea
		Sample images from up to three morning routes, midday routes, evening routes, ignoring routes with “burn” or “bounce” in the name
		First FIS file from first and last route, ignoring routes with “burn” or “bounce” in the name

2)  DATE_VEHICLE_Validation.zip
	LRS validations:
		.gps
		.fea
		.raw
		.log
		.rdf
		.rsp
		all images from first pass
		dmi_cal txt file
	ASSET validations:
		.gps
		.fea
		.raw
		.hdl
		.log
		.rdf
		.hdlg
		.hdls
		.hdli
		.txt
		all images from first pass in either directions
		POSPAC session
	VCM validations:
		.gps
		.fea
		.raw
		.hdl
		.log
		.rdf
		.hdlg
		.hdls
		.hdli
		.txt
		all images from first pass in either lanes
		POSPAC session
	PAVE validations:
		.gps
		.fea
		.raw
		.rsp
		.log
		.rdf
		.txt
		ALL .fis
		all images from first pass

	DISTRESS validations:
		.gps
		.fea
		.raw
		.rsp
		.log
		.rdf
		.txt
		ALL .fis
		all images from first pass

3)  ___DATE_VEHICLE_Critical.zip
	GPS files
	txt files