#!/usr/bin/env python
# encoding: utf-8
"""
birdconsBedFormatter.py

Created by Brant Faircloth on 2009-10-30.
Copyright (c) 2009 Brant Faircloth. All rights reserved.
"""

import os
import pdb
import sys
import MySQLdb
import optparse
import ConfigParser

def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--configuration', dest = 'conf', action='store', 
type='string', default = None, help='The path to the configuration file.', 
metavar='FILE')

    p.add_option('--cons-min', dest = 'min', action='store', 
type='int', default = None, help='The min cons size to plot')

    p.add_option('--cons-max', dest = 'max', action='store', 
type='int', default = None, help='The max cons size to plot')

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
    conn = MySQLdb.connect(
        user=conf.get('Database','USER'), 
        passwd=conf.get('Database','PASSWORD'), 
        db=conf.get('Database','DATABASE')
    )
    cur = conn.cursor()
    target_file = open('taeGut1.conserved.{0}-{1}.bed'.format(options.min, options.max), 'w')
    query_file = open('galGal3.conserved.{0}-{1}.bed'.format(options.min, options.max), 'w')
    target_file.write('''track name=birdcons_taeGut1 description="taeGut1 ''' 
        '''conserved regions within {0}-{1}"\n'''.format(options.min, options.max))
    query_file.write('''track name=birdcons_galGal3 description="galgal3 '''
        '''conserved regions within {0}-{1}"\n'''.format(options.min, options.max))
    query = '''SELECT id, close_target, close_query FROM distance WHERE
        close_target_distance between {0} AND {1} 
        AND close_query_distance between {0} AND {1} 
        AND close_target = close_query'''.format(options.min, options.max)
    cur.execute(query)
    data = cur.fetchall()
    #pdb.set_trace()
    for d in data:
        iden, target_id, query = d
        # get params for iden
        cur.execute('''SELECT target_chromo, target_cons_start, 
            target_cons_end, query_chromo, query_cons_start, query_cons_end 
            FROM cons WHERE id = %s''', (iden,))
        iden_row = cur.fetchall()[0]
        iden_target = iden_row[0:3]
        iden_query  = iden_row[3:]
        cur.execute('''SELECT target_chromo, target_cons_start, 
            target_cons_end FROM cons WHERE id = %s''', (target_id,))
        target = cur.fetchall()[0]
        cur.execute('''SELECT query_chromo, query_cons_start, 
            query_cons_end FROM cons WHERE id = %s''', (query,))
        query = cur.fetchall()[0]
        # write to outfiles
        target_file.write('{0} {1} {2} {3}\n'.format(iden_target[0], iden_target[1], iden_target[2], iden))
        target_file.write('{0} {1} {2} {3}\n'.format(target[0], target[1], target[2], target_id))
        query_file.write('{0} {1} {2} {3}\n'.format(iden_query[0], iden_query[1], iden_query[2], iden))
        query_file.write('{0} {1} {2} {3}\n'.format(query[0], query[1], query[2], target_id))
    target_file.close()
    query_file.close()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()

