



if __name__ == '__main__':

    ti = time.clock()
    db = MySQLdb.connect(user = 'root', passwd = 'mashima', db = 'popsyntrb')
    dbc = db.cursor()

    print ('select hhldtype, sum(frequency) from hhld_synthetic_data where pumano = 106, tract = 217202, bg = 1')
    print ('select hhldtype, sum(frequency) from hhld_synthetic_data where pumano = 106, tract = 217202, bg = 3')
