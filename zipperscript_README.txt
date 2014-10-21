Zipperscript

This script has been written in python to replace the applescript zipperscript written by technology, so that it can be more easily edited.  The zipperscript zips up a sample of data collected to be uploaded to the FTP server and reviewed by the collection team.  It should be located in every collection vehicle on the desktop and should be used at the end of any day where data is collected.

Using the Zipper Script:
To start the zipperscript, double click on the zipperscript icon.  The script will prompt the user for a directory.  The user should pick that days collection Date directory and press “OK”.  Alternatively, the user may drag the date directory on top of zipperscript app icon; in this case the user will not be prompted for a date directory.  Next, the user will be prompted for a vehicle name.  The user will wait for a “success” dialog to appear.  This may take several minutes and previous GUI windows may remain on the screen.

HAWAII VERSION:
Hawaii version of zipperscript will prompt the user for a 2nd date directory and will look for all FIS files within it.

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
		Up to six sample images from up to three morning routes, midday routes, evening routes, ignoring routes with “burn” or “bounce” in the name
		Up to three sample FIS files from one morning route, midday route, and evening route, ignoring routes with “burn” or “bounce” in the name

2)  DATE_VEHICLE_Validation.zip
	LRS validations:
		.gps
		.log
		.rdf
		dmi_cal txt file
	ASSET validations:
		.gps
		.raw
		.hdl
		.log
		.rdf
		all images from first pass
		POSPAC session
	VCM validations:
		.gps
		.raw
		.hdl
		.log
		.rdf
		all images from first pass
		POSPAC session
	PAVE validations:
		.gps
		.rsp
		.log
		.rdf
		ALL .fis
		all images from first pass

	DISTRESS validations:
		.gps
		.rsp
		.log
		.rdf
		ALL .fis
		all images from first pass

3)  ___DATE_VEHICLE_Critical.zip
		.gps files
		.txt files