from pynq import Overlay,PL
import cffi
from pz1sofi.general_const import *

class pz1sofi():
    """Class to control the Sobel filter hardware

    Attributes
    ----------
    bitfile : str
    Absolute path to bitstream
    libfile : str
    Absolute path to shared library
    overlay : Overlay
    Pynq-Z1 Sobel filter overlay
    frame_gray : 
    Pointer to intermediate gray image
    """

    def __init__(self):
        #Set attributes
        self.bitfile = BITFILE
        self.libfile = LIBFILE
        self._ffi = cffi.FFI()
        #Accelerator functions
        self._ffi.cdef("void _p0_rgb_2_gray_0(uint8_t * input,"+
                       "uint8_t * output);")
        self._ffi.cdef("void _p0_sobel_filter_0(uint8_t * input,"+
                       "uint8_t * output);")
        self._ffilib =  self._ffi.dlopen(LIBFILE)
        self.overlay = Overlay(self.bitfile)
        #XLNK functions
        self._ffi.cdef("void *cma_alloc(uint32_t len,"+
                       "uint32_t cacheable);")
        self._ffi.cdef("void cma_free(void *buf);")
        #Allocate memory for gray frame 
        self.frame_gray = self._ffi.cast("uint8_t *",
        self._ffilib.cma_alloc(1920*1080,0))
        #Check if bitstream is loaded
        if not Overlay.is_loaded(self.overlay):
            self.overlay.download()

    def get_frame_ptr(self, hdmi_in_frame):
        """...
        """
        return self._ffi.cast("uint8_t *",hdmi_in_frame.frame_addr())

    def sobel_filter(self,frame_in, frame_out, num_frames=1, get_fps=False):
        """...
        """
        if get_fps:
            import time
            time1 = time.time()
        for i in range(num_frames):
            self._ffilib._p0_rgb_2_gray_0(frame_in,self.frame_gray)
            self._ffilib._p0_sobel_filter_0(self.frame_gray,frame_out)
        if get_fps:
            time2 = time.time()
            return num_frames/(time2-time1)

    def __del__(self):
        #Deallocate memory for gray frame 
        self._ffilib.cma_free(self._ffi.cast("void *",self.frame_gray))

