# Design-and-calibration-of-a-multi-view-multi-illumination-imaging-system
This folder contains the codes for acquiring images with a Python GUI, which manages three subprograms. 
The main file is called GUI_complex.py and can manage two different types of cameras: IDS or Alvium.
The IDS ones are directly managed through the two subprograms called test_camera.py and cameraIDSN.py; the Alvium cameras
are managed by the program called acquisizioni_vimba_originale.
The main program GUI_complex can perform an image acquisition procedure by using an arbitrary number of cameras and it can also control
a LED illumination system through an Arduino UNO.
To save the images the user has to select a path in which he wants to store the picture acquired.
The other two files stereo_calibration2.hdev and stereo_calibration3.hdev are two simple programs that can calibrate a multi-camera systems,
in particular the first one can calibrate a stereo-vision system, the second one can calibrate a trinocular system.
