

class SigProConfig:

    def __init__(self):
        self.N = 1



class PlotConfig:

    def __init__(self):
        self.frame_numbers  = False
        self.time_signals   = False
        self.range_profile  = False
        self.sum_data       = False
        self.dbf_cost_func  = False

class BoardConfig:

    def __init__(self):
        self.fStrt = 24.00e9
        self.fStop = 24.25e9
        self.TRampUp = 256e-6
        self.Perd = 0.4e-3
        self.N = 256
        self.Seq = [1, 2]
        self.CycSiz = 4
        self.FrmSiz = 128
        self.FrmMeasSiz = 1

