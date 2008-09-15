# This file contains a MySQL class that helps manipulate data. The instance of
# the class also stores the results of the query as a list.

import time
import MySQLdb
from numpy import asarray as arr

def create_marginals(db, bgs):
    dbc = db.cursor()
    margs_hhld = open('marginals_hhld.txt','w')
    margs_pers = open('marginals_person.txt','w')

    for i in bgs:
        margs_hhld.write('geoid ' + str(i))
        margs_pers.write('geoid ' + str(i))
        margs_hhld.write('\n')
        margs_pers.write('\n')
        print i
        dbc.execute('select hhldtype, hhldsize, hhldinc, frequency from hhld_%s_joint_dist where tract = %s and bg = %s order by hhldtype, hhldsize, hhldinc '%(i[0], i[1], i[2]))
        result = arr(dbc.fetchall())
        print sum(result[:,-1])
        for j in result:
            
            margs_hhld.write(str(j[0].astype(int)))
            margs_hhld.write(',')
            margs_hhld.write(str(j[1].astype(int)))
            margs_hhld.write(',')
            margs_hhld.write(str(j[2].astype(int)))
            margs_hhld.write(',')
            margs_hhld.write(str(j[3]))
            margs_hhld.write('\n')

        dbc.execute('select gender, age, race, frequency from person_%s_joint_dist where tract = %s and bg = %s order by gender, age, race'%(i[0], i[1], i[2]))
        result = arr(dbc.fetchall())
        print sum(result[:,-1])        
        for j in result:
            margs_pers.write(str(j[0].astype(int)))
            margs_pers.write(',')
            margs_pers.write(str(j[1].astype(int)))
            margs_pers.write(',')
            margs_pers.write(str(j[2].astype(int)))
            margs_pers.write(',')
            margs_pers.write(str(j[3]))
            margs_pers.write('\n')
    

    margs_hhld.close()
    margs_pers.close()
    dbc.close()



if __name__ == '__main__':

    ti = time.clock()
    print "start - ",ti

    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'popsyntrb')

#    bgs = [[102, 71513, 2],
#           [103, 30372, 3],
#           [103, 30309, 4],
#           [103, 104100, 5],
#           [103, 104000, 5],
#           [104, 103216, 4],
#           [106, 217700, 2],
#           [106, 217002, 3],
#           [106, 217202, 7],
#           [107, 103615, 3]]
    bgs = [[0,0,0]]

    create_marginals(db, bgs)
   
    print "End - ",time.clock()-ti
