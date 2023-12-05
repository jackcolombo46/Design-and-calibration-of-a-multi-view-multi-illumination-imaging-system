from pyueye import ueye
import numpy as np
import cv2 as cv
import time
import string

#############################################################################
##############################     INPUTS      ##############################
# CAREFUL!!! These initial inputs must be defined both here and in N_cams_acquisition.py
GLOBAL_PATH = 'D:/DOCUMENTI_G/PoliMi/Magistrale/Tesi/Python/IDS/Images2/'
Ncams = 3

exposure = 200  # ms
alphabet = string.ascii_uppercase
exp_vect = []
camNames_vect = []
for k in range(Ncams):
    camNames_vect.append(alphabet[k])
    exp_vect.append(exposure)

## We can manually set cameras names and exposure times using the two following lines
#exp_vect = [25, 25, 10]
# camNames_vect = ["A", "B", "C"]


########### Other inputs (these only need to be defined in this code)
# acquisition parameters:
pixelClock = 30  # 30, 59, 118, 237, 474
gain = 30
triggerDelay = 0  # us (int)
AOIstartX = 0  # pixel (int)
AOIstartY = 0  # pixel (int)
AOIwidth = 1936  # pixel (int)
AOIheight = 1216  # pixel (int)

############
# CAMERA PARAMETERS
################
pcImageMemory_vect = []
hCam_vect = []
MemID_vect = []
exposure_vect = []
for k in range(Ncams):
    hCam_vect.append(ueye.HIDS(k + 1))
    pcImageMemory_vect.append(ueye.c_mem_p())
    MemID_vect.append(ueye.int())
    exposure_vect.append(ueye.double(exp_vect[k]))

frameRate = ueye.double(1.0)
flashParameter = ueye.IO_FLASH_PARAMS()
imageAOI = ueye.IS_RECT()
imageAOI.s32X = ueye.int(AOIstartX)
imageAOI.s32Y = ueye.int(AOIstartY)
imageAOI.s32Width = ueye.int(AOIwidth)
imageAOI.s32Height = ueye.int(AOIheight)
pixelClockVal = ueye.uint(pixelClock)

triggDelay = ueye.int(triggerDelay)
ISOgain = ueye.int(gain)
rGain = ueye.int(0)
gGain = ueye.int(0)
bGain = ueye.int(0)
bitPerPixel = ueye.int(8)
frameWidth = ueye.int(AOIwidth)
frameHeight = ueye.int(AOIheight)


def initMulticams(Ncams, ): #exposure
    for k in range(Ncams):
        initSingleCamera(hCam_vect[k], camNames_vect[k], exposure_vect[k], camNames_vect[k]) #


def initSingleCamera(hCam, idCam, exposure_time, camName):
    nRet = 0
    nRet = ueye.is_InitCamera(hCam, None)
    print("--------->", idCam)
    if nRet != ueye.IS_SUCCESS:
        print("is_InitCamera ERROR")
        print("nRet error code: ", nRet)
        exit()

    # Reset camera to default parameters
    nRet = ueye.is_ResetToDefault(hCam)
    if nRet != ueye.IS_SUCCESS:
        print("is_ResetToDefault ERROR")

    # Set camera gain
    nRet = ueye.is_SetHardwareGain(hCam, ISOgain, rGain, gGain,
                                   bGain)  # ueye.IS_IGNORE_PARAMETER, ueye.IS_IGNORE_PARAMETER, # ueye.IS_IGNORE_PARAMETER)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetHardwareGain ERROR")

    # Set gain boost
    nRet = ueye.is_SetGainBoost(hCam, ueye.IS_SET_GAINBOOST_OFF)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetGainBoost ERROR")

    # Set pixel clock
    nRet = ueye.is_PixelClock(hCam, ueye.IS_PIXELCLOCK_CMD_SET, pixelClockVal, ueye.sizeof(pixelClockVal))
    if nRet != ueye.IS_SUCCESS:
        print("set pixel clock error")

    actual_frameRate = ueye.double()
    nRet = ueye.is_SetFrameRate(hCam, frameRate, actual_frameRate)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetFrameRate ERROR")

    # Set the exposure time for the frame
    print(idCam)
    exposure_new = ueye.double()
    nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, exposure_time, ueye.sizeof(exposure_time))
    if nRet != ueye.IS_SUCCESS:
        print("is_SetExposure ERROR")
    else:
        nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, exposure_new, ueye.sizeof(exposure_new))
        if nRet != ueye.IS_SUCCESS:
            print("is_GetExposure ERROR")
        else:
            exposure_new = exposure_new.value
            print("Exposure time ", camName, ": ", exposure_new)

    # Retrieve the current frame dimension (Area Of Interest)
    nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_SET_AOI, imageAOI, ueye.sizeof(imageAOI))
    if nRet != ueye.IS_SUCCESS:
        print("is_AOI ERROR")
    else:
        frameWidth = imageAOI.s32Width
        frameHeight = imageAOI.s32Height

    colorMode = ueye.int(ueye.IS_CM_MONO8)  # (ueye.IS_CM_RGB8_PACKED)#(ueye.IS_CM_MONO8)
    nRet = ueye.is_SetColorMode(hCam, colorMode)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetColorMode ERROR")

    # Set trigger mode for sync (rising edge)
    nRet = ueye.is_SetExternalTrigger(hCam, ueye.IS_SET_TRIGGER_SOFTWARE)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetExternalTrigger ERROR")

    nRet = ueye.is_SetTriggerDelay(hCam, triggDelay)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetTriggerDealy ERROR")


def initMemory(Ncams):
    # Allocates the image memory of size frameWidth x frameHeight and its color depth of bitPerPixel
    for k in range(Ncams):
        nRet = ueye.is_AllocImageMem(hCam_vect[k], frameWidth, frameHeight, bitPerPixel, pcImageMemory_vect[k],MemID_vect[k])
        if nRet != ueye.IS_SUCCESS:
            print("is_AllocImageMem ERROR")
        else:
            # Makes the specified image memory the active memory
            nRet = ueye.is_SetImageMem(hCam_vect[k], pcImageMemory_vect[k], MemID_vect[k])
            if nRet != ueye.IS_SUCCESS:
                print("is_SetImageMem ERROR")


def acquireSingleImage(filename, k):
    bytePerPixel = int(bitPerPixel / 8)
    image = np.zeros((frameHeight.value, frameWidth.value, bytePerPixel), dtype=np.uint8)
    nRet = ueye.is_FreezeVideo(hCam_vect[k], ueye.IS_WAIT)
    nRetCopy = ueye.is_CopyImageMem(hCam_vect[k], pcImageMemory_vect[k], MemID_vect[0], image.ctypes.data)
    # print(time.time_ns())

    filePath = GLOBAL_PATH + "/" + camNames_vect[k] + "/" + filename + ".png"
    cv.imwrite(filePath, image)
    # print('stored image ' + camNames_vect[k] + 'in path: ' + str(filePath))
    if nRet != ueye.IS_SUCCESS:
        print("is_FreezeVideo ERROR")
        print(nRet, nRetCopy)
    if nRetCopy != ueye.IS_SUCCESS:
        print("is_CopyImageMem ERROR")


def closeCamera(Ncams):
    for k in range(Ncams):
        # Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
        ueye.is_FreeImageMem(hCam_vect[k], pcImageMemory_vect[k], MemID_vect[k])
        # Disables the hCam camera handle and releases the data structures and memory areas taken up by the uEye camera
        ueye.is_ExitCamera(hCam_vect[k])
    # Destroys the OpenCv windows
    cv.destroyAllWindows()