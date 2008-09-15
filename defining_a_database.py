# This file contains a MySQL class that helps manipulate data. The instance of
# the class also stores the results of the query as a list.

import MySQLdb
from  numpy import asarray as arr

class database:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.dbc = self.db.cursor()
        self.debug = 1

    def __getitem__(self, item):
        self.dbc.execute("Select * from %s limit %s, 1"% (self.name, item))
        return self.dbc.fetchone()

    def __delitem__(self, varname, value):
        self.dbc.execute("delete from %s where %s = '%s'"% (self.name, varname, value))
        return self

    def _query(self, q):
        if self.debug: print "Query: %s" % (q)
        self.dbc.execute(q)
        

    def __iter__(self):
        q = "select * from %s" % (self.name)
        self._query(q)
        return self

    def categories(self, varname):
        """Returns the number of unique categories in the supplied variable
        """
        self.dbc.execute("select distinct %s from %s"% ( varname, self.name))
        category_count = self.dbc.rowcount        
        return category_count

    def vardescription(self):
        """Returns the description of the variables in a particular table
        """
        self.dbc.execute("desc %s"% (self.name))

    def variables(self):
        """Returns the description of the variables in a particular table
        """
        self.vardescription()
        result = self.dbc.fetchall()
        self_var_desc = []    
        for dummy in result:
            self_var_desc.append(list(dummy)[0])
        return self_var_desc

    
    def next(self):
        r = self.dbc.fetchone()
        if not r:
            raise StopIteration
        return r

if __name__ == '__main__':
    db = MySQLdb.connect(user = 'root', passwd = 'mashima', db = 'popsyn')
    person = database(db, 'person_pums')
    
    hhld = database(db, 'hhld_pums')

    print hhld.variables()


# Accessing the variables in the household file
    hhld.vardescription()
    result = hhld.dbc.fetchall()
    hhld_var_desc = []    
    for dummy in result:
        hhld_var_desc.append(list(dummy))
    print arr(hhld_var_desc)

# Accessing the number of unique categories in each of the control variables for household file
    for dummy in range(len(hhld_var_desc)):
        hhld.categories(hhld_var_desc[dummy][0])
        result = hhld.dbc.rowcount        
        print result

# Accessing the variables in the person file
    person.vardescription()
    result = person.dbc.fetchall()
    person_var_desc = []    
    for dummy in result:
        person_var_desc.append(list(dummy))
    print arr(person_var_desc)

# Accessing the number of unique categories in each of the control variables for person file
    for dummy in range(len(person_var_desc)):
        person.categories(person_var_desc[dummy][0])
        result = person.dbc.rowcount        
        print result


