#!/usr/bin/env python

import pmt
import numpy
from decoder import event_handler as event
from gnuradio import gr

class rds_synchronizer(gr.sync_block):
    #Class attributes
    #Parity-check matrix
    H=[
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 0],
        [0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 1, 0, 1, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 0, 0, 1, 1],
        [1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 0],
        [0, 1, 1, 0, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 0, 1, 1]];
    H=numpy.concatenate((numpy.identity(10, int), H), axis=0);
    H=numpy.matrix(H);
    # see Annex B, table B.1 in the standard
    # offset word C' has been put at the end
    offset_pos=[0,1,2,3,2];
    offset_name=["A","B","C","D","C'"];
    offset_word=[
            0b0011111100,
            0b0110011000,
            0b0101101000,
            0b0110110100,
            0b1101010000];
    syndrome=[
            0b1111011000,
            0b1111010100,
            0b1001011100,
            0b1001011000,
            0b1111001100];
    syndrome_err_patterns=dict();
    for i in range(0,22):
        for j in range(0,2**5):
            e=numpy.zeros(26, numpy.int)
            e[i]=j&0b01;
            e[i+1]=(j>>1)&0b01;
            e[i+2]=(j>>2)&0b01;
            e[i+3]=(j>>3)&0b01;
            e[i+4]=(j>>4)&0b01;
            e=numpy.matrix(e);

            s=numpy.mod(e*H,2);

            #We convert e and s to integers
            e_int=0;
            for k in range(0,26):
                e_int=(e_int<<1)|e[0,k];

            s_int=0;
            for k in range(0,10):
                s_int=(s_int<<1)|s[0,k];

            syndrome_err_patterns[s_int]=e_int;

    def __init__(self):
        #Parent constructor
        gr.sync_block.__init__(self,
            name="RDS sink",
            in_sig=[ numpy.uint8 ],
            out_sig=None);

        #Register message ports
        self.message_port_register_out(pmt.intern('Group'));

        #Attributes definitions
        self.reset_attr();

        #Events definitions
        self.sync_event=event.event(); #fire(True) if synced, fire(False) else

    def reset_attr(self):
        self.sync_bit_counter = 0;
        self.lastseen_offset_counter = 0;
        self.block_bit_counter = 0;
        self.wrong_blocks_counter = 0;
        self.blocks_counter = 0;
        self.group = [0, 0, 0, 0];
        self.presync = False;
        self.group_assembly_started = False;
        self.lastseen_offset = 0;
        self.block_number = 0;
        self.reg = 0;
        self.synced = False;

    def enter_no_sync(self):
        self.reset_attr();
        #Fire event
        self.sync_event.fire(False);

    def enter_sync(self, sync_block_number):
        self.wrong_blocks_counter = 0;
        self.blocks_counter = 0;
        self.block_bit_counter = 0;
        self.block_number = (sync_block_number + 1) % 4;
        self.group_assembly_started = 0;
        self.synced = True;
        #Fire event
        self.sync_event.fire(True);

    def aquire_sync(self):
        i=0;
        reg_syndrome=0;
        bit_distance=0;
        block_distance=0;

        reg_syndrome = self.calc_syndrome(self.reg);
        for i in range(0,5):
            if (reg_syndrome == self.syndrome[i]):
                if (self.presync == False):
                    self.lastseen_offset = i;
                    self.lastseen_offset_counter=self.sync_bit_counter;
                    self.presync=True;
                else:
                    bit_distance = self.sync_bit_counter - self.lastseen_offset_counter;
                    self.presync = False;
                    self.sync_bit_counter=0;
                    if (bit_distance%26 == 0):
                        block_distance=bit_distance/26;
                        if((block_distance < 3) and (self.offset_pos[self.lastseen_offset] < self.offset_pos[i])):
                            self.enter_sync(i);
                break; #syndrome found, no more cycles

    def calc_syndrome(self, seq):
        vec_seq=numpy.fromstring(numpy.binary_repr(seq,26), dtype=numpy.uint8)-48;
        vec_seq=numpy.matrix(vec_seq);

        syndrome=numpy.mod(vec_seq*self.H, 2);
        syndrome_int=numpy.packbits(syndrome);
        syndrome_int=(syndrome_int[0,0]<<2) + (syndrome_int[0,1]>>6);

        return syndrome_int

    def correct_errors(self, seq, block_number):
        #Remove syndrome corresponding to the offset word
        seq=seq ^ self.offset_word[block_number];

        #Compute syndrome
        syndrome=self.calc_syndrome(seq);

        #Decode
        try:
            m_dec=(seq^self.syndrome_err_patterns[syndrome])>>10;
        except KeyError as e:
            return -1;

        return m_dec;

    def work(self, input_items, output_items):
        in0=input_items[0];

        for item in in0:
            # the synchronization process is described in Annex C
            # page 66 of the standard
            dataword=0;
            #reg contains the last 26 rds bits (last block)
            self.reg=(self.reg<<1)|item;
            #Limit the size of the register to 26 bits
            self.reg=self.reg&0x3FFFFFF;

            if(self.synced == False):
                self.sync_bit_counter += 1;
                self.aquire_sync();
            else:
                self.block_bit_counter = (self.block_bit_counter + 1)%26;
                # wait until 26 bits enter the buffer
                if(self.block_bit_counter == 0):
                    #Error correction and detection
                    corrected_seq=self.correct_errors(self.reg, self.block_number);
                    if(corrected_seq != -1):
                        dataword=corrected_seq;
                    # manage special case of C or C' offset word
                    elif ((self.block_number == 2)):
                        corrected_seq=self.correct_errors(self.reg, 4);
                        if(corrected_seq != -1):
                            dataword=corrected_seq;
                        else:
                            self.wrong_blocks_counter += 1;
                    else:
                        self.wrong_blocks_counter += 1;

                    # done checking CRC
                    if (self.block_number == 0 and corrected_seq != -1):
                        self.group_assembly_started = True;

                    if (self.group_assembly_started):
                        if (corrected_seq == -1):
                            self.group_assembly_started = False;
                        else:
                            self.group[self.block_number] = dataword;
                            
                        if (self.block_number == 3):
                            self.message_port_pub(
                                pmt.intern('Group'), 
                                pmt.to_pmt(numpy.array(self.group, dtype=numpy.uint16)));

                    self.block_number = (self.block_number + 1) % 4;
                    self.blocks_counter += 1;

                    #1187.5 bps / 104 bits = 11.4 groups/sec, or 45.7 blocks/sec */
                    if (self.blocks_counter==50):
                        if (self.wrong_blocks_counter>25):
                            #Lost sync
                            self.enter_no_sync();

                        self.blocks_counter=0;
                        self.wrong_blocks_counter=0;

        return len(input_items[0]);
