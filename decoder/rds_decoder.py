#!/usr/bin/env python

import pmt
import rds_constants
import tmc_events
from event_handler import event
from gnuradio import gr
import datetime

class rds_decoder(gr.sync_block):
    def __init__(self):
        #Parent constructor
        gr.sync_block.__init__(self, name="RDS decoder", in_sig=None, out_sig=None);

        #Register message ports
        self.message_port_register_in(pmt.intern('Group'));
        self.set_msg_handler(pmt.intern('Group'), self.decode_group);

        #Attributes and events definitions
        self.reset_attr();

        #Event definition
        self.af_event = event();
        self.af_nb_af_to_follow_event = event();
        self.pty_event = event();
        self.pi_event = event();
        self.rt_event = event();
        self.ps_name_event = event();
        self.di_event = event();
        self.paging_opc_event = event();
        self.paging_id_event = event();
        self.paging_code_event = event();
        self.broadcasters_codes_event = event();
        self.ews_id_event = event();
        self.ews_id_event = event();
        self.ews_id_event = event();
        self.na1_event = event();
        self.na2_event = event();
        self.language_code_event = event();
        self.tmc_id_event = event();
        self.ecc_event = event();
        self.pin_event = event();
        self.paging_opc_event = event();
        self.paging_id_event = event();
        self.paging_code_event = event();
        self.oda_application_group_type_code_event = event();
        self.oda_message_event = event();
        self.oda_aid_event = event();
        self.date_event = event();
        self.eon_new_event = event();     #Event fired with PI(ON)
        self.eon_change_event = event();  #Event fired with PI(ON)
        self.tp_event = event();
        self.ta_event = event();
        self.ms_event = event();

    def reset_attr(self):
        #Attributes definitions
        #Alternative Frequencies (AF)
        self.af_list = [];
        self.af_lfmf = False;
        self.nb_af_to_follow = 0;

        #Program Type (PTY)
        self.pty = 0
        self.static_pty_flag = False;

        #Program Information (PI)
        self.pi = 0;
        self.pi_country_identification = 0;
        self.pi_area_coverage = 0;
        self.pi_program_reference_number = 0;

        #RadioText (RT)
        self.rt = [' '] * 64;
        self.rt_ab_flag = False;

        #Program Service name (PS)
        self.ps_name = [' '] * 8;

        #Decoder Identification (DI)
        self.di = 0;
        self.mono_stereo_flag = False;
        self.artificial_head_flag = False;
        self.compressed_flag = False;

        #Paging
        self.paging_codes = 0;
        self.paging_opc = 0;
        self.paging_id = 0;

        #Program Item Number (PIN)
        self.pin_day = 0;
        self.pin_hour = 0;
        self.pin_minute = 0;

        ##Slow labelling codes
        #Extended Country Code (ECC)
        self.ecc = 0;
        #Traffic Message Channel (TMC)
        self.tmc_id = 0;
        #Language code
        self.language_code = 0;
        #Not assignated
        self.na1 = 0;
        self.na2 = 0;
        #For use by broadcasters
        self.broadcasters_codes = 0;
        #Emergency Warning Systems (EWS)
        self.ews_id = 0;

        #Open Data Application
        self.oda_application_group_type_code = 0;
        self.oda_message = 0;
        self.oda_aid = 0;

        #ClockTime (CT)
        self.clocktime = None;

        #Enhanced Other Networks information (EON)
        self.on_dict = {};  #Key: PI(ON), Value: eon object

        #Traffic Program (TP)
        self.tp_flag = False;
        #Traffic Announcement (TA)
        self.ta_flag = False;
        #Music/Speech
        self.ms_flag = False;

    def decode_group(self, group_pmt):
        group=pmt.to_python(group_pmt);
        group_type = ((group[1] >> 12) & 0xf);
        ab = (group[1] >> 11 ) & 0x1;

        #PI
        pi = group[0];
        if(pi != self.pi):
            self.pi = pi;
            self.pi_country_identification = (self.pi >> 12) & 0xf;
            self.pi_area_coverage = (self.pi >> 8) & 0xf;
            self.pi_program_reference_number = self.pi & 0xff;
            #Fire event
            self.pi_event.fire(self);

        #PTY
        pty = (group[1] >> 5) & 0x1f;
        if(pty != self.pty):
            self.pty = pty;
            #Fire event
            self.pty_event.fire(self);

        #TP
        tp_flag = (group[1] >> 10) & 0x01;
        if(tp_flag != self.tp_flag):
            self.tp_flag = tp_flag;
            #Fire event
            self.tp_event.fire(self);

        #Specific decoding depending on group type
        if(group_type == 0):
            self.decode_type0(group, ab);
        elif(group_type == 1):
            self.decode_type1(group, ab);
        elif(group_type == 2):
            self.decode_type2(group, ab);
        elif(group_type == 3):
            self.decode_type3(group, ab);
        elif(group_type == 4):
            self.decode_type4(group, ab);
        elif(group_type == 5):
            self.decode_type5(group, ab);
        elif(group_type == 6):
            self.decode_type6(group, ab);
        elif(group_type == 7):
            self.decode_type7(group, ab);
        elif(group_type == 8):
            self.decode_type8(group, ab);
        elif(group_type == 9):
            self.decode_type9(group, ab);
        elif(group_type == 10):
            self.decode_type10(group, ab);
        elif(group_type == 11):
            self.decode_type11(group, ab);
        elif(group_type == 12):
            self.decode_type12(group, ab);
        elif(group_type == 13):
            self.decode_type13(group, ab);
        elif(group_type == 14):
            self.decode_type14(group, ab);
        elif(group_type == 15):
            self.decode_type15(group, ab);

    def decode_type0(self, group, B):
        af_code_1 = 0;
        af_code_2 = 0;
        no_af = 0;
        af_1 = 0;
        af_2 = 0;
        ps_name = list(self.ps_name);

        #TA
        ta_flag = (group[1] >>  4) & 0x01;
        if (ta_flag != self.ta_flag):
            self.ta_flag = ta_flag;
            #Fire event
            self.ta_event.fire(self);

        #MS
        ms_flag = (group[1] >>  3) & 0x01;
        if (ms_flag != self.ms_flag):
            self.ms_flag = ms_flag;
            #Fire event
            self.ms_event.fire(self);

        #DI
        di = (group[1] >> 2) & 0x01;
        segment_address = group[1] & 0x03; #DI segment
        if(di != self.di):
            # see page 41, table 9 of the standard
            if(segment_address==0):
                self.mono_stereo_flag=di;
            elif(segment_address==1):
                self.artificial_head_flag=di;
            elif(segment_address==2):
                self.compressed_flag=di;
            elif(segment_address==3):
                self.static_pty_flag=di;
            #Fire event
            self.di_event.fire(self);

        ps_name[segment_address * 2]     = chr((group[3] >> 8) & 0xff);
        ps_name[segment_address * 2 + 1] = chr(group[3] & 0xff);
        if(ps_name != self.ps_name):
            self.ps_name = ps_name;
            self.ps_name_event.fire(self);


        if(not B): # type 0A
            #Decode AFs
            af_1 = self.decode_af((group[2] >> 8) & 0xff);
            af_2 = self.decode_af((group[2]) & 0xff);
            af = False;

            #If new AFs found, add to AF list
            if((af_1 != 0) and (af_1 not in self.af_list)):
                self.af_list.append(af_1);
                af = True;

            if((af_2 != 0) and (af_2 not in self.af_list)):
                self.af_list.append(af_2);
                af = True;

            #If new AFs found, fire event
            if(af):
                self.af_event.fire(self);

    def decode_af(self, af_code):
        alt_frequency = 0; # in kHz

        if((af_code == 0) or                    # not to be used
            (af_code == 205) or                 # filler code
            (af_code in range(206, 224)) or     # not assigned
            (af_code == 224) or                 # No AF exists
            (af_code in range(251, 256))):       # not assigned
                return 0;

        if(af_code in range(225, 250)): # VHF frequencies follow
            self.af_lfmf = False;
            self.nb_af_to_follow = af_code - 224;
            self.af_nb_af_to_follow_event.fire();
            return 0;

        if(af_code == 250):             # One LF/MF frequency follows
            self.af_lfmf = True;
            self.nb_af_to_follow = 1;
            self.af_nb_af_to_follow_event.fire();
            return 0;

        if(self.af_lfmf):
            if(af_code in range(1, 16)):       # LF (153-279kHz)
                alt_frequency = 153 + (af_code - 1) * 9;
            elif(af_code in range(16, 136)):   # MF (531-1602kHz)
                alt_frequency = 531 + (af_code - 16) * 9;
            else:
                return 0;
        else:                                  # VHF (87.6-107.9MHz)
            if(af_code in range(1, 206)):
                alt_frequency = 1000 * (af_code*0.1 + 87.5);
            else:
                return 0;

        return alt_frequency;

    def decode_type1(self, group, B):
        ecc = 0;
        paging = 0;
        country_code = (group[0] >> 12) & 0x0f;

        self.paging_codes =  group[1] & 0x1f;
        #Fire event
        if (self.paging_codes):
            self.paging_code_event.fire(self);

        variant_code = (group[2] >> 12) & 0x7;
        slow_labelling = group[2] & 0xfff;

        day = (group[3] >> 11) & 0x1f;
        hour = (group[3] >>  6) & 0x1f;
        minute = group[3] & 0x3f;

        if(day or hour or minute):
            self.pin_day = day;
            self.pin_hour = hour;
            self.pin_minute = minute;
            #Fire event
            self.pin_event.fire(self);

        if(variant_code==0): # paging + ecc
            paging_opc = (slow_labelling >> 8) & 0x0f;
            ecc = slow_labelling & 0xff;

            if(self.paging_opc != paging_opc):
                self.paging_opc = paging_opc;
                #Fire event
                self.paging_opc_event.fire(self);
            if(self.ecc != ecc):
                self.ecc= ecc;
                #Fire event
                self.ecc_event.fire(self);

        elif(variant_code==1): #TMC identification
            if(self.tmc_id != slow_labelling):
                self.tmc = slow_labelling;
                #Fire event
                self.tmc_id_event.fire(self);

        elif(variant_code==2): #Paging identification
            if(self.paging_id != slow_labelling):
                self.paging_id = slow_labelling;
                #Fire event
                self.paging_id_event.fire(self);

        elif(variant_code==3): #Language codes
            if(self.language_code != slow_labelling):
                self.language_code = slow_labelling;
                #Fire event
                self.language_code_event.fire(self);

        elif(variant_code==4): #Not assignated (1)
            if(self.na1 != slow_labelling):
                self.na1 = slow_labelling;
                #Fire event
                self.na1_event.fire(self);

        elif(variant_code==5): #Not assignated (2)
            if(self.na2 != slow_labelling):
                self.na2 = slow_labelling;
                #Fire event
                self.na2_event.fire(self);

        elif(variant_code==6): #For use by broadcasters
            if(self.broadcasters_codes != slow_labelling):
                self.broadcasters_codes= slow_labelling;
                #Fire event
                self.broadcasters_codes_event.fire(self);

        elif(variant_code==7): #EWS
            if(self.ews_id != slow_labelling):
                self.ews_id= slow_labelling;
                #Fire event
                self.ews_id_event.fire(self);

    def decode_type2(self, group, B): #RadioText
        text_segment_address_code = group[1] & 0x0f;
        rt = list(self.rt);

        # when the A/B flag is toggled, flush your current rt
        if(self.rt_ab_flag != ((group[1] >> 4) & 0x01)):
            for i in range(0, 64):
                self.rt[i] = ' ';

        self.rt_ab_flag = (group[1] >> 4) & 0x01;

        if(not B):
            rt[text_segment_address_code *4     ] = chr((group[2] >> 8) & 0xff);
            rt[text_segment_address_code * 4 + 1] = chr(group[2] & 0xff);
            rt[text_segment_address_code * 4 + 2] = chr((group[3] >> 8) & 0xff);
            rt[text_segment_address_code * 4 + 3] = chr(group[3] & 0xff);
        else:
            rt[text_segment_address_code * 2    ] = chr((group[3] >> 8) & 0xff);
            rt[text_segment_address_code * 2 + 1] = chr(group[3] & 0xff);

        if(rt != self.rt):
            self.rt=rt;
            self.rt_event.fire(self);

    def decode_type3(self, group, B):
        if(B):  #ODA
            return;

        if(self.oda_application_group_type_code != group[1]):
            self.oda_application_group_type_code = group[1];
            #Fire event
            self.oda_application_group_type_code_event.fire(self);

        if(self.oda_message != group[2]):
            self.oda_message = group[2];
            #Fire event
            self.oda_message_event.fire(self);

        if(self.oda_aid != group[3]):
            self.oda_aid = group[3];
            #Fire event
            self.oda_aid_event.fire(self);

    def decode_type4(self, group, B): #ClockTime
        if(B):  #ODA
            return;

        hour = ((group[2] & 0x1) << 4) | ((group[3] >> 12) & 0x0f);
        minute = (group[3] >> 6) & 0x3f;

        modified_julian_date = ((group[1] & 0x03) << 15) | ((group[2] >> 1) & 0x7fff);
        year = int((modified_julian_date - 15078.2) / 365.25);
        month = int((modified_julian_date - 14956.1 - (year * 365.25)) / 30.6001);
        day = modified_julian_date - 14956 - int(year * 365.25) - int(month * 30.6001);

        month -= 1;
        year += 1900;

        if ((month == 14) or (month == 15)):
            year += 1;
            month -= 12;

        time_offset_sign=1 - ((group[3]>>5)&0x1) * 2;
        time_offset=(group[3]&0x1F);
        minute_offset=time_offset_sign * 30 * time_offset;

        #Do nothing if date values are corrupted
        if((year < 1900) or (month < 1) or (month > 12) or (day < 1)
                or (day > 31) or (hour > 23) or (minute > 59) or (time_offset > 24)):
            return;

        tzinfo=ct_tz_data(minute_offset);
        self.clocktime=datetime.datetime(year, month, day, hour, minute, tzinfo=tzinfo);

        #Fire event
        self.date_event.fire(self);

    def decode_type5(self, group, B): #ODA
        return;

    def decode_type6(self, group, B): #ODA
        return;

    def decode_type7(self, group, B): #ODA
        return;

    def decode_type8(self, group, B): #ODA/TMC
        return;

    def decode_type9(self, group, B): #ODA/EWS
        return;

    def decode_type10(self, group, B): #ODA/PTYN
        return;

    def decode_type11(self, group, B): #ODA
        return;

    def decode_type12(self, group, B): #ODA
        return;

    def decode_type13(self, group, B): #ODA/Enhanced paging
        return;

    def decode_type14(self, group, B): #EON
        new_on_flag = False;
        variant_code= group[1] & 0x0f;
        information = group[2];
        pi_on       = group[3];

        #Tuned network infos
        pty_tn = (group[1] >> 5) & 0x1F;
        if (pty_tn != self.pty):
            self.pty = pty_tn;
            #Fire event
            self.pty_event.fire(self);

        tp_flag_tn = (group[1] >> 10) & 0x01;
        if (tp_flag_tn != self.tp_flag):
            self.tp_flag = tp_flag_tn;
            #Fire event
            self.tp_event.fire(self);

        #Retrieve or create eon obect
        if (pi_on in self.on_dict):
            on = self.on_dict[pi_on];
        else:
            on = eon();
            on.pi = pi_on;
            self.on_dict[pi_on] = on;
            new_on_flag = True;

        #ON TP flag
        on.tp_flag = (group[1] >> 4) & 0x01;

        if (not B):
            if (variant_code >= 0 and variant_code <= 3): # PS(ON)
                on.ps_name[variant_code * 2    ] = chr((information >> 8) & 0xff);
                on.ps_name[variant_code * 2 + 1] = chr(information       & 0xff);

            elif (variant_code == 4): # AF
                af_1 = 100.0 * (((information >> 8) & 0xff) + 875);
                af_2 = 100.0 * ((information & 0xff) + 875);
                if(af_1 not in self.af_list):
                    on.af_list.append(af_1);
                if(af_2 not in self.af_list):
                    on.af_list.append(af_2);

            elif (variant_code >= 5 and variant_code <= 8): # mapped frequencies
                af_1 = 100.0 * (((information >> 8) & 0xff) + 875);
                af_2 = 100.0 * ((information & 0xff) + 875);
                if(af_1 not in self.af_list):
                    on.af_list.append(af_1);
                if(af_2 not in self.af_list):
                    on.af_list.append(af_2);

            elif (variant_code == 9): # mapped frequencies (AM)
                af_1 = 100.0 * (((information >> 8) & 0xff) + 875);
                af_2 = (9.0 * ((information & 0xff) - 16) + 531)/1000;
                if(af_1 not in self.af_list):
                    on.af_list.append(af_1);
                if(af_2 not in self.af_list):
                    on.af_list.append(af_2);

            elif (variant_code == 10): # unallocated
                on.variant10 = information;

            elif (variant_code == 11): # unallocated
                on.variant11 = information;

            elif (variant_code == 12): # linkage information
                on.linkage_info = information;

            elif (variant_code == 13): # PTY(ON), TA(ON)
                on.ta_flag = information & 0x01;
                on.pty = (information >> 11) & 0x1f;

            elif (variant_code == 14): # PIN(ON)
                on.pin_day = (information >> 11) & 0x1f;
                on.pin_hour = (information >>  6) & 0x1f;
                on.pin_minute = information & 0x3f;
        else: #type B
            on.ta_flag = (group[1] >> 3) & 0x01;

    def decode_type15(self, group, B):
        return;

#EON Class
class eon(object):
    def __init__(self):
        #PI
        self.pi = 0;

        #Program Service name (PS)
        self.ps_name = [];
        for i in range(0, 8):
            self.ps_name.append(' ');

        #Alternative Frequencies (AF)
        self.af_list = [];

        #Variant 10 (unallocated)
        self.variant10 = 0;

        #Variant 11 (unallocated)
        self.variant11 = 0;

        #Linkage information
        self.linkage_info = 0;

        #PTY
        self.pty = 0;

        #TA
        self.ta_flag = False;

        #TP
        self.tp_flag = False;

        #PIN
        self.pin_day = 0;
        self.pin_hour = 0;
        self.pin_minute = 0;

        #Variant 15 (reserved for broadcasters use)
        self.variant15 = 0;

#Timezone class, to be used with datetime class for CT
class ct_tz_data(datetime.tzinfo):
    def __init__(self, minute_offset):
        self.minute_offset=minute_offset;

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.minute_offset);

    def dst(self, dt):
        return datetime.timedelta(0);
