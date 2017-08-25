# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: FM receiver
# Author: Alexandre Marquet
# Generated: Fri Aug 25 15:02:40 2017
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from mpx_demod import mpx_demod  # grc-generated hier_block
import math


class fm_receiver(gr.hier_block2):

    def __init__(self, audio_rate=48000, samp_rate=512e3):
        gr.hier_block2.__init__(
            self, "FM receiver",
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
        self.mpx_demod_0 = mpx_demod(
            audio_rate=audio_rate,
            samp_rate=samp_rate,
        )
        self.blocks_float_to_complex_0_0 = blocks.float_to_complex(1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(2*math.pi*75e3/samp_rate)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_float_to_complex_0_0, 0))
        self.connect((self.blocks_float_to_complex_0_0, 0), (self.mpx_demod_0, 0))
        self.connect((self.mpx_demod_0, 0), (self, 0))
        self.connect((self.mpx_demod_0, 1), (self, 1))
        self.connect((self.mpx_demod_0, 2), (self, 2))
        self.connect((self.mpx_demod_0, 3), (self, 3))
        self.connect((self.mpx_demod_0, 4), (self, 4))
        self.connect((self, 0), (self.analog_quadrature_demod_cf_0, 0))

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.mpx_demod_0.set_audio_rate(self.audio_rate)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.mpx_demod_0.set_samp_rate(self.samp_rate)
        self.analog_quadrature_demod_cf_0.set_gain(2*math.pi*75e3/self.samp_rate)
