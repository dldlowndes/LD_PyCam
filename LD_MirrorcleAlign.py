from LD_PyCam import LD_PyCam
import cv2


class MirrorcleAligner(LD_PyCam):
    def __init__(self, cam_ID=0):
        """
        Nothing much new in here more than the parent class' constructor.
        Need to make a window with some controls in it though.
        """
        LD_PyCam.__init__(self, cam_ID)
        self._Make_Trackbars()

    def _Make_Trackbars(self):
        """
        The whole point of this class is to draw stuff on the camera image,
        for this to be useful the dimensions of said stuff needs to be
        controllable. Highgui is a quick and dirty way of doing this.
        """
        cv2.namedWindow("Sizes", cv2.WINDOW_NORMAL)

        # For the chip carrier.
        cv2.createTrackbar("Chip X pos",
                           "Sizes",
                           640,
                           1280,
                           lambda x: x)
        cv2.createTrackbar("Chip Y pos",
                           "Sizes",
                           512,
                           1024,
                           lambda x: x)
        cv2.createTrackbar("Chip size",
                           "Sizes",
                           200,
                           1024,
                           lambda x: x)

        # For the mirror
        cv2.createTrackbar("Mirror X pos",
                           "Sizes",
                           640,
                           1280,
                           lambda x: x)
        cv2.createTrackbar("Mirror Y pos",
                           "Sizes",
                           512,
                           1024,
                           lambda x: x)
        cv2.createTrackbar("Mirror size",
                           "Sizes",
                           200,
                           1024,
                           lambda x: x)

        # A bonus extra point for... purposes.
        cv2.createTrackbar("Extra X pos",
                           "Sizes",
                           640,
                           1280,
                           lambda x: x)
        cv2.createTrackbar("Extra Y pos",
                           "Sizes",
                           512,
                           1024,
                           lambda x: x)
        cv2.createTrackbar("Extra size",
                           "Sizes",
                           25,
                           1024,
                           lambda x: x)

    def _Draw_Circle(self, pos, radius, colour=(255, 0, 0)):
        """
        Draw a circle on the most recently collected image.
        pos is the (x,y) co-ordinate of the centre of the circle."
        """
        cv2.circle(self.img, pos, radius, color=colour)

    def _Draw_Rectangle(self, pos, dims, colour=(0, 255, 0)):
        """
        Draw a rectangle on the most recently collected image.
        pos is the (x,y) co-ordinate of the centre of the rectangle,
        dims is the (x,y) width/height of the rectangle.
        """
        pt1 = (pos[0] - dims[0]//2, pos[1] - dims[1]//2)
        pt2 = (pos[0] + dims[0]//2, pos[1] + dims[1]//2)

        cv2.rectangle(self.img, pt1, pt2, color=colour)

    def _Draw_Chip(self):
        """
        Get the size of the rectangle to draw on the image which will
        correspond to the chip carrier of the mirrorcle mirror.
        """
        self.chip_X = cv2.getTrackbarPos("Chip X pos", "Sizes")
        self.chip_Y = cv2.getTrackbarPos("Chip Y pos", "Sizes")
        self.chip_Size = cv2.getTrackbarPos("Chip size", "Sizes")

        self._Draw_Rectangle((self.chip_X, self.chip_Y),
                             (self.chip_Size, self.chip_Size),
                             (0, 255, 0))

    def _Draw_Mirror(self):
        """
        Get the size of the circle to draw on the image which will
        correspond to the actual mirror of the mirrorcle package.
        """
        self.mirror_X = cv2.getTrackbarPos("Mirror X pos", "Sizes")
        self.mirror_Y = cv2.getTrackbarPos("Mirror Y pos", "Sizes")
        self.mirror_Size = cv2.getTrackbarPos("Mirror size", "Sizes")

        self._Draw_Circle((self.mirror_X, self.mirror_Y),
                          self.mirror_Size//2,
                          (255, 0, 0))

    def _Draw_Extra(self):
        """
        Draw an extra point on the image whose position will also be given
        relative to the middle of the package in case there's other stuff
        to be measured on the camera feed (mounting holes?)
        """
        self.extra_X = cv2.getTrackbarPos("Extra X pos", "Sizes")
        self.extra_Y = cv2.getTrackbarPos("Extra Y pos", "Sizes")
        self.extra_Size = cv2.getTrackbarPos("Extra size", "Sizes")

        self._Draw_Circle((self.extra_X, self.extra_Y),
                          self.extra_Size//2,
                          (0, 0, 255))

    def Show_Overlay(self):
        """
        Draw all the shapes over the top of the most recently collected image.
        Returns like parent class' Show_Image which is the code of any keys
        pressed during the display of the image.
        """
        self._Draw_Chip()
        self._Draw_Mirror()
        self._Draw_Extra()

#        self.img = cv2.resize(self.img, (640, 512), cv2.INTER_LINEAR)
#        cv2.imshow("Sizes", self.img)
#        return cv2.waitKey(1)

        return self.Show_Image()

    def Get_Alignment_Info(self, chip_Size_mm=10):
        """
        Given the known dimension of the mirrorcle chip carrier (mm) and the
        known size of the box drawn around it on the image (pixels), get a
        scale factor which can be used to obtain a measurement (mm) from a
        number of pixels drawn on the image.
        """
        # Find the scale factor
        pix_Per_mm = self.chip_Size / chip_Size_mm
        self.logger.info(f"{pix_Per_mm} pixels per mm")

        # Find the offset between the centre of the mirror and the centre of
        # the chip carrier. Also the diameter of the mirror for good measure.
        x_Difference_Mirror = (self.mirror_X - self.chip_X) / pix_Per_mm
        y_Difference_Mirror = (self.mirror_Y - self.chip_Y) / pix_Per_mm
        mirror_Dia = self.mirror_Size / pix_Per_mm

        # Like with the mirror previously, do the same with the "Extra" point
        # which can be used to measure other features on the camera feed
        x_Difference_Extra = (self.extra_X - self.chip_X) / pix_Per_mm
        y_Difference_Extra = (self.extra_Y - self.chip_Y) / pix_Per_mm
        extra_Dia = self.extra_Size / pix_Per_mm

        # I guess a dict is the best way to present this output info?
        measured = {
                "mirror_Offset_XY": (x_Difference_Mirror,
                                     y_Difference_Mirror),
                "mirror Diameter": mirror_Dia,
                "extra_Point_Offset_XY": (x_Difference_Extra,
                                          y_Difference_Extra),
                "extra_Point_Diameter": extra_Dia,
                }
        self.logger.info(f"{measured}")
        return measured


if __name__ == "__main__":
    my_Cam = MirrorcleAligner()
    while True:
        my_Cam.Get_Image()

        kb_Hit = my_Cam.Show_Overlay()
        if kb_Hit == ord('q'):
            break

    print(my_Cam.Get_Alignment_Info(10))
    cv2.destroyAllWindows()
