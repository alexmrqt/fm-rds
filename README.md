# fm-rds
A stereophonic FM broadcasting receiver and RDS (Radio Data System) decoder.

Several python script for the radio demodulation and the RDS protocol decoding are provided.
For studying purpose, we also provide GRC flowgraphs of the radio demodulator.

## Listening to a local station

Download and extract the archive rds.tar.gz

tar -xvzf rds.tar.gz

Open the extracted folder and execute the program

`cd rds`

`./fm.py -c <card> -s <sample_rate>`


Where :

* `card` is the kind of card you are usingn : ursp for NI/Ettus USRP, rtlsdr for dongles based on the RTL2832u ;
* `sample_rate` is the sample rate at which you want your SDR receiver to operate.

## Opening the flowgraphs in gnuradio-companion
The flowgraphs are located in the radio/grc folder. It contains four files :

* `radio.grc`: the main flowgraph performing the audio and RDS demodulation (needs `fm_receiver.grc` to be built) ;
* `fm_receiver.grc`: FM demodulate the incoming signal, yielding the multiplex containing audio channels L+R (Left plus Right), L-R and the RDS digital channel.
* `mpx_demod.grc`: separates the L+R (Left plus Right), L-R and RDS channels of the MPX multiplex (needs `fm_audio_demod` and `rds_demod` to be built) ;
* `fm_audio_demod.grc`: produces the stereo audio output ;
* `rds_demod.grc`: produces the raw RDS bits output (in this file, you have to change the `prefix` variable to the complete path of `fm-rds/radio/grc`.
