#!/usr/bin/env python

import radio.fm_receiver as fmr
import radio.rds_synchronizer as rds_sync
import decoder.rds_decoder as rds_dec
import rds_handlers as rds_handlers
import threading
import time
import sys
import getopt

from PyQt4 import Qt
from PyQt4.QtCore import QObject, pyqtSlot
import PyQt4.Qwt5 as Qwt

from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.filter import firdes
#import osmosdr
import sip

class radio(gr.top_block, Qt.QWidget):
    def __init__(self, tuner, gain, card, samp_rate):
        #Gnuradio top_block constructor
        gr.top_block.__init__(self, "Top Block")

        #QT widget constructor
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FM Radio")
        try:
             self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
             pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Attributes
        ##################################################
        self.tuner = tuner
        self.freq_offset = freq_offset = 0;
        self.gain = gain

        self.samp_rate = samp_rate;
        self.audio_rate = audio_rate = 48000;
        self.fm_sample_rate= fm_sample_rate = 512e3;

        ##################################################
        # Variables
        ##################################################
        fm_start = 87.5e6;
        fm_stop = 108e6;
        rtlsdr_gains = [0.0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7,
                16.6, 19.7, 20.7, 22.9, 25.4, 28.0, 29.7, 32.8, 33.8, 36.4,
                37.2, 38.6, 40.2, 42.1, 43.4, 43.9, 44.5, 48.0, 49.6];

        ##################################################
        # Blocks
        ##################################################
        if(card == "rtlsdr"):
            self.freq_offset=freq_offset=250e3;
            self.source = osmosdr.source( args="numchan=" + str(1) + " " + "" )
            self.source.set_sample_rate(samp_rate)
            self.source.set_center_freq(tuner-freq_offset, 0)
            self.source.set_freq_corr(0, 0)
            self.source.set_dc_offset_mode(0, 0)
            self.source.set_iq_balance_mode(0, 0)
            self.source.set_gain_mode(False, 0)
            self.source.set_gain(gain, 0)
            self.source.set_if_gain(20, 0)
            self.source.set_bb_gain(20, 0)
            self.source.set_antenna("", 0)
            self.source.set_bandwidth(0, 0)
        elif(card == "usrp"):
            self.freq_offset=freq_offset=0;
            self.source = uhd.usrp_source(
                    ",".join(("", "")),
                    uhd.stream_args(
                            cpu_format="fc32",
                            channels=range(1),
                    ),
            )
            self.source.set_samp_rate(samp_rate)
            self.source.set_center_freq(tuner-freq_offset, 0)
            self.source.set_gain(gain, 0)
        else:
            print "Unrecognized device ",
            print card
            sys.exit(2);

        self.channel_xlating_filter = filter.freq_xlating_fir_filter_ccc(
                1, (1, ), freq_offset, samp_rate);
        self.rational_resampler = filter.rational_resampler_ccc(
                interpolation=int(fm_sample_rate), decimation=int(samp_rate),
                taps=None, fractional_bw=None);
        self.fm_receiver = fmr.fm_receiver(audio_rate, fm_sample_rate);
        self.rds_sync = rds_sync.rds_synchronizer();
        self.rds_dec = rds_dec.rds_decoder();
        self.register_rds_handlers();
        self.audio_sink = audio.sink(audio_rate, "", True)

        ##################################################
        # GUI blocks
        ##################################################
        #Tuner bar
        self.tuner_layout = Qt.QVBoxLayout()
        self.tuner_tool_bar = Qt.QToolBar(self)
        self.tuner_layout.addWidget(self.tuner_tool_bar)
        self.tuner_tool_bar.addWidget(Qt.QLabel("tuner"+": "))
        class qwt_counter_pyslot(Qwt.QwtCounter):
            def __init__(self, parent=None):
                Qwt.QwtCounter.__init__(self, parent)
            @pyqtSlot('double')
            def setValue(self, value):
                super(Qwt.QwtCounter, self).setValue(value)
        self.tuner_counter = qwt_counter_pyslot()
        self.tuner_counter.setRange(fm_start, fm_stop, 0.1e6)
        self.tuner_counter.setNumButtons(2)
        self.tuner_counter.setValue(self.tuner)
        self.tuner_counter.valueChanged.connect(self.set_tuner)
        self.tuner_tool_bar.addWidget(self.tuner_counter)
        self.tuner_slider = Qwt.QwtSlider(None, Qt.Qt.Horizontal,
                Qwt.QwtSlider.BottomScale, Qwt.QwtSlider.BgSlot)
        self.tuner_slider.setRange(fm_start, fm_stop, 0.1e6)
        self.tuner_slider.setValue(self.tuner)
        self.tuner_slider.setMinimumWidth(200)
        self.tuner_slider.valueChanged.connect(self.set_tuner)
        self.tuner_layout.addWidget(self.tuner_slider)
        self.top_layout.addLayout(self.tuner_layout)

        #Gain chooser
        self.gain_options = rtlsdr_gains;
        self.gain_labels = map(str, self.gain_options)
        self.gain_tool_bar = Qt.QToolBar(self)
        self.gain_tool_bar.addWidget(Qt.QLabel("gain"+": "))
        self.gain_combo_box = Qt.QComboBox()
        self.gain_tool_bar.addWidget(self.gain_combo_box)
        for label in self.gain_labels: self.gain_combo_box.addItem(label)
        self.gain_callback = lambda i: Qt.QMetaObject.invokeMethod(
                self.gain_combo_box, "setCurrentIndex",
                Qt.Q_ARG("int", self.gain_options.index(i)))
        self.gain_callback(self.gain)
        self.gain_combo_box.currentIndexChanged.connect(
            lambda i: self.set_gain(self.gain_options[i]))
        self.top_layout.addWidget(self.gain_tool_bar)

        #FFT
        self.qtgui_freq_sink = qtgui.freq_sink_c(
            512, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "FM Spectrum", #name
            1 #number of inputs
        )
        self.qtgui_freq_sink.set_update_time(0.10)
        self.qtgui_freq_sink.set_y_axis(-140, 10)
        self.qtgui_freq_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink.enable_autoscale(False)
        self.qtgui_freq_sink.enable_grid(True)
        self.qtgui_freq_sink.set_fft_average(1.0)
        if complex == type(float()):
          self.qtgui_freq_sink.set_plot_pos_half(not True)
        self._qtgui_freq_sink_win = sip.wrapinstance(self.qtgui_freq_sink.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_win)

        #Stereo indicator
        self.qtgui_number_sink = qtgui.number_sink(gr.sizeof_char, 0,
                qtgui.NUM_GRAPH_NONE, 1)
        self.qtgui_number_sink.set_update_time(0.10)
        self.qtgui_number_sink.set_title("Stereo")
        self.qtgui_number_sink.set_min(0, 0)
        self.qtgui_number_sink.set_max(0, 1)
        self.qtgui_number_sink.enable_autoscale(False)
        self._qtgui_number_sink_win = sip.wrapinstance(self.qtgui_number_sink.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_number_sink_win)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.source, 0), (self.channel_xlating_filter, 0))
        self.connect((self.channel_xlating_filter, 0), (self.rational_resampler, 0))
        self.connect((self.rational_resampler, 0), (self.fm_receiver, 0))
        self.connect((self.fm_receiver, 0), (self.rds_sync, 0))
        self.msg_connect(self.rds_sync, 'Group', self.rds_dec, 'Group')
        self.connect((self.fm_receiver, 1), (self.qtgui_number_sink, 0))
        self.connect((self.fm_receiver, 2), (self.audio_sink, 1))
        self.connect((self.fm_receiver, 3), (self.audio_sink, 0))

        ##################################################
        # GUI connections
        ##################################################
        self.connect((self.channel_xlating_filter, 0), (self.qtgui_freq_sink, 0))

    def get_tuner(self):
        return self.tuner

    def set_tuner(self, tuner):
        self.tuner = tuner
        self.source.set_center_freq(self.tuner-self.freq_offset, 0)
        Qt.QMetaObject.invokeMethod(self.tuner_counter, "setValue", Qt.Q_ARG("double", self.tuner))
        Qt.QMetaObject.invokeMethod(self.tuner_slider, "setValue", Qt.Q_ARG("double", self.tuner))
        self.rds_dec.reset_attr();

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.source.set_sample_rate(self.samp_rate)
        self.channel_xlating_filter.set_taps((firdes.low_pass(1, self.samp_rate, 100e3, 100e3)))
        self.fm_receiver.set_samp_rate(self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.gain_callback(self.gain)
        self.source.set_gain(self.gain, 0)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.qtgui_time_sink_x_1.set_samp_rate(self.audio_rate)
        self.fm_receiver.set_audio_rate(self.audio_rate)

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def register_rds_handlers(self):
        handlers = rds_handlers.rds_handlers();
        #synchronizer
        self.rds_sync.sync_event.add_handler(handlers.log_sync);
        #decoder
        self.rds_dec.ps_name_event.add_handler(handlers.print_ps_name);
        self.rds_dec.rt_event.add_handler(handlers.print_radiotext);
        #self.rds_dec.af_event.add_handler(handlers.print_af);
        self.rds_dec.date_event.add_handler(handlers.print_date);
        #self.rds_dec.eon_change_event.add_handler(handlers.print_eon_info);

if __name__ == "__main__":
    helpstring='fm.py -c (rtlsdr|usrp) -s sample rate';

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hc:s:",["card=", "samp_rate="]);
    except getopt.GetoptError:
        print helpstring;
        sys.exit(2);

    for opt, arg in opts:
        if opt == '-h':
            print helpstring;
            sys.exit();
        elif opt in ("-c", "--card"):
            card = arg;
        elif opt in ("-s", "--samp_rate"):
            samp_rate = arg;

    qapp = Qt.QApplication(sys.argv)

    receiver=radio(98.2e6, 29.7, card, int(samp_rate));

    receiver.start();
    receiver.show();

    def quitting():
        receiver.stop();
        receiver.wait();

    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    receiver = None #to clean up Qt widgets
