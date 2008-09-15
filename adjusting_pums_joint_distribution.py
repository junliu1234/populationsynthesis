# This file contains a MySQL class that helps manipulate data. The instance of
# the class also stores the results of the query as a list.

import time
import MySQLdb
import os
from re import match
from numpy import asarray as arr
from numpy import fix as quo
from numpy import zeros
from ipf_mysql import *

def create_matching_string(table_name1, table_name2, control_variables):
    string = ''
    for dummy in control_variables:
        if len(string) == 0:
            string = string + table_name1 + '.' + dummy + '=' + table_name2 + '.' + dummy
        else:
            string = string + ' '+'and' + ' ' + table_name1 + '.' + dummy + '=' + table_name2 + '.' + dummy
    return string

def create_adjusted_frequencies(db, synthesis_type, control_variables, pumano, tract= 0, bg= 0):
    dbc = db.cursor()
    dummy_order_string = create_aggregation_string(control_variables)
    puma_table = ('%s_%s_joint_dist'%(synthesis_type, pumano))
    pums_table = ('%s_%s_joint_dist'%(synthesis_type, 0))

    dbc.execute('select * from %s where tract = %s and bg = %s order by %s' %(puma_table, tract, bg, dummy_order_string))
    puma_joint = arr(dbc.fetchall())
    puma_prob = puma_joint[:,-1] / sum(puma_joint[:,-1])
    upper_prob_bound = 0.5 / sum(puma_joint[:,-1])
   
    dbc.execute('select * from %s order by %s' %(pums_table, dummy_order_string))
    pums_joint = arr(dbc.fetchall())
    pums_prob = pums_joint[:,-1] / sum(pums_joint[:,-1])
    
    puma_adjustment = (pums_prob <= upper_prob_bound) * pums_prob + (pums_prob > upper_prob_bound) * upper_prob_bound
    correction = 1 - sum((puma_prob == 0) * puma_adjustment)
    puma_prob = ((puma_prob <> 0) * correction * puma_prob +
                 (puma_prob == 0) * puma_adjustment)
    puma_joint[:,-1] = sum(puma_joint[:,-1]) * puma_prob

    dbc.execute('delete from %s where tract = %s and bg = %s'%(puma_table, tract, bg))
    puma_joint_dummy = str([tuple(i) for i in puma_joint])
    dbc.execute('insert into %s values %s' %(puma_table, puma_joint_dummy[1:-1]))
    dbc.close()


if __name__ == '__main__':


    db = MySQLdb.connect(user = 'root', passwd = 'mashima', db = 'popsyntrb')
    dbc = db.cursor()

    ti = time.clock()
    dimensions = arr(create_dimensions(db, 'hhld'))
    control_variables = choose_control_variables(db, 'hhld')
# Total PUMS Sample x composite_type adjustment for hhld    
    create_joint_dist(db, 'hhld', control_variables, dimensions, 0)
# Example puma x composite_type adjustment for hhld    
    create_joint_dist(db, 'hhld', control_variables, dimensions, 101, 71504, 1)
    create_adjusted_frequencies(db, 'hhld', control_variables, 101, 71504, 1)
    adjust_weights(db, 'hhld', control_variables, 101, 71504, 1)


    dimensions = arr(create_dimensions(db, 'person'))
    control_variables = choose_control_variables(db, 'person')
# Total PUMS Sample x composite_type adjustment for person    
    create_joint_dist(db, 'person', control_variables, dimensions, 0)
# Example puma x composite_type adjustment for person
    create_joint_dist(db, 'person', control_variables, dimensions, 101, 71504, 1)
    create_adjusted_frequencies(db, 'person', control_variables, 101, 71504, 1)
    adjust_weights(db, 'person', control_variables, 101, 71504, 1)

    print 'Person IPF and Household IPF in %.4f' %(time.clock()-ti)

    dbc.close()
    db.close()
    

  

