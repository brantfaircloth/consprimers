#!/usr/bin/env python
# encoding: utf-8

"""
make_primer_bed.py

Created by Brant Faircloth on 08 July 2010 17:38 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.
"""

import pdb
import os
import sys
import oursql
import optparse
import ConfigParser


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--configuration', dest = 'conf', action='store', 
type='string', default = None, help='The path to the configuration file.', 
metavar='FILE')

    p.add_option('--output', dest = 'output', action='store', 
type='string', default = None, help='The path to the output file.', 
metavar='FILE')

    p.add_option('--chicken', dest = 'chicken', action='store_true', 
default=False, help='Map to chicken sequence reads')

    (options,arg) = p.parse_args()
    if not options.conf:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.conf):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg 


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
    cur.execute('''SELECT distance_id, distance_close_target, left_p, right_p 
        from primers where primer = 0''')
    data = cur.fetchall()
    #pdb.set_trace()
    outp = open(options.output, 'w')
    outp.write('''track name=consPrimers description="Primers" itemRgb=1 useScore=0\n''')
    for d in data:
        iden, ct, lp, rp = d
        # get the positions of each locus and find the smallest start pos
        # we need to do this relative to zebra finch and then transform it to
        # chicken
        cur.execute('''SELECT id, target_chromo, target_cons_start, target_cons_end 
            FROM cons WHERE id in (?, ?) ORDER BY target_cons_end''', (iden, ct))
        #pdb.set_trace()
        positions = cur.fetchall()
        start   = sorted([positions[0][2],  positions[1][2]])[0]
        end     = sorted([positions[0][3],  positions[1][3]])[1]
        #pdb.set_trace()
        d_pos = sorted([d[0], d[1]])
        upper_name = '{0}-{1}_upper'.format(d_pos[0], d_pos[1])
        lower_name = '{0}-{1}_lower'.format(d_pos[0], d_pos[1])
        #upper_name = '{0}_upper'.format(positions[0][0])
        #lower_name = '{0}_lower'.format(positions[0][0])
        # determine the actual position of the primer
        #pdb.set_trace()
        rp_start_temp = (start + int(rp.split(',')[0])) - end
        rp_end_temp = rp_start_temp - int(rp.split(',')[1])
        if not options.chicken:
            chromo      = positions[0][1]
            lp_start    = start + int(lp.split(',')[0])
            lp_end      = lp_start + int(lp.split(',')[1])
            rp_end      = end + (rp_start_temp)
            rp_start    = end + (rp_end_temp)
        if options.chicken:
            cur.execute('''SELECT id, query_chromo, query_cons_start, query_cons_end 
                FROM cons WHERE id in (?, ?) ORDER BY query_cons_end''', (iden, ct))
            positions   = cur.fetchall()
            chromo      = positions[0][1]
            start       = sorted([positions[0][2],  positions[1][2]])[0]
            end         = sorted([positions[0][3],  positions[1][3]])[1]
            lp_start    = start + int(lp.split(',')[0]) - 1
            lp_end      = lp_start + int(lp.split(',')[1])
            rp_end      = end + (rp_start_temp)
            rp_start    = end + (rp_end_temp)
        outp.write('{0} {1} {2} {3} 1000 + {1} {2} 255,0,0\n'.format(chromo, 
            lp_start, lp_end, upper_name))
        outp.write('{0} {1} {2} {3} 1000 - {1} {2} 0,0,255\n'.format(chromo, 
            rp_start, rp_end, lower_name))
    outp.close()
    conn.close()
    
if __name__ == '__main__':
    main()