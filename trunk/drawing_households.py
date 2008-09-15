# Running IPF on Person and Household data

import MySQLdb
import pylab
import time
import os
from numpy import asarray as arr
from numpy import random, histogram, zeros, arange
from ipf_mysql import create_aggregation_string
from ipf_mysql import choose_control_variables

def person_index_matrix(db, pumano = 0):
    dbc = db.cursor()
    if pumano == 0:
        try:
            dbc.execute('create table person_pums_%s select * from person_pums group by hhldid, personid'%(pumano))
        except:
            dbc.execute('drop table person_pums_%s'%(pumano))
            dbc.execute('create table person_pums_%s select * from person_pums group by hhldid, personid'%(pumano))
    else:
        try:
            dbc.execute('create table person_pums_%s select * from person_pums where pumano = %s group by hhldid, personid'%(pumano, pumano))            
        except:
            dbc.execute('drop table person_pums_%s'%(pumano))            
            dbc.execute('create table person_pums_%s select * from person_pums where pumano = %s group by hhldid, personid'%(pumano, pumano))
            
    dbc.execute('alter table person_pums_%s add column id int primary key auto_increment not null first'%(pumano))
    dbc.execute('select hhldid, min(id), max(id) from person_pums_%s group by hhldid'%(pumano))
    result = arr(dbc.fetchall())
    dbc.execute('drop table person_pums_%s'%(pumano))
    dbc.close()
    return result
    

def create_whole_marginals(db, order_string, pumano = 0, tract = 0, bg = 0):
    dbc = db.cursor()
    hhld_ipf = ('hhld_ipf_%s'%(pumano))

    try:
        dbc.execute('create table %s select pumano, tract, bg, frequency from hhld_%s_joint_dist where 0;' %(hhld_ipf, pumano))
        dbc.execute('alter table %s change frequency marginal float'%(hhld_ipf))
        dbc.execute('alter table %s add r_marginal int default 0'%(hhld_ipf))
        dbc.execute('alter table %s add diff_marginals float default 0'%(hhld_ipf))
        dbc.execute('alter table %s add hhlduniqueid int'%(hhld_ipf))
        dbc.execute('alter table %s add index(tract, bg)'%(hhld_ipf))
    except:
        pass
    dbc.execute('select frequency from hhld_%s_joint_dist where tract = %s and bg = %s order by %s;' %(pumano, tract, bg, order_string))
    result = arr(dbc.fetchall())
    rowcount = dbc.rowcount
    dummy_table = zeros((rowcount, 5))
    dummy_table[:,:-2] = [pumano, tract, bg]
    dummy_table[:,-2] = result[:,0]
    dummy_table[:,-1] = (arange(rowcount)+1)

    dbc.execute('delete from %s where tract = %s and bg = %s' %(hhld_ipf, tract, bg))
    dummy_table = str([tuple(i) for i in dummy_table])
    dbc.execute('insert into %s (pumano, tract, bg, marginal, hhlduniqueid) values %s;' %(hhld_ipf, dummy_table[1:-1]))
    dbc.execute('update %s set r_marginal = marginal where tract = %s and bg = %s'%(hhld_ipf, tract, bg))
    dbc.execute('update %s set diff_marginals = (marginal - r_marginal) * marginal where tract = %s and bg = %s'%(hhld_ipf, tract, bg))
    dbc.execute('select sum(marginal) - sum(r_marginal) from %s where tract = %s and bg = %s'%(hhld_ipf, tract, bg))
    result = dbc.fetchall()
    diff_total = round(result[0][0])

  
    if diff_total < 0:
        dbc.execute('select hhlduniqueid from %s where r_marginal <>0 and tract = %s and bg = %s order by diff_marginals '%(hhld_ipf, tract, bg))
    else:
        dbc.execute('select hhlduniqueid from %s where marginal <>0 and tract = %s and bg = %s order by diff_marginals desc'%(hhld_ipf, tract, bg))
    result = dbc.fetchall()

#    print 'The marginals corresponding to the following hhldtypes were changed by the given amount'

    for i in range(int(abs(diff_total))):
#        print 'record - %s changed by %s' %(result[i][0], diff_total / abs(diff_total))
        dbc.execute('update %s set r_marginal = r_marginal + %s where hhlduniqueid = %s and r_marginal <> 0 and tract = %s and bg = %s' %(hhld_ipf, diff_total / abs(diff_total), result[i][0], tract, bg))

    dbc.execute('select r_marginal from %s where marginal <> 0 and tract = %s and bg = %s order by hhlduniqueid'%(hhld_ipf, tract, bg))
    marginals = arr(dbc.fetchall())
    dbc.close()
    
    return marginals
    


def drawing_households(db, hhld_marginals, weights, index_matrix, sp_matrix, pumano = 0):

    dbc = db.cursor()
    dbc.execute('select hhlduniqueid from hhld_pums group by hhlduniqueid')
    hhld_colno = arr(dbc.fetchall())

    synthetic_population=[]

    j = 0
    for i in index_matrix[:hhld_colno.shape[0],:]:
        if i[1] == i[2] and hhld_marginals[j]<>0:
            synthetic_population.append([sp_matrix[i[1]-1, 2] + 1, hhld_marginals[j]])
        else:
            cumulative_weights = weights[sp_matrix[i[1]-1:i[2], 2]].cumsum()
            probability_distribution = cumulative_weights / cumulative_weights[-1]
            probability_lower_limit = probability_distribution[:-1].tolist()
            probability_lower_limit.insert(0,0)
            probability_lower_limit = arr(probability_lower_limit)

            random_numbers = random.rand(hhld_marginals[j])

            freq, probability_lower_limit = histogram(random_numbers, probability_lower_limit)
            hhldid_by_type = sp_matrix[i[1]-1:i[2],2] 

            for k in range(len(freq)):
                if freq[k]<>0:
                    synthetic_population.append([hhldid_by_type[k] + 1, freq[k]])
                    
        j = j + 1
    dbc.close()
    return arr(synthetic_population)

