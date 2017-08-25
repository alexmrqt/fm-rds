# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: RDS demodulator
# Author: Alexandre Marquet
# Generated: Fri Aug 25 12:27:37 2017
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio import trellis
from gnuradio import trellis, digital
from gnuradio.filter import firdes
import numpy


class rds_demod(gr.hier_block2):

    def __init__(self, samp_rate=512e3):
        gr.hier_block2.__init__(
            self, "RDS demodulator",
            gr.io_signaturev(2, 2, [gr.sizeof_gr_complex*1, gr.sizeof_gr_complex*1]),
            gr.io_signaturev(2, 2, [gr.sizeof_char*1, gr.sizeof_gr_complex*1]),
        )

        ##################################################
        # Parameters
        ##################################################
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.bitrate = bitrate = 1187.5
        self.syms_rate = syms_rate = 2*bitrate
        self.samp_per_sym = samp_per_sym = 4
        self.prefix = prefix = "radio/"

        self.variable_constellation_0 = variable_constellation_0 = digital.constellation_bpsk().base()

        self.fsm = fsm = trellis.fsm(prefix+"diff_manchester.fsm")
        self.decim = decim = int(samp_rate/(samp_per_sym*syms_rate))

        self.RRC_filtr_taps = RRC_filtr_taps = firdes.root_raised_cosine(10, samp_rate, syms_rate, 1, int(6*samp_rate/syms_rate))


        ##################################################
        # Blocks
        ##################################################
        self.trellis_viterbi_x_0 = trellis.viterbi_b(trellis.fsm(fsm), 10000, 0, -1)
        self.trellis_metrics_x_0 = trellis.metrics_c(fsm.O(), 2, (-1, -1, -1, 1, 1, -1, 1, 1), digital.TRELLIS_EUCLIDEAN)
        self.fir_filter_xxx_0 = filter.fir_filter_ccf(decim, (RRC_filtr_taps))
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_lms_dd_equalizer_cc_0_0 = digital.lms_dd_equalizer_cc(1, 0.1, 1, variable_constellation_0)
        self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_cc(samp_rate/decim/syms_rate, 0.25*0.175*0.175, 0.5, 0.175, 0.005)
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_multiply_xx_1, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_lms_dd_equalizer_cc_0_0, 0))
        self.connect((self.digital_lms_dd_equalizer_cc_0_0, 0), (self, 1))
        self.connect((self.digital_lms_dd_equalizer_cc_0_0, 0), (self.trellis_metrics_x_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.digital_clock_recovery_mm_xx_0, 0))
        self.connect((self, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self, 1), (self.blocks_multiply_xx_1, 0))
        self.connect((self.trellis_metrics_x_0, 0), (self.trellis_viterbi_x_0, 0))
        self.connect((self.trellis_viterbi_x_0, 0), (self, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_decim(int(self.samp_rate/(self.samp_per_sym*self.syms_rate)))
        self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_rate/self.decim/self.syms_rate)

    def get_bitrate(self):
        return self.bitrate

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate
        self.set_syms_rate(2*self.bitrate)

    def get_syms_rate(self):
        return self.syms_rate

    def set_syms_rate(self, syms_rate):
        self.syms_rate = syms_rate
        self.set_decim(int(self.samp_rate/(self.samp_per_sym*self.syms_rate)))
        self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_rate/self.decim/self.syms_rate)

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.set_decim(int(self.samp_rate/(self.samp_per_sym*self.syms_rate)))

    def get_prefix(self):
        return self.prefix

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.set_fsm(trellis.fsm(self.prefix+"diff_manchester.fsm"))

    def get_variable_constellation_0(self):
        return self.variable_constellation_0

    def set_variable_constellation_0(self, variable_constellation_0):
        self.variable_constellation_0 = variable_constellation_0

    def get_fsm(self):
        return self.fsm

    def set_fsm(self, fsm):
        self.fsm = fsm
        self.trellis_viterbi_x_0.set_FSM(trellis.fsm(self.fsm))

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_rate/self.decim/self.syms_rate)

    def get_RRC_filtr_taps(self):
        return self.RRC_filtr_taps

    def set_RRC_filtr_taps(self, RRC_filtr_taps):
        self.RRC_filtr_taps = RRC_filtr_taps
        self.fir_filter_xxx_0.set_taps((self.RRC_filtr_taps))
