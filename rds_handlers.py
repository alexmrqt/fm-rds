#!/usr/bin/env python
import datetime

class rds_handlers():
#Synchronizer event handlers
    def log_sync(self,sync_state):
        if sync_state:
            print "***SYNCED***"
        else:
            print "***LOST SYNC***"

#Decoder event handlers
    def print_ps_name(self,rds_decoder):
        print "Station: ",
        print ''.join(rds_decoder.ps_name);

    def print_radiotext(self,rds_decoder):
        print "Radiotext: ",
        print ''.join(rds_decoder.rt);

    def print_af(self,rds_decoder):
        print "Alternative frequencies:"
        af_list=list(rds_decoder.af_list);
        af_list.sort();
        for af in af_list:
            print '-',;
            if(af > 1e3):
                print af/1e3,;
                print 'MHz';
            else:
                print af,;
                print 'kHz';
        print "\n";

    def print_date(self,rds_decoder):
        print "Date: ",
        print rds_decoder.clocktime.strftime("%d/%m/%Y %H:%M %z");

    def print_eon_info(self,rds_decoder):
        print "Information on network ",
        print rds_decoder.pi,
        print " received\n"
        print "(EON) Station: ",
        print rds_decoder.ondict[rds_decoder.pi].ps_name;
        print "(EON) Alternative frequencies (kHz): ",
        for af in rds_decoder.ondict[rds_decoder.pi].af_list:
            print af,;
            print ", ";
        print "\n";
