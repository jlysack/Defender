import constants as const
import numpy as np

class SigProConfig:

    def __init__(self, Brd, min_range, max_range, noise_floor=-35):
        # Constant speed of light
        c0 = const.c0

        # Initialize TinyRad Board Config Object
        brd_cfg = BoardConfig()

        # Send RF Settings to TinyRad
        Brd.RfMeas(brd_cfg.dictify())

        # Read back board configuration
        num_channels = int(Brd.Get('NrChn')) # Number of receive channels (4)
        num_samples  = int(Brd.Get('N'))     # Number of samples measured
        samp_freq    = Brd.Get('fs')         # Sampling Frequency (1 MHz)

        # Processing of Range Profile
        NFFT = 2**12 # TODO: What to rename?

        hann_window_2d  = Brd.hanning(num_samples-1, 2*num_channels-1)
        sca_hann_window = np.sum(hann_window_2d[:,0])
        kf              = Brd.Get('kf') # TODO: What is this???
        range_vector    = np.arange(NFFT)/NFFT*samp_freq*c0/(2*kf)

        # Configure range interval to be displayed
        # min and max range in meters
        min_range_idx       = np.argmin(np.abs(range_vector - min_range)) # array index of min_range meters
        max_range_idx       = np.argmin(np.abs(range_vector - max_range)) # array index of RMax meters
        range_extent_vector = range_vector[min_range_idx:max_range_idx]        # array of ranges between min_range and max_range

        # Calculate Radar Data Rate
        data_rate = 16 * num_channels * num_samples * brd_cfg.FrmMeasSiz \
                     / (brd_cfg.FrmSiz * brd_cfg.Perd)

        # Window function for receive channels
        NFFTAnt          = 256 # TODO: What to rename?
        ant_window_2d    = Brd.hanning(2*num_channels-1, len(range_extent_vector))
        sca_ant_window   = np.sum(ant_window_2d[:,0])
        ant_window_2d    = ant_window_2d.transpose()
        angle_extent_vec = np.arcsin(2*np.arange(-NFFTAnt//2, NFFTAnt//2)/NFFTAnt)/np.pi*180

        # Store variables in object
        self.noise_floor      = noise_floor
        self.board_params     = brd_cfg
        self.num_channels     = num_channels
        self.num_samples      = num_samples
        self.samp_freq        = samp_freq
        self.NFFT             = NFFT
        self.hann_window_2d   = hann_window_2d
        self.sca_hann_window  = sca_hann_window
        self.kf               = kf
        self.range_vector     = range_vector
        self.min_range        = min_range
        self.max_range        = max_range
        self.min_range_idx    = min_range_idx
        self.max_range_idx    = max_range_idx
        self.range_extent_vec = range_extent_vector
        self.data_rate        = data_rate
        self.NFFTAnt          = NFFTAnt
        self.ant_window_2d    = ant_window_2d
        self.sca_ant_window   = sca_ant_window 
        self.angle_extent_vec = angle_extent_vec
        self.logger           = None

class PlotConfig:

    def __init__(self):
        self.frame_numbers  = False # print frame numbers (deprecated)
        self.time_signals   = False # plot time-domain signals (deprecated)
        self.range_profile  = False # plot range profiles
        self.sum_data       = False # plot sum of all 7 range profile channels across all angles
        self.az_data        = False # plot sum of all 7 range profile channels across all range cells
        self.heat_map       = False # plot 2D heat map of amplitudes across angle and range

class BoardConfig:

    def __init__(self):
        # NOTE: These values coems from the TinyRad datasheet and CANNOT be
        #       modified, since they are used internally within the TinyRad via
        #       the Brd.RfMeas() function
        self.fStrt          = 24.00e9   # Chirp Frequency Start (GHz)
        self.fStop          = 24.25e9   # Chirp Frequency Stop (GHz)
        self.TRampUp        = 256e-6    # Duration of the upchirp (sec)
        self.N              = 256       # Number of samples per chirp (for 1 MHz, = TRampUp * 1000000)
        self.Perd           = 0.4e-3    # Chirp repetition interval (sec)
        self.Seq            = [1, 2]    # Array used to hold antenna sequence
        self.CycSiz         = 4         # Number of buffers in the DSP to store data
        self.FrmSiz         = 128       # Number of chirps for one measurement cycle NOTE: this affects runtime speed a lot
        self.FrmSiz         = 1       # Number of chirps for one measurement cycle NOTE: this affects runtime speed a lot
        self.FrmMeasSiz     = 1         # Number of chirps in which data is collected
    
        # Table 6 from TinyRad Datasheet
        #self.fStrt          = 24.00e9   # Chirp Frequency Start (GHz)
        #self.fStop          = 24.25e9   # Chirp Frequency Stop (GHz)
        #self.TRampUp        = 512e-6    # Duration of the upchirp (sec)
        #self.N              = 512       # Number of samples per chirp (for 1 MHz, = TRampUp * 1000000)
        #self.Perd           = 1.0e-3    # Chirp repetition interval (sec)
        #self.Seq            = [1]    # Array used to hold antenna sequence
        #self.CycSiz         = 2         # Number of buffers in the DSP to store data
        #self.FrmSiz         = 4       # Number of chirps for one measurement cycle NOTE: this affects runtime speed a lot
        #self.FrmMeasSiz     = 2         # Number of chirps in which data is collected

        # Table 7 from TinyRad Datasheet
        #self.fStrt          = 24.00e9   # Chirp Frequency Start (GHz)
        #self.fStop          = 24.25e9   # Chirp Frequency Stop (GHz)
        #self.TRampUp        = 256e-6    # Duration of the upchirp (sec)
        #self.N              = 256       # Number of samples per chirp (for 1 MHz, = TRampUp * 1000000)
        #self.Perd           = 0.3e-3    # Chirp repetition interval (sec)
        #self.Seq            = [1, 2]    # Array used to hold antenna sequence
        #self.CycSiz         = 2         # Number of buffers in the DSP to store data
        #self.FrmSiz         = 3       # Number of chirps for one measurement cycle NOTE: this affects runtime speed a lot
        #self.FrmMeasSiz     = 2         # Number of chirps in which data is collected

    # Put Boardconfig contents into a dictionary for use with Brd.RfMeas
    def dictify(self):
        brd_cfg = dict()

        brd_cfg['fStrt']        = self.fStrt
        brd_cfg['fStop']        = self.fStop
        brd_cfg['TRampUp']      = self.TRampUp
        brd_cfg['Perd']         = self.Perd
        brd_cfg['N']            = self.N
        brd_cfg['Seq']          = self.Seq
        brd_cfg['CycSiz']       = self.CycSiz
        brd_cfg['FrmSiz']       = self.FrmSiz
        brd_cfg['FrmMeasSiz']   = self.FrmMeasSiz

        return brd_cfg
