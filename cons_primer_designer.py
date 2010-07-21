#!/usr/bin/env python
# encoding: utf-8

"""
cons_primer_designer.py

Created by Brant Faircloth on 08 July 2010 14:41 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

PURPOSE:  to design primers for adjacent/somewhat adjacent conserved loci
in the bird (chicken :: zebra finch) genome

"""

import pdb
import os
import sys
import oursql
import optparse
import ConfigParser
import bx.seq.twobit
import p3wrapr


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--configuration', dest = 'conf', action='store', 
type='string', default = None, help='The path to the configuration file.', 
metavar='FILE')

    p.add_option('--chicken', dest = 'chicken', action='store_true', default=False, 
help='Include chicken sequence reads')

    (options,arg) = p.parse_args()
    if not options.conf:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.conf):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg 


def get_adjacent_loci(cur):
    cur.execute('''select id, close_target, close_target_distance as 
        target_amplicon, close_query, close_query_distance as query_amplicon 
        from distance where (close_target_distance >= 200 and 
        close_target_distance <= 5000) and (close_query_distance >= 200 and 
        close_query_distance <= 5000) and close_target = close_query''')
    data = cur.fetchall()
    return data

def create_primers_table(cur):
    try:
        cur.execute('''DROP TABLE primers''')
    except:
        pass
    cur.execute('''CREATE TABLE primers (
        distance_id int(10) UNSIGNED NOT NULL,
        distance_close_target int(10) UNSIGNED NOT NULL,
        primer int(4) UNSIGNED NOT NULL,
        left_p varchar(100) NOT NULL,
        left_sequence varchar(100) NOT NULL,
        left_tm float,
        left_gc float,
        left_self_end float,
        left_self_any float,
        left_hairpin float,
        left_end_stability float,
        left_penalty float,
        right_p varchar(100) NOT NULL,
        right_sequence varchar(100) NOT NULL,
        right_tm float,
        right_gc float,
        right_self_end float,
        right_self_any float,
        right_hairpin float,
        right_end_stability float,
        right_penalty float,
        pair_product_size float,
        pair_compl_end float,
        pair_compl_any float,
        pair_penalty float
        ) ENGINE=InnoDB''')

def insert_primers(cur, iden, ct, primer3):
    for i,p in primer3.primers.iteritems():
        if i != 'metadata':
            # create a copy of the dict, to which we add the
            # FOREIGN KEY reference
            td = p.copy()
            td['IDEN'] = iden
            td['CT'] = ct
            td['PRIMER'] = i
            cur.execute('''INSERT INTO primers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                td['IDEN'],
                td['CT'],
                td['PRIMER'],
                td['PRIMER_LEFT'],
                td['PRIMER_LEFT_SEQUENCE'],
                td['PRIMER_LEFT_TM'],
                td['PRIMER_LEFT_GC_PERCENT'],
                td['PRIMER_LEFT_SELF_END_TH'],
                td['PRIMER_LEFT_SELF_ANY_TH'],
                td['PRIMER_LEFT_HAIRPIN_TH'],
                td['PRIMER_LEFT_END_STABILITY'],
                td['PRIMER_LEFT_PENALTY'],
                td['PRIMER_RIGHT'],
                td['PRIMER_RIGHT_SEQUENCE'],
                td['PRIMER_RIGHT_TM'],
                td['PRIMER_RIGHT_GC_PERCENT'],
                td['PRIMER_RIGHT_SELF_END_TH'],
                td['PRIMER_RIGHT_SELF_ANY_TH'],
                td['PRIMER_RIGHT_HAIRPIN_TH'],
                td['PRIMER_RIGHT_END_STABILITY'],
                td['PRIMER_RIGHT_PENALTY'],
                td['PRIMER_PAIR_PRODUCT_SIZE'],
                td['PRIMER_PAIR_COMPL_END_TH'],
                td['PRIMER_PAIR_COMPL_ANY_TH'],
                td['PRIMER_PAIR_PENALTY']))

def main():
    conf = ConfigParser.ConfigParser()
    options, arg = interface()
    conf.read(options.conf)
    conn = oursql.connect(
        user=conf.get('Database','USER'), 
        passwd=conf.get('Database','PASSWORD'), 
        db=conf.get('Database','DATABASE')
    )
    cur = conn.cursor()
    data = get_adjacent_loci(cur)
    genome_path = '/Volumes/Data/Genomes/taeGut1/taeGut1.2bit'
    twobit      = bx.seq.twobit.TwoBitFile(file(genome_path))
    #pdb.set_trace()
    settings = p3wrapr.primer.Settings()
    settings.basic()
    # ensure that we get pretty different primers for each set of X designed
    # => offset by 10 bp.  this makes primer3 somewhat slower.
    settings.params['PRIMER_MIN_THREE_PRIME_DISTANCE'] = 10
    # override the default location for the mispriming library
    settings.params['PRIMER_MISPRIMING_LIBRARY'] = '/Users/bcf/Bin/misprime_lib_weight'
    # up the Tm to keep primers specific
    settings.params['PRIMER_OPT_TM'] = 65.0
    settings.params['PRIMER_MIN_TM'] = 63.0
    settings.params['PRIMER_MAX_TM'] = 68.0
    # keep the lengths relatively long => strict
    settings.params['PRIMER_OPT_SIZE'] = 21
    settings.params['PRIMER_MIN_SIZE'] = 19
    settings.params['PRIMER_MAX_SIZE'] = 24
    settings.params['PRIMER_PRODUCT_SIZE_RANGE'] = '150-5000'
    #pdb.set_trace()
    create_primers_table(cur)
    for locus in data:
        iden, ct, ctd, cq, cqd = locus
        #pdb.set_trace()
        # get the reduced cons record for each sequence
        cur.execute('''SELECT id, target_spp, target_chromo, target_cons_start, target_cons_end, 
        target_strand, query_chromo, query_cons_start, query_cons_end, query_strand, cons FROM cons 
        WHERE id in (?, ?) ORDER BY target_end''', (iden, ct))
        rows = cur.fetchall()
        # ensure we are working on the same chromo
        assert rows[0][2] == rows[1][2]
        # get the chromo and the start of the first conserved
        # region and the end of the second conserved region
        # these should be sorted which fixes the problem where
        # stop < start
        assert rows[0][3] < rows[1][4]
        t_chromo = rows[0][2][0].capitalize() + rows[0][2][1:]
        t_5_begin, t_5_end, t_3_begin, t_3_end = rows[0][3]-1, \
            rows[0][4], rows[1][3]-1,rows[1][4]
        # snip the sequence of interest from the genome
        seq = twobit[t_chromo][t_5_begin:t_3_end]
        target_start = t_5_end - t_5_begin
        target_end = t_3_end - t_3_begin
        pcr_target = '{0},{1}'.format(target_start, (len(seq) - target_end) - target_start)
        #pdb.set_trace()
        primer3 = p3wrapr.Primers()
        primer3.pick(settings, sequence = seq, target=pcr_target, name = 'primers')
        #pdb.set_trace()
        insert_primers(cur, iden, ct, primer3)
    cur.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()