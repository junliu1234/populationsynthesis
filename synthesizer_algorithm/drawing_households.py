# Running IPF on Person and Household data

import MySQLdb
import time
import os
from numpy import asarray as arr
from numpy import random, histogram, zeros, arange

def person_index_matrix(db, pumano = 0):
    dbc = db.cursor()

    ti = time.time()
    if pumano == 0:
        try:
            dbc.execute('create table person_sample_%s select * from person_sample group by hhid, pnum'%(pumano))
        except:
            dbc.execute('drop table person_sample_%s'%(pumano))
            dbc.execute('create table person_sample_%s select * from person_sample group by hhid, pnum'%(pumano))
    else:
        try:
            dbc.execute('create table person_sample_%s select * from person_sample where pumano = %s group by hhid, pnum'%(pumano, pumano))
        except:
            dbc.execute('drop table person_sample_%s'%(pumano))
            dbc.execute('create table person_sample_%s select * from person_sample where pumano = %s group by hhid, pnum'%(pumano, pumano))


    try:
        dbc.execute('alter table person_sample_%s add column id int primary key auto_increment not null first'%(pumano))
    except Exception, e:
        print e

    dbc.execute('select hhid, min(id), max(id) from person_sample_%s group by hhid'%(pumano))
    result = dbc.fetchall()

    #print 'Person index matrix read in - %.4f' %(time.time()-ti)

    #dbc.execute('drop table person_sample_%s'%(pumano))

    dbc.close()
    db.commit()
    return result


def create_whole_frequencies(db, synthesis_type, order_string, pumano = 0, tract = 0, bg = 0):
    dbc = db.cursor()
    table_name = ('%s_%s_ipf'%(synthesis_type, pumano))



    try:
        dbc.execute('create table %s select pumano, tract, bg, frequency from hhld_%s_joint_dist where 0;' %(table_name, pumano))
        dbc.execute('alter table %s change frequency marginal float(27)'%(table_name))
        dbc.execute('alter table %s add prior int default 0' %(table_name))
        dbc.execute('alter table %s add r_marginal int default 0'%(table_name))
        dbc.execute('alter table %s add diff_marginals float(27) default 0'%(table_name))
        dbc.execute('alter table %s add %suniqueid int'%(table_name, synthesis_type))
        dbc.execute('alter table %s add index(tract, bg)'%(table_name))
    except:
        pass
    dbc.execute('select frequency from %s_%s_joint_dist where tract = %s and bg = %s order by %s;' %(synthesis_type, pumano, tract, bg, order_string))
    frequency = arr(dbc.fetchall())

    dbc.execute('select frequency from %s_0_joint_dist order by %s' %(synthesis_type, order_string))
    prior = arr(dbc.fetchall())

    rowcount = dbc.rowcount
    dummy_table = zeros((rowcount, 6))
    dummy_table[:,:-3] = [pumano, tract, bg]
    dummy_table[:,-3] = frequency[:,0]
    dummy_table[:,-2] = prior[:,0]
    dummy_table[:,-1] = (arange(rowcount)+1)

    dbc.execute('delete from %s where tract = %s and bg = %s' %(table_name, tract, bg))
    dummy_table = str([tuple(i) for i in dummy_table])
    dbc.execute('insert into %s (pumano, tract, bg, marginal, prior, %suniqueid) values %s;' %(table_name, synthesis_type, dummy_table[1:-1]))
    dbc.execute('update %s set r_marginal = marginal where tract = %s and bg = %s'%(table_name, tract, bg))
    dbc.execute('update %s set diff_marginals = (marginal - r_marginal) * marginal where tract = %s and bg = %s'%(table_name, tract, bg))
    dbc.execute('select sum(marginal) - sum(r_marginal) from %s where tract = %s and bg = %s'%(table_name, tract, bg))
    result = dbc.fetchall()
    diff_total = round(result[0][0])


    if diff_total < 0:
        dbc.execute('select %suniqueid from %s where r_marginal <>0 and tract = %s and bg = %s order by diff_marginals '%(synthesis_type, table_name, tract, bg))
    else:
        dbc.execute('select %suniqueid from %s where marginal <>0 and tract = %s and bg = %s order by diff_marginals desc'%(synthesis_type, table_name, tract, bg))
    result = dbc.fetchall()

