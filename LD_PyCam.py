import ctypes
import cv2
from pyueye import ueye
import logging


class LD_PyCam:
    def __init__(self, cam_ID=0):
        """
        Connect to the camera specified by cam_ID, or 0 for the first available
        camera on the system. Then set up the basic camera settings.
        """
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.m_hG = ctypes.c_uint(cam_ID)
        m_Ret = 0
        self.logger.debug(f"Attempt to open camera {cam_ID}")
        m_Ret = ueye.is_InitCamera(self.m_hG, None)
        self.logger.debug(f"Camera says: {m_Ret}")

        # Hard code for now, is_GetSensorInfo doesn't seem to return sense
        # for the actual colour mode set.
        colour_Mode = ueye.IS_CM_BGR8_PACKED
        self.bitsPixel = 24  # 8 bits per channel (of which there are 3).
        self.logger.debug(f"Set colour mode to {colour_Mode}")
        m_Ret = ueye.is_SetColorMode(self.m_hG, colour_Mode)
        self.logger.debug(f"Camera says: {m_Ret}")

        # Sensor info gives useful information about frame size etc.
        self.logger.debug(f"Ask camera for info")
        self.sensorInfo = ueye.SENSORINFO()
        m_Ret = ueye.is_GetSensorInfo(self.m_hG, self.sensorInfo)
        self.logger.debug(f"Camera says {m_Ret}")

        # I think for most purposes software trigger is the solution.
        self.logger.debug(f"Set trigger")
        m_Ret = ueye.is_SetExternalTrigger(self.m_hG,
                                           ueye.IS_SET_TRIGGER_SOFTWARE)
        self.logger.debug(f"Camera says {m_Ret}")

        # Memory for the camera to dump image data to.
        self.logger.debug(f"Allocate memory")
        self.pcmem = ueye.c_mem_p()
        self.memID = ueye.c_int()
        m_Ret = ueye.is_AllocImageMem(self.m_hG,
                                      self.sensorInfo.nMaxWidth,
                                      self.sensorInfo.nMaxHeight,
                                      self.bitsPixel,
                                      self.pcmem,
                                      self.memID)
        m_Ret = ueye.is_SetImageMem(self.m_hG, self.pcmem, self.memID)
        self.logger.debug(f"Camera says {m_Ret}")

        # Some default known pixel clock, frame rate and exposure.
        self.Set_Exposure(24, 10, 5)

    def __del__(self):
        """
        Make sure the camera is disconnected if the object gets destroyed.
        """
        self.Close()

    def Close(self):
        """
        Gracefully disconnect from the camera to make it available for other
        programs (or a different instance of this!)
        """
        ueye.is_ExitCamera(self.m_hG)
        cv2.destroyAllWindows()

    def Set_Exposure(self, pixel_Clock, frame_Rate, exposure):
        """
        Change the pixel clock, frame rate and exposure time of the camera.
        Care should be taken in choosing compatible values which is why this is
        one method. Obviously exposure <= 1/frame_Rate. Higher pixel clocks
        allow higher frame rates at the cost of power, heat and potential
        transmission errors.
        """
        self.logger.info(f"Set pixel clock {pixel_Clock} "
                         f"Set frame rate {frame_Rate} "
                         f"Set exposure {exposure}")
        m_pixel_Clock = ctypes.c_uint(pixel_Clock)
        m_exposure = ctypes.c_double(exposure)
        newframerate = ctypes.c_double(0)

        m_Ret = ueye.is_PixelClock(self.m_hG,
                                   ueye.IS_PIXELCLOCK_CMD_SET,
                                   m_pixel_Clock,
                                   ctypes.sizeof(m_pixel_Clock))
        self.logger.debug(f"Pixel clock says {m_Ret}")

        m_Ret = ueye.is_SetFrameRate(self.m_hG, frame_Rate, newframerate)
        self.logger.debug(f"Frame rate says {m_Ret}")
        self.logger.debug(f"new frame rate {newframerate.value}")

        m_Ret = ueye.is_Exposure(self.m_hG,
                                 ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,
                                 m_exposure,
                                 ctypes.sizeof(m_exposure))
        self.logger.debug(f"Exposure says {m_Ret}")

    def Get_Image(self):
        """
        Take a frame from the camera into the memory allocated for the frames,
        take that data and put into a format opencv understands as an image
        (basically a 3D numpy array). Returns the numpy array but also updates
        the member variable self.img with the same data.
        """
        self.logger.debug(f"Take image")
        m_Ret = ueye.is_FreezeVideo(self.m_hG, ueye.IS_WAIT)
        self.logger.debug(f"Camera says {m_Ret}")

        lineinc = self.sensorInfo.nMaxWidth * int((self.bitsPixel + 7) / 8)
        img = ueye.get_data(self.pcmem,
                            self.sensorInfo.nMaxWidth,
                            self.sensorInfo.nMaxHeight,
                            self.bitsPixel,
                            lineinc,
                            True)
        self.img = img.reshape((int(self.sensorInfo.nMaxHeight),
                                int(self.sensorInfo.nMaxWidth), 3))
        self.logger.debug(f"Image of dims {self.img.shape} taken")
        return self.img

    def Show_Image(self):
        """
        Show the most recently collected image in an opencv window. Returns
        the code for any key pressed during the displaying of the image.
        """
        self.logger.debug(f"Display image")
        cv2.imshow("hi", self.img)
        kb_Hit = cv2.waitKey(1)
        if (kb_Hit != 255):
            self.logger.debug(f"Key press registered {kb_Hit}")
        return kb_Hit

    def Save_Image(self, filename):
        """
        Save the most recently collected image to file. Opencv infers the
        format from the supplied filename"
        """
        self.logger.info(f"Save image as {filename}")
        m_Ret = cv2.imwrite(filename, self.img)
        self.logger.debug(f"Save image says {m_Ret}")


if __name__ == "__main__":
    my_Cam = LD_PyCam(0)
    while True:
        my_Cam.Get_Image()
        kb_Hit = my_Cam.Show_Image()

        if kb_Hit == ord('q'):
            break
    my_Cam.Close()
