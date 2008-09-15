# Running IPF on Person and Household data

import heuristic_algorithm as heuristic_algorithm
import psuedo_sparse_matrix as psuedo_sparse_matrix
import drawing_households as drawing_households
import adjusting_pums_joint_distribution as adjusting_pums_joint_distribution
import scipy
import scipy.stats
import numpy
import pylab
import pp, sys
import MySQLdb
import time
import datetime

def configure_and_run(index_matrix, p_index_matrix, geoid):
    pumano = int(geoid[0])
    tract = int(geoid[1])
    bg = int(geoid[2])

    print '--------------------------------------------------------------------------------'
    print 'Geography: PUMA ID- %s, Tract ID- %0.2f, BG ID- %s' %(pumano, float(tract)/100, bg)
    print '--------------------------------------------------------------------------------'
    
    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'popsyntest')
    dbc = db.cursor()
    
    tii = time.clock()
    ti = time.clock()

    dbc.execute('select * from hhld_pums')
    rows = dbc.rowcount
    hhld_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'hhld'))
    person_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'person'))
#______________________________________________________________________
# Creating the sparse array
    dbc.execute('select * from sparse_matrix1_%s' %(0))
    sp_matrix = numpy.asarray(dbc.fetchall())

#______________________________________________________________________
# Running IPF for Households
    print 'Step 1A: Running IPF procedure for Households... '
    hhld_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'hhld')
# Creating hhld objective joint distributions
    adjusting_pums_joint_distribution.create_joint_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, pumano, tract, bg)
    adjusting_pums_joint_distribution.adjust_weights(db, 'hhld', hhld_control_variables, pumano, tract, bg)
    hhld_order_dummy = adjusting_pums_joint_distribution.create_aggregation_string(hhld_control_variables)
    dbc.execute('select frequency from hhld_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, hhld_order_dummy))
    hhld_objective_frequency = numpy.asarray(dbc.fetchall())
# Example puma x composite_type adjustment for hhld    
    adjusting_pums_joint_distribution.create_joint_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, pumano, tract, bg)
    adjusting_pums_joint_distribution.create_adjusted_frequencies(db, 'hhld', hhld_control_variables, pumano, tract, bg)
    adjusting_pums_joint_distribution.adjust_weights(db, 'hhld', hhld_control_variables, pumano, tract, bg)
    print 'IPF procedure for Households completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

# Running IPF for persons
    print 'Step 1B: Running IPF procedure for Persons... '
    person_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'person')
