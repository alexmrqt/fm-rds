# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: FM audio demodulator
# Author: Alexandre Marquet
# Generated: Fri Aug 25 15:48:40 2017
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes


class fm_audio_demod(gr.hier_block2):

    def __init__(self, audio_rate=48000, samp_rate=512e3):
        gr.hier_block2.__init__(
            self, "FM audio demodulator",
            gr.io_signaturev(2, 2, [gr.sizeof_gr_complex*1, gr.sizeof_gr_complex*1]),
            gr.io_signaturev(3, 3, [gr.sizeof_char*1, gr.sizeof_float*1, gr.sizeof_float*1]),
        )

        ##################################################
        # Parameters
        ##################################################
        self.audio_rate = audio_rate
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.thres_lo = thres_lo = 2
        self.thres_hi = thres_hi = 5
        self.avg_len = avg_len = int(1e6)

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_fff(
                interpolation=int(audio_rate),
                decimation=int(samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=int(audio_rate),
                decimation=int(samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.low_pass_filter_1_0 = filter.fir_filter_fff(1, firdes.low_pass(
        	1, audio_rate, 15e3, 1.5e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1 = filter.fir_filter_fff(1, firdes.low_pass(
        	1, audio_rate, 15e3, 1.5e3, firdes.WIN_HAMMING, 6.76))
        self.blocks_threshold_ff_0 = blocks.threshold_ff(thres_hi, thres_hi, 0)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_multiply_xx_2 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_moving_average_xx_0_0 = blocks.moving_average_ff(avg_len, 1.0, 4000)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(avg_len, 1.0, 4000)
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 1)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_complex_to_real_0_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_vff((-1, ))
        self.blocks_abs_xx_1 = blocks.abs_ff(1)
        self.blocks_abs_xx_0_0 = blocks.abs_ff(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)
        self.analog_fm_deemph_0_0_0_0 = analog.fm_deemph(fs=audio_rate, tau=50e-6)
        self.analog_fm_deemph_0_0_0 = analog.fm_deemph(fs=audio_rate, tau=50e-6)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_deemph_0_0_0, 0), (self, 1))
        self.connect((self.analog_fm_deemph_0_0_0_0, 0), (self, 2))
        self.connect((self.blocks_abs_xx_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_abs_xx_0_0, 0), (self.blocks_moving_average_xx_0_0, 0))
        self.connect((self.blocks_abs_xx_1, 0), (self.blocks_float_to_char_0, 0))
        self.connect((self.blocks_abs_xx_1, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_abs_xx_1, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_fm_deemph_0_0_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_complex_to_real_0_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_divide_xx_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_0_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_complex_to_real_0_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_multiply_xx_2, 1))
        self.connect((self.blocks_multiply_xx_2, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_xx_2, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_sub_xx_0, 0), (self.analog_fm_deemph_0_0_0_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_abs_xx_0_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_multiply_xx_2, 0))
        self.connect((self.low_pass_filter_1_0, 0), (self.blocks_abs_xx_0, 0))
        self.connect((self.low_pass_filter_1_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.low_pass_filter_1_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self, 1), (self.blocks_multiply_xx_0, 1))
        self.connect((self.rational_resampler_xxx_0, 0), (self.low_pass_filter_1_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.low_pass_filter_1, 0))

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.low_pass_filter_1_0.set_taps(firdes.low_pass(1, self.audio_rate, 15e3, 1.5e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.audio_rate, 15e3, 1.5e3, firdes.WIN_HAMMING, 6.76))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_thres_lo(self):
        return self.thres_lo

    def set_thres_lo(self, thres_lo):
        self.thres_lo = thres_lo

    def get_thres_hi(self):
        return self.thres_hi

    def set_thres_hi(self, thres_hi):
        self.thres_hi = thres_hi
        self.blocks_threshold_ff_0.set_hi(self.thres_hi)
        self.blocks_threshold_ff_0.set_lo(self.thres_hi)

    def get_avg_len(self):
        return self.avg_len

    def set_avg_len(self, avg_len):
        self.avg_len = avg_len
        self.blocks_moving_average_xx_0_0.set_length_and_scale(self.avg_len, 1.0)
        self.blocks_moving_average_xx_0.set_length_and_scale(self.avg_len, 1.0)
