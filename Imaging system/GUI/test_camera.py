#_______________________________LIBRARIES_________________________________________#
import threading
import cameraIDSN
import time
import string
import os

#_________________________________NOTES___________________________________________#
'''
-> Camera ids must be set manually using IDS camera manager, otherwise it won't work
    Set them to 1, 2, 3,... n, do not set any of them to 0

-> This code requires a second script, cameraIDSN.py, to work.
    Some inputs must be defined in both scripts (see inputs section)

-> If the required folders for image saving do not exist, the code will create them in GOLBAL_PATH automatically
    GOLBAL_PATH must have the format 'dir1/dir2/dir3/...', not 'dir1\\dir2\\dir3\\...' nor r'dir1\dir2\dir3\...'
'''

#_________________________________INPUTS__________________________________________#

# Many other inputs are in cameraIDSN.py. 
# CAREFUL!!! These initial inputs must also be defined in cameraIDSN, and they must be identical
path='D:/DOCUMENTI_G/PoliMi/Magistrale/Tesi/Python/IDS/Images2/' # Must be dir1/dir2/...
Ncams = 3
init_picture = 0 # It does nothing if =0, set it higher to avoid overwriting files in GLOBAL_PATH

exposure = 200 # ms
alphabet = string.ascii_uppercase
exp_vect = []
camNames_vect = []

for k in range(Ncams):
    camNames_vect.append(alphabet[k])
    exp_vect.append(exposure)

## We can manually set cameras names and exposure times using the two following lines
#camNames_vect = ["A", "B", "C"]
#exp_vect = [25, 25, 10] # [ms]


########### Other inputs (these only need to be defined in this code)
TIME_PERIOD=3 # >=1
#N_IMG=10       # Can be used for acquiring multiple images with each camera (for now it doesn't do it)
filename=""

#_________________________________MAIN CODE___________________________________________#

def main(path, Ncams,):  #exposure
    print("Test camera")
    cameraIDSN.initMulticams(Ncams,)  #exposure
    cameraIDSN.initMemory(Ncams)

    for camName in camNames_vect:
        try:
            new_path = path + "/" + camName
            os.mkdir(new_path)
        except:
            pass

def pic_event(N_img):
    timestamp = int(time.time())
    starttime=time.time()
    thread_list = []
    for nthread in range(Ncams):
        filename=str(nthread+1)+"-0"+str(timestamp)
        print('\nTaking pic n°: ' + str(timestamp) + ', filename : ', filename + '.png')
        t = threading.Thread(target=cameraIDSN.acquireSingleImage, args=(filename, nthread,))
        t.start() # starting threads
        thread_list.append(t)
    for nthread in thread_list:
        nthread.join() # wait until threads are completely executed
    time.sleep(TIME_PERIOD - ((time.time() - starttime)))

def close_camera():
    cameraIDSN.closeCamera(Ncams)

if __name__ == "__main__":
    main()
