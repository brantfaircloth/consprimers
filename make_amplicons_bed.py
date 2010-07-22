#!/usr/bin/env python
# encoding: utf-8

"""
make_amplicons_bed.py

Created by Brant Faircloth on 21 July 2010 12:17 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

Take a BED file input for upper and lower primers and return
BED file output giving their amplicon.
"""

import pdb
import os
import sys
import optparse


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--input', dest = 'input', action='store', 
type='string', default = None, help='The path to the primers input file.', 
metavar='FILE')

    p.add_option('--output', dest = 'output', action='store', 
type='string', default = None, help='The path to the amplicon output file.', 
metavar='FILE')

    (options,arg) = p.parse_args()
    if not options.input:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.input):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg 

def main():
    options, args = interface()
    infile = open(options.input, 'rU')
    outfile = open(options.output, 'w')
    # skip infile header
    infile.readline()
    # write outfile header
    outfile.write('''track name=cons_amplicons description="Conserved ''' 
        '''region primer amplicons" itemRgb=1 useScore=0\n''')
    while infile:
        line1 = infile.readline()
        line2 = infile.readline()
        if not line2: break
        line1 = line1.split(' ')
        line2 = line2.split(' ')
        # ensure we have the same primer
        assert line1[3].split('_')[0] == line2[3].split('_')[0], "Primers !="
        #pdb.set_trace()
        name = line1[3].split('_')[0]
        # ensure the start is less than the end
        assert int(line1[1]) < int(line2[2]), "Start-end mismatch"
        outfile.write('{0} {1} {2} {3} 1000 + {1} {2} 34,139,34\n'.format(
            line1[0], line1[1], line2[2], name))
    outfile.close()
    infile.close()


if __name__ == '__main__':
    main()