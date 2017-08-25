# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: MPX Demodulator
# Author: Alexandre Marquet
# Generated: Fri Aug 25 15:36:33 2017
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from fm_audio_demod import fm_audio_demod  # grc-generated hier_block
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from rds_demod import rds_demod  # grc-generated hier_block
import math


class mpx_demod(gr.hier_block2):

    def __init__(self, audio_rate=48000, samp_rate=512e3):
        gr.hier_block2.__init__(
            self, "MPX Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signaturev(5, 5, [gr.sizeof_char*1, gr.sizeof_char*1, gr.sizeof_float*1, gr.sizeof_float*1, gr.sizeof_gr_complex*1]),
        )

        ##################################################
        # Parameters
        ##################################################
        self.audio_rate = audio_rate
        self.samp_rate = samp_rate

        ##################################################
        # Blocks
        ##################################################
        self.rds_demod_0 = rds_demod(
            samp_rate=samp_rate,
        )
        self.fm_audio_demod_0 = fm_audio_demod(
            audio_rate=audio_rate,
            samp_rate=samp_rate,
        )
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.band_pass_filter_0_1 = filter.fir_filter_ccf(1, firdes.band_pass(
        	1, samp_rate, 19e3-500, 19e3+500, 1e3, firdes.WIN_HAMMING, 6.76))
        self.analog_pll_refout_cc_0 = analog.pll_refout_cc(2 * math.pi * 8 / samp_rate, 2 * math.pi * (19000+4) / samp_rate, 2 * math.pi * (19000-4) / samp_rate)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0_0, 2))
        self.connect((self.band_pass_filter_0_1, 0), (self.analog_pll_refout_cc_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.fm_audio_demod_0, 1))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.rds_demod_0, 0))
        self.connect((self.fm_audio_demod_0, 0), (self, 1))
        self.connect((self.fm_audio_demod_0, 1), (self, 2))
        self.connect((self.fm_audio_demod_0, 2), (self, 3))
        self.connect((self, 0), (self.band_pass_filter_0_1, 0))
        self.connect((self, 0), (self.fm_audio_demod_0, 0))
        self.connect((self, 0), (self.rds_demod_0, 1))
        self.connect((self.rds_demod_0, 0), (self, 0))
        self.connect((self.rds_demod_0, 1), (self, 4))

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.fm_audio_demod_0.set_audio_rate(self.audio_rate)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rds_demod_0.set_samp_rate(self.samp_rate)
        self.fm_audio_demod_0.set_samp_rate(self.samp_rate)
        self.band_pass_filter_0_1.set_taps(firdes.band_pass(1, self.samp_rate, 19e3-500, 19e3+500, 1e3, firdes.WIN_HAMMING, 6.76))
        self.analog_pll_refout_cc_0.set_loop_bandwidth(2 * math.pi * 8 / self.samp_rate)
        self.analog_pll_refout_cc_0.set_max_freq(2 * math.pi * (19000+4) / self.samp_rate)
        self.analog_pll_refout_cc_0.set_min_freq(2 * math.pi * (19000-4) / self.samp_rate)