#    print 'The marginals corresponding to the following hhldtypes were changed by the given amount'

    for i in range(int(abs(diff_total))):
#        print 'record - %s changed by %s' %(result[i][0], diff_total / abs(diff_total))
        dbc.execute('update %s set r_marginal = r_marginal + %s where %suniqueid = %s and tract = %s and bg = %s' %(table_name, diff_total / abs(diff_total), synthesis_type, result[i][0], tract, bg))

    dbc.execute('select r_marginal from %s where prior <> 0 and tract = %s and bg = %s order by %suniqueid'%(table_name, tract, bg, synthesis_type))
    marginals = arr(dbc.fetchall())
    dbc.close()
    db.commit()
    return marginals



def drawing_housing_units(db, frequencies, weights, index_matrix, sp_matrix, pumano = 0):

    dbc = db.cursor()
    dbc.execute('select hhlduniqueid from hhld_sample group by hhlduniqueid')
    hhld_colno = dbc.rowcount
    dbc.execute('select gquniqueid from gq_sample group by gquniqueid')
    gq_colno = dbc.rowcount

    hh_colno = hhld_colno + gq_colno
    synthetic_population=[]
    j = 0
    for i in index_matrix[:hh_colno,:]:
        if i[1] == i[2] and frequencies[j]>0:
            synthetic_population.append([sp_matrix[i[1]-1, 2] + 1, frequencies[j], i[0]])
        else:
            cumulative_weights = weights[sp_matrix[i[1]-1:i[2], 2]].cumsum()
            probability_distribution = cumulative_weights / cumulative_weights[-1]
            probability_lower_limit = probability_distribution.tolist()
            probability_lower_limit.insert(0,0)
            probability_lower_limit = arr(probability_lower_limit)
            random_numbers = random.rand(frequencies[j])
            freq, probability_lower_limit = histogram(random_numbers, probability_lower_limit)
            hhldid_by_type = sp_matrix[i[1]-1:i[2],2]

            for k in range(len(freq)):
                if freq[k]<>0:
                    #hhid = hhidRowDict[hhldid_by_type[k]]
                    # storing the matrix row no, freq, type
                    synthetic_population.append([hhldid_by_type[k], freq[k], i[0]])
        j = j + 1

    dbc.close()
    db.commit()
    return arr(synthetic_population)

def hhid_row_dictionary(housing_sample):
    hhidRowDict = {}
    counter = 0
    for i in housing_sample:
        hhidRowDict[counter] = i[0]
        counter = counter + 1
    return hhidRowDict


def row_hhid_dictionary(person_index_matrix):
    # returns corresponding rowvalue for the hhid in the person_index_matrix
    rowHhidDict = {}
    counter = 0

    for i in person_index_matrix:
        rowHhidDict[i[0]] = counter
        counter = counter + 1
    return rowHhidDict



def synthetic_population_properties(db, geo, synthetic_population, person_index_matrix, housing_sample, person_sample, hhidRowDict, rowHhidDict):

    state, county, pumano, tract, bg = geo.state, geo.county, geo.puma5, geo.tract, geo.bg

    dbc = db.cursor()
# Layout - housing attributes, frequency
    synthetic_housing_attributes = zeros((synthetic_population.shape[0], 8))
    synthetic_housing_attributes[:,0] = state
    synthetic_housing_attributes[:,1] = county
    synthetic_housing_attributes[:,2] = tract
    synthetic_housing_attributes[:,3] = bg
    
    synthetic_housing_attributes[:,4:-2] = housing_sample[synthetic_population[:,0],:]
    
    

    # Store household frequency
    synthetic_housing_attributes[:,-2] = synthetic_population[:,1]
    # Store household unique id
    synthetic_housing_attributes[:,-1] = synthetic_population[:,2]-3

