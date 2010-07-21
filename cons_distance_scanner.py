#!/usr/bin/env python
# encoding: utf-8
"""
consDistanceScanner.py

Created by Brant Faircloth on 2009-10-30.
Copyright (c) 2009 Brant Faircloth. All rights reserved.

"""

import pdb
import MySQLdb
import ConfigParser

def insertDistanceData(cur, id, prev_id, distance, target=True):
    if target:
        cur.execute('''INSERT INTO distance (id, close_target, close_target_distance) 
        VALUES (%s, %s, %s)''', (id, prev_id, distance))
    else:
        cur.execute('''UPDATE distance set close_query = %s, close_query_distance = %s WHERE id = %s''', (prev_id, distance, id))

def makeDuplicate(cur, id, val):
    cur.execute('''UPDATE cons SET duplicate = %s WHERE id = %s''', (val, id,))

def getDistance(cur, chromo, target=True):
    #pdb.set_trace()
    if target:
        cur.execute('''SELECT id, target_cons_start, target_cons_end FROM cons 
        WHERE target_chromo = %s ORDER BY target_cons_start''', (chromo))
    else:
        cur.execute('''SELECT id, query_cons_start, query_cons_end FROM cons 
        WHERE query_chromo = %s ORDER BY query_cons_start''', (chromo))
    chromo_results = cur.fetchall()
    for i in xrange(len(chromo_results)):
        if i == 0:
            # just set the record to null
            insertDistanceData(cur, chromo_results[i][0], None, None)
        else:
            this_start      = chromo_results[i][1]
            previous_end    = chromo_results[i-1][2]
            distance = this_start - previous_end
            insertDistanceData(cur, chromo_results[i][0], chromo_results[i-1][0], distance, target)
            if distance <= 0:
                makeDuplicate(cur, chromo_results[i][0], 1)
            else:
                makeDuplicate(cur, chromo_results[i][0], 0)


def createDistanceTable(cur):
    '''create a table to hold the results'''
    try:
        # if previous tables exist, drop them
        # TODO: fix createDbase() to drop tables safely
        cur.execute('''DROP TABLE distance''')
    except:
        pass
    try:
        cur.execute('''UPDATE cons SET duplicate = NULL''')
    except:
        pass
    # create the distance results table
    cur.execute('''CREATE TABLE distance (
    id MEDIUMINT UNSIGNED NOT NULL,
    close_target MEDIUMINT UNSIGNED,
    close_target_distance MEDIUMINT,
    close_query MEDIUMINT UNSIGNED,
    close_query_distance MEDIUMINT,
    FOREIGN KEY (id) REFERENCES cons (id),
    INDEX cons_close_target_dist (close_target_distance),
    INDEX cons_close_query_dist (close_query_distance)
    ) ENGINE=InnoDB
    ''')

def main():
    conf = ConfigParser.ConfigParser()
    conf.read('db.conf')
    conn = MySQLdb.connect(user=conf.get('Database','USER'), 
        passwd=conf.get('Database','PASSWORD'), 
        db=conf.get('Database','DATABASE'))
    cur = conn.cursor()
    createDistanceTable(cur)
    cur.execute('''select distinct target_chromo from cons''')
    results = cur.fetchall()
    for r in results:
        getDistance(cur, r)
    cur.execute('''select distinct query_chromo from cons''')
    for r in results:
        getDistance(cur, r, target=False)
    conn.commit()

if __name__ == '__main__':
    main()