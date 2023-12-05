#_______________________________NOTES_________________________________________#
'''This code acquires pictures simultaneously with two Alvium cameras (can be edited to work with N cameras)
Requires installing the Vimba software (see documentation)
It only acquires, for now it doesn't stream
It doesn't work if vimba viewer is opened or if any other software/code is already accessing the cameras
When the terminal asks for input, type n to take a new picture, r to retake the previous picture, and n0/n1 or r0/r1 to do
    the same using only one of the two cameras
Careful not to overwrite images: they are always saved in save_path, numbered starting from init_frame, if an image with the
    same name already exists it is overwritten. It is advised to never change save_path, and instead move the useful pictures
    to a new directory when necessary.'''

#_____________________________LIBRARIES_______________________________________#
import cv2
from vimba import *
import threading
import numpy as np
import time
from matplotlib import pyplot as plt
import serial
import sys



#_____________________________FUNCTIONS_______________________________________#
# Frame acquisition
def acquire_frame(camera_index, ):
    
    lock.acquire()
    with Vimba.get_instance () as vimba:
        cams = vimba.get_all_cameras ()
        lock.release() # So that we don't access both cameras at the same time, prevents errors

        with cams [camera_index] as cam:
            frame = cam.get_frame ()
            frame.convert_pixel_format(PixelFormat.Mono8)
            img = frame.as_opencv_image()

            # Saving directory is always coherent with camera index, but display order sometimes isn't if we simply use append(), as the threads order might differ.
            # Instead of using lock.acquire() and lock.release(), we use an if so that append is used only if imgs_vect is empty, otherwise we use insert,
            # this way we into account camera index and upper/lower cameras are always displayed in the same way.
            if imgs_vect==[]:
                imgs_vect.append(img)
            else:
                imgs_vect.insert(camera_index, img)

            timestamp = int(time.time() * 1000)
            img_name = path + folder_names[camera_index] + str(camera_index)+ '-0' + str(timestamp) + "_cam" + '.png'

            cv2.imwrite(img_name, img)

# Plot two histograms side by side
def plot_2_hist(old_image, new_image,title_old="Orignal", title_new="New Image"):

    intensity_values=np.array([x for x in range(256)])
    plt.subplot(1, 2, 1)
    plt.bar(intensity_values, cv2.calcHist([old_image],[0],None,[256],[0,256])[:,0],width = 5)
    plt.title(title_old)
    plt.xlabel('Pixel intensity')
    plt.subplot(1, 2, 2)
    plt.bar(intensity_values, cv2.calcHist([new_image],[0],None,[256],[0,256])[:,0],width = 5)
    plt.title(title_new)
    plt.xlabel('Pixel intensity')
    plt.show()

#_________________________________INPUTS___________________________________________#
path = 'D:/DOCUMENTI_G/PoliMi/Magistrale/Tesi/Python/VIMBA/IMG/' # In this path there must be a folder named "A" and another named "B"
H_display = 600 # [pixels], used only for showing the acquired images
exp1 = 220000 # Exposure time [micro seconds] (min. 30k) One for each camera (not always the same one, changes each time we connect them)
exp2 = 220000
exp3 = 220000
#init_frame = 1 # It starts saving pictures using this index, if we don't want to overwrite images in save_path we can set init_frame higher than the last acquisition
use_threading = 1 # wether or not we want to use multi-threading (there should be no errors leaving it =1, and makes the code significantly faster)
show_hist = 1 # Histograms are shown if =1, otherwise they are not
show_saturation = 0 # shows saturated white pixels in red, and saturated black pixels in green [STILL NOT IMPLEMENTED]

#_________________________________MAIN CODE___________________________________________#
# Part 0: define constants and useful variables

lock = threading.Lock() # used to avoid errors (see acquire_frame function)
exp_vect = [exp1, exp2, exp3]
H_res = 2592 # Camera horizontal resolution [pixels]
V_res = 1944 # Camera vertical resolution [pixels]
AR = H_res / V_res
global folder_names # We will access it inside the threading function
folder_names=["A/", "B/", "C/"]
Ncams=3
time.sleep(2)
var=''

# Part 1: establishing features (exposure time,...)
def main(): #exposure, path, Ncams,
    print("Vimba", Ncams, path)
    cameras_list = list(range(Ncams)) #[0, 1, 2]

    # for k in cameras_list: # Use [0] for one camera, [0,1] for two
    for k in [0, 1, 2]:
        with Vimba.get_instance () as vimba:
            cams = vimba.get_all_cameras ()
            with cams [k] as cam:
                exposure_time = cam.ExposureTime
                exposure_time.set(exp_vect[k])

    # Part 2: image acquisition
    #N_IMG=init_frame-1 # Python starts counting from 0, not from 1, the nth element is actually the (n-1)

    global imgs_vect
    imgs_vect = []

    #Option with multithreading
    #for i in range(init_frame):
    thread_list=[]

    for j in cameras_list:
        thread = threading.Thread(target=acquire_frame, args=(j,)) # Each loop iteration creates a thread, one for each camera
        thread.start() # The thread starts
        thread_list.append(thread) # The thread is added to the list

    for t in thread_list:
        t.join()

# Image display after acquisition
# In case only one camera is being used we will also display a black image corresponding to the camera that is not being used

    # img_display = np.concatenate(imgs_vect, axis=0)
    #
    # win_name = "Frame couple " + str(init_frame) + ", upper = A, lower = B"
    # cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    # cv2.resizeWindow(win_name, int(H_display), int(H_display/AR*2))
    # cv2.moveWindow(win_name, 0, 0)
    # cv2.imshow(win_name, img_display)
    # cv2.waitKey(5)
    #
    # # Histogram display
    # if show_hist==1:
    #     plot_2_hist(imgs_vect[0], imgs_vect[1], "img1", "img2")

if __name__ == "__main__":
    main()