# Number of synthetic persons corresponding to the different unique synthetic household id's
    rows = 0
    for i in synthetic_population:
        hhid = hhidRowDict[i[0]]
        personrowno = rowHhidDict[hhid]
        
        rows = rows + person_index_matrix[personrowno, 2] - person_index_matrix[personrowno, 1] + 1

    synthetic_person_attributes = zeros((rows, 9))


# populating the person attribute array with synthetic population information
    dummy = 0
    synthetic_person_attributes[:,0] = state
    synthetic_person_attributes[:,1] = county
    synthetic_person_attributes[:,2] = tract
    synthetic_person_attributes[:,3] = bg

    for i in synthetic_population:

        start_row = dummy

        # give me hhid of corresponding row
        hhid = hhidRowDict[i[0]]
        # give me the the row number for the hhid in the person index matrix
        personrowno = rowHhidDict[hhid]
        

        pums_start_row = person_index_matrix[personrowno,1] - 1

        end_row = start_row + person_index_matrix[personrowno,2] - person_index_matrix[personrowno,1] + 1


        pums_end_row = person_index_matrix[personrowno,2]
        dummy = end_row


        synthetic_person_attributes[start_row:end_row,4:-2] = person_sample[pums_start_row:pums_end_row, :-1]
        synthetic_person_attributes[start_row:end_row, -2] = i[1]
        #store person unique id
        synthetic_person_attributes[start_row:end_row, -1] = person_sample[pums_start_row:pums_end_row, -1]

    dbc.close()
    db.commit()
    return synthetic_housing_attributes, synthetic_person_attributes


def checking_against_joint_distribution(objective_frequency, attributes, dimensions, pumano = 0, tract = 0, bg = 0):

    estimated_frequency = zeros((dimensions.prod(),1))
    
    for i in attributes[:,-2:]:
        #print i
        estimated_frequency[i[1]-1,0] = estimated_frequency[i[1]-1, 0] + i[0]

    statistic = 0
    counter = 0
    for i in range(len(objective_frequency)):
        if objective_frequency[i] > 0:
            counter = counter + 1

            statistic = statistic + sum(((objective_frequency[i] - estimated_frequency[i]) ** 2)/ objective_frequency[i])

    return statistic, counter, estimated_frequency

def storing_synthetic_attributes(db, synthesis_type, attributes, county, tract = 0, bg = 0):
    dbc = db.cursor()
    dbc.execute('delete from %s_synthetic_data where county = %s and tract = %s and bg = %s' %(synthesis_type, county, tract, bg))

    for i in range(attributes.shape[0]):
        dbc.execute('insert into %s_synthetic_data values %s;' %(synthesis_type, str(tuple(attributes[i,:]))))
    dbc.close()
    db.commit()


def create_performance_table(db):
    dbc = db.cursor()
    dbc.execute("""create table if not exists performance_statistics(state int, county int, tract int,"""
                """bg int, chivalue float, pvalue float, synpopiter float, heuriter float, aardvalue float)""")
    dbc.execute("""delete from performance_statistics""")
    dbc.close()
    db.commit()

def store_performance_statistics(db, geo, values):

    state, county, pumano, tract, bg = geo.state, geo.county, geo.puma5, geo.tract, geo.bg

    dbc = db.cursor()
    dbc.execute("""delete from performance_statistics where"""
                """ county = %s and tract = %s and bg = %s""" %(county, tract, bg))
    dbc.execute("""insert into performance_statistics values %s""" %str(values))
        
    dbc.close()
    db.commit()

def create_synthetic_attribute_tables(db):
    dbc = db.cursor()
    dbc.execute("""create table if not exists housing_synthetic_data(state int, county int, tract int, bg int,"""
                """hhid int, serialno int, frequency int, hhuniqueid int)""")
    dbc.execute("""create table if not exists person_synthetic_data(state int, county int, tract int, bg int,"""
                """hhid int, serialno int, pnum int,  frequency int, personuniqueid int)""")
    dbc.execute("""delete from housing_synthetic_data""")
    dbc.execute("""delete from person_synthetic_data""")
    dbc.close()
    db.commit()


if __name__ == '__main__':
    pass