# Creating person objective joint distributions
    adjusting_pums_joint_distribution.create_joint_dist(db, 'person', person_control_variables, person_dimensions, pumano, tract, bg)
    adjusting_pums_joint_distribution.adjust_weights(db, 'person', person_control_variables, pumano, tract, bg)
    person_order_dummy = adjusting_pums_joint_distribution.create_aggregation_string(person_control_variables)
    dbc.execute('select frequency from person_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, person_order_dummy))
    person_objective_frequency = numpy.asarray(dbc.fetchall())
# Example puma x composite_type adjustment for hhld    
    adjusting_pums_joint_distribution.create_joint_dist(db, 'person', person_control_variables, person_dimensions, pumano, tract, bg)
    adjusting_pums_joint_distribution.create_adjusted_frequencies(db, 'person', person_control_variables, pumano, tract, bg)
    adjusting_pums_joint_distribution.adjust_weights(db, 'person', person_control_variables, pumano, tract, bg)

    print 'IPF procedure for Persons completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

    print 'Step 2: Running IPU procedure for obtaining weights that satisfy Household and Person type constraints... '
#______________________________________________________________________
# Creating the weights array
    dbc.execute('select rowno from sparse_matrix1_%s group by rowno'%(0))
    result = numpy.asarray(dbc.fetchall())[:,0]
    weights = numpy.ones((1,rows), dtype = float)[0] * -99
    weights[result]=1
#______________________________________________________________________
# Creating the control array
    dbc.execute('select * from person_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, person_order_dummy))
    result = numpy.asarray(dbc.fetchall())
    person_controls = result[:, -1]
    dbc.execute('select * from hhld_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, hhld_order_dummy))
    result = numpy.asarray(dbc.fetchall())
    hhld_controls = result[:, -1]
    control = numpy.hstack((hhld_controls, person_controls))

#______________________________________________________________________
# Running the heuristic algorithm for the required geography
    weights, conv_crit_array, wts_array = heuristic_algorithm.heuristic_adjustment(db, 0, index_matrix, weights, control, hhld_dimensions, sp_matrix)

    sum_heuristic =0
    for i in weights:
        if i <0 and i <>-99:
            print 'wrong weight modified'
        if i>=0:
            sum_heuristic = sum_heuristic +i

    sum_ipf =0
    for j in hhld_controls:
        sum_ipf = sum_ipf + j

    
    print 'IPU procedure was completed in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()
    
    print 'Step 3: Creating the synthetic households and individuals...'
#_________________________________________________________________
# creating whole marginal values
    hhld_marginals = drawing_households.create_whole_marginals(db, hhld_order_dummy, pumano, tract, bg)

#______________________________________________________________________
# Drawing Households
    hhld_controls = adjusting_pums_joint_distribution.choose_control_variables(db, 'hhld')
    hhld_controls.append('hhlduniqueid')
    dummy = adjusting_pums_joint_distribution.create_aggregation_string(hhld_controls)
    hhld_controls.insert(0, 'hhldid')
    hhld_controls.append('frequency')
    dbc.execute('select %s from hhld_pums' %(dummy))
    hhld_attribute_pums = numpy.asarray(dbc.fetchall())


    person_controls = adjusting_pums_joint_distribution.choose_control_variables(db, 'person')
    person_controls.append('personuniqueid')
    person_controls.insert(0,'personid')
    person_controls.insert(0,'hhldid')
    dummy = adjusting_pums_joint_distribution.create_aggregation_string(person_controls)
    dbc.execute('select %s from person_pums' %(dummy))
    person_attribute_pums = numpy.asarray(dbc.fetchall())
    person_controls.append('frequency')
    
    p_value = 0
    max_p = 0
    min_chi = 1e10
    draw_count = 0
    while(p_value < 0.9999 and draw_count < 25):
        draw_count = draw_count + 1
        synthetic_households = drawing_households.drawing_households(db, hhld_marginals, weights, index_matrix, sp_matrix, 0)
        synthetic_households.sort(0)
# Creating synthetic hhld, and person attribute tables

        person_attributes, hhld_attributes = drawing_households.synthetic_population_properties(db, synthetic_households, p_index_matrix, hhld_attribute_pums, person_attribute_pums)
        synth_hhld_stat, count_hhld = drawing_households.checking_against_joint_distribution(hhld_objective_frequency, hhld_attributes, hhld_dimensions, pumano, tract, bg)
        synth_person_stat, count_person = drawing_households.checking_against_joint_distribution(person_objective_frequency, person_attributes, person_dimensions, pumano, tract, bg)
#        stat = synth_hhld_stat + synth_person_stat
#        dof = count_hhld + count_person - 1
        stat = synth_person_stat
        dof = count_person - 1


        p_value = scipy.stats.stats.chisqprob(stat, dof)
        if p_value > max_p or stat < min_chi: 
            max_p_synthetic_households = synthetic_households
            max_p = p_value
            max_p_hhld_attributes = hhld_attributes
            max_p_person_attributes = person_attributes
            min_chi = stat


    if draw_count >=25:
        print 'Max Iterations reached for drawing households with a max p-value of %.4f' %(max_p)
    
    drawing_households.storing_synthetic_attributes(db, 'hhld', max_p_hhld_attributes, pumano, tract, bg)
    drawing_households.storing_synthetic_attributes(db, 'person', max_p_person_attributes, pumano, tract, bg)


    dbc.execute('select hhldtotal from hhld_marginals where pumano = %s and tract = %s and bg = %s'%(pumano, tract, bg))
    hhldtotal = dbc.fetchall()[0][0]

    dbc.execute('select sum(gender1 + gender2) from person_marginals where pumano = %s and tract = %s and bg = %s'%(pumano, tract, bg))
    persontotal = dbc.fetchall()[0][0]

    print 'Number of Synthetic Household - %d, and given Household total from the Census SF - %d' %(sum(max_p_hhld_attributes[:,-1]), hhldtotal)
    print 'Number of Synthetic Persons - %d and given Person total from the Census SF - %d' %(sum(max_p_person_attributes[:,-1]), persontotal)
    print 'Synthetic households created for the geography in %.2f\n' %(time.clock()-ti)    
    dbc.close()
    db.close()


if __name__ == '__main__':

    start = time.clock()
    ti = time.clock()
#    Processes/ methods to be called at the beginning of the pop_synthesis process 
    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'popsyntest')
    dbc = db.cursor()

    dbc.execute('select * from hhld_pums')
    rows = dbc.rowcount
    hhld_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'hhld'))
    person_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'person'))
    
    print hhld_dimensions
    print person_dimensions
    
    print 'dimensions - %.4f' %(time.clock()-ti)
    ti = time.clock()
   

    hhld_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'hhld')
    person_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'person')

    print 'control_variables - %.4f' %(time.clock()-ti)
    ti = time.clock()
    
    update_string = adjusting_pums_joint_distribution.create_update_string(db, hhld_control_variables, hhld_dimensions)
    adjusting_pums_joint_distribution.add_unique_id(db, 'hhld', update_string)
    update_string = adjusting_pums_joint_distribution.create_update_string(db, person_control_variables, person_dimensions)
    adjusting_pums_joint_distribution.add_unique_id(db, 'person', update_string)
    print 'uniqueid - %.4f' %(time.clock()-ti)
    ti = time.clock()

#    populated_matrix = psuedo_sparse_matrix.populate_master_matrix(db, 0, rows, hhld_dimensions, person_dimensions)
    print 'populated in %.4f' %(time.clock()-ti)
    ti = time.clock()
    
#    ps_sp_matrix = psuedo_sparse_matrix.psuedo_sparse_matrix(db, populated_matrix, 0)
    print 'psuedo created %.4f' %(time.clock()-ti)
    ti = time.clock()
#______________________________________________________________________
#Creating Index Matrix
#    index_matrix = psuedo_sparse_matrix.generate_index_matrix(db, 0)
    dbc.execute("select * from index_matrix_%s"%(0))
    result = dbc.fetchall()
    index_matrix = numpy.asarray(result)
    print 'index %.4f' %(time.clock()-ti)
    ti = time.clock()


#______________________________________________________________________
# creating person index_matrix
    p_index_matrix = drawing_households.person_index_matrix(db)

# Total PUMS Sample x composite_type adjustment for hhld    
    adjusting_pums_joint_distribution.create_joint_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, 0, 0, 0)

# Total PUMS Sample x composite_type adjustment for hhld    
    adjusting_pums_joint_distribution.create_joint_dist(db, 'person', person_control_variables, person_dimensions, 0, 0, 0)

#______________________________________________________________________
# creating synthetic_population tables in MySQL
    drawing_households.create_synthetic_attribute_tables(db, hhld_control_variables, person_control_variables)

    geography = [(106,217202,1), (106,217202,2)]
    configure_and_run(index_matrix, p_index_matrix, geography[0])
    print 'Synthesis for %d geographies completed in %.2f' %(len(geography),time.clock()-ti)

    
    dbc.close()
    db.close()





