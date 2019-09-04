# Hello
Intended for the ThorLabs DCC3240N camera (although will work with almost all - including the more common DCC1545M).

# Structure
This comprises an OO interface to the camera (LD_Cam.py) which basically just grabs images from the camera. LD_MirrorcleAlign.py defines a derived class which adds the functionality for drawing on the camera feed and making measurements based on the drawings.

UI is all done quick and dirty with Opencv's highgui functions because this doesn't really warrant anything more advanced right now.

# Usage
There is an example in LD_MirrorcleAlign.py, basically make an instance of MirrorcleAligner, call, Get_Image() to take a frame from the feed, then call Show_Overlay() to display the image with the drawings on it. Call Get_Alignment_Info(x) with the argument being the dimension of the mirror chip carrier and the function will return the offset of the middle of the two circular objects (mirror and extra) and their diameters.

# Requires
* IDS ueye camera drivers and C API files from http://www.ids-imaging.com/.
* The python wrapper for this https://pypi.org/project/pyueye/ (or "pip3 install pyueye --user" should do the trick)
* OpenCV for python, I've run this with 3.2.0 but it's hardly using cutting edge features so should probably cope with a fairly wide array of opencv versions.

# Notes
This seems to have trouble running in an IDE so if in doubt, run it from command line.

# Author
* David Lowndes (david@lownd.es)
