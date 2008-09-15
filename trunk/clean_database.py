# This file contains a MySQL class that helps manipulate data. The instance of
# the class also stores the results of the query as a list.

import time
import MySQLdb

def clean_database(db):
    dbc = db.cursor()

    dbc.execute('Show tables')
    result = dbc.fetchall()

    for i in result:
        if check_table(i[0]) == 1:
            print "dropping - %s"%i[0]
            dbc.execute('drop table %s'%i[0])
  
    dbc.close()

def check_table(name):
       
    if name == 'hhld_marginals' or name == 'hhld_pums' or name == 'person_marginals' or \
        name == 'person_pums' or name == 'hhld_puma_marginals' or name == 'person_puma_marginals' \
        or name =='sparse_matrix_0' or name == 'sparse_matrix1_0' or name =='hhld_synthetic_data' or name =='person_synthetic_data':
        return 0
    else:
        return 1


if __name__ == '__main__':

    ti = time.clock()
    print "start - ",ti

    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'popsyntest')
    
    clean_database(db)
   
    print "End - ",time.clock()-ti