def synthetic_population_properties(db, synthetic_population, person_index_matrix, hhld_attribute_pums, person_attribute_pums):

    dbc = db.cursor()
    
# Layout - hhldid, attributes, frequency

    synthetic_hhld_attributes = zeros((synthetic_population.shape[0], hhld_attribute_pums.shape[1] + 2))
    synthetic_hhld_attributes[:,0] = synthetic_population[:,0] 
    synthetic_hhld_attributes[:,1:-1] =  hhld_attribute_pums[synthetic_population[:,0] - 1,:]
    synthetic_hhld_attributes[:,-1] = synthetic_population[:,1]

# Layout - hhldid, personid, attributes, frequency

# Number of synthetic persons corresponding top the different unique synthetic household id's
    number_synthetic_person =  sum(person_index_matrix[synthetic_population[:,0] - 1,2] -
                                person_index_matrix[synthetic_population[:,0] - 1,1] + 1)
    synthetic_person_attributes = zeros((number_synthetic_person, person_attribute_pums.shape[1] + 1))
# populating the person attribute array with synthetic population information
    dummy = 0
    for i in synthetic_population:
        start_row = dummy
        pums_start_row = person_index_matrix[i[0] - 1,1] - 1

        end_row = start_row + person_index_matrix[i[0] - 1,2] - person_index_matrix[i[0] - 1,1] + 1
        pums_end_row = person_index_matrix[i[0] - 1,2]
        dummy = end_row

        synthetic_person_attributes[start_row:end_row, :2] = person_attribute_pums[pums_start_row:pums_end_row, :2]
        synthetic_person_attributes[start_row:end_row, 2:-1] = person_attribute_pums[pums_start_row:pums_end_row, 2:]
        synthetic_person_attributes[start_row:end_row, -1] = i[1]

 
    dbc.close()
    return synthetic_person_attributes, synthetic_hhld_attributes

def checking_against_joint_distribution(objective_frequency, attributes, dimensions, pumano = 0, tract = 0, bg = 0):

    estimated_frequency = zeros((dimensions.prod(),1))
    for i in attributes[:,-2:]:
        estimated_frequency[i[0]-1,0] = estimated_frequency[i[0]-1, 0] + i[1]

    statistic = 0
    counter = 0
    for i in range(len(objective_frequency)):
        if objective_frequency[i] > 0:
            counter = counter + 1
            statistic = statistic + sum(((objective_frequency[i] - estimated_frequency[i]) ** 2)/ objective_frequency[i])

#    print 'objective', sum(objective_frequency)
#    print 'estimated', sum(estimated_frequency)

    return statistic, counter

def storing_synthetic_attributes(db, synthesis_type, attributes, pumano = 0, tract = 0, bg = 0):
    dbc = db.cursor()
    dbc.execute('delete from %s_synthetic_data where pumano = %d and tract = %d and bg = %d' %(synthesis_type, pumano, tract, bg))
    row_data = [0] * (attributes.shape[-1] + 3)
    row_data[0] = pumano
    row_data[1] = tract
    row_data[2] = bg
    for i in range(attributes.shape[0]):
        row_data[3:] = attributes[i, :]
        dbc.execute('insert into %s_synthetic_data values %s;' %(synthesis_type, str(tuple(row_data))))
    db.commit()
    dbc.close()

def create_synthetic_attribute_tables(db, hhld_control_variables, person_control_variables):
    dbc = db.cursor()
    for synthesis_type in ['hhld','person']:
        try:
            dbc.execute('create table %s_synthetic_data (pumano int, tract int, bg int, \
                                                        hhldid int, %suniqueid int, frequency int)' %(synthesis_type, synthesis_type))
            if synthesis_type == 'hhld':
                control_variables = hhld_control_variables
            else:
                control_variables = person_control_variables
            control_variables.reverse()
            for variable in control_variables:
                dbc.execute('alter table %s_synthetic_data add %s int after hhldid' %(synthesis_type, variable))
            control_variables.reverse()            
            if synthesis_type == 'person':
                dbc.execute('alter table person_synthetic_data add personid int after hhldid')
        except:
            dbc.execute('drop table %s_synthetic_data' %(synthesis_type))
            dbc.execute('create table %s_synthetic_data (pumano int, tract int, bg int, \
                                                        hhldid int, %suniqueid int, frequency int)' %(synthesis_type, synthesis_type))
            if synthesis_type == 'hhld':
                control_variables = hhld_control_variables
            else:
                control_variables = person_control_variables
            control_variables.reverse()
            for variable in control_variables:
                dbc.execute('alter table %s_synthetic_data add %s int after hhldid' %(synthesis_type, variable))
            control_variables.reverse()            
            if synthesis_type == 'person':
                dbc.execute('alter table person_synthetic_data add personid int after hhldid')
    dbc.close()


if __name__ == '__main__':

    db = MySQLdb.connect(user = 'root', passwd = 'mashima', db = 'popsyn')
    dbc = db.cursor()
    ti = time.clock()
#    p_index_matrix = person_index_matrix(db)
#    print 'Person Index Matrix created in %s seconds' %(time.clock()-ti)

#    hhld_control_variables = choose_control_variables(db, 'hhld')
#    person_control_variables = choose_control_variables(db, 'person')
#    create_synthetic_attribute_tables(db, hhld_control_variables, person_control_variables)

    blockgroups_in_puma(db)

    dbc.close()
    db.close()
    

    

    
