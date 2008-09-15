import MySQLdb

def create_tables(db, project_name):
	
	dbc = db.cursor()
	print ('Create Database %s' %(project_name))
	dbc.execute('Create Database %s' %(project_name))
	dbc.close()
	
	db = MySQLdb.connect(user = 'root', passwd = '1234', db = '%s'%(project_name))
	dbc = db.cursor()
	
	dbc.execute('''Create Table hhld_pums(pumano int,
							     hhldpumsid int,
							     hhldid int,
							     childpresence int,
							     hhldtype int,
							     hhldsize int,
							     hhldinc int)''')
	
	dbc.execute(''' Create Table person_pums(pumano int,
								 hhldpumsid int,
								 hhldid int,
								 personid int,
								 gender int,
								 age int, 
								 race int, 
								 employment int)''')
	
	dbc.execute('''Create Table hhld_marginals(county int,
								  pumano int,
								  tract int,
								  bg int,
								  hhldtotal int,
								  childpresence1 int,
								  childpresence2 int,
								  hhldtype1 int,
								  hhldtype2 int,
								  hhldtype3 int,
								  hhldtype4 int,
								  hhldtype5 int,
								  hhldsize1 int,
								  hhldsize2 int,
								  hhldsize3 int,
								  hhldsize4 int,
								  hhldsize5 int,
								  hhldsize6 int,
								  hhldsize7 int,
								  hhldinc1 int,
								  hhldinc2 int,
								  hhldinc3 int,
								  hhldinc4 int,
								  hhldinc5 int,
								  hhldinc6 int,
								  hhldinc7 int,
								  hhldinc8 int)''')

	dbc.execute(''' Create Table person_marginals(county int,
								       pumano int,
								       tract int,
								       bg int,
								       gender1 int,
								       gender2 int,
								       age1 int, 
								       age2 int, 
								       age3 int, 
								       age4 int, 
								       age5 int, 
								       age6 int, 
								       age7 int, 
								       age8 int, 
								       age9 int, 
								       age10 int, 
								       race1 int,
								       race2 int, 
								       race3 int, 
								       race4 int, 
								       race5 int, 
								       race6 int, 
								       race7 int,
								       employment1 int,
								       employment2 int,
								       employment3 int,
								       employment4 int)''')
	dbc.close()
	db.close()

if __name__ == '__main__':
	db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'test')
	
	create_tables (db, 'NCPopSyn')
	
	db.close()