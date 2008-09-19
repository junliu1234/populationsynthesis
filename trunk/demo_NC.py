# Running IPF on Person and Household data

import heuristic_algorithm
import psuedo_sparse_matrix
import drawing_households
import adjusting_pums_joint_distribution
import ipf
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

    print '------------------------------------------------------------------'
    print 'Geography: PUMA ID- %s, Tract ID- %0.2f, BG ID- %s' \
                                                                         %(pumano, float(tract)/100, bg)
    print '------------------------------------------------------------------'
    
    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'ncpopsynnew')
    dbc = db.cursor()
    
    tii = time.clock()
    ti = time.clock()

# Identifying the number of housing units in the disaggregate sample
# Make Sure that the file is sorted by hhid
    dbc.execute('select * from housing_pums')
    housing_pums = numpy.asarray(dbc.fetchall())[:,1:]
    housing_units = dbc.rowcount

# Identifying the control variables for the households, gq's, and persons
    hhld_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'hhld')
    gq_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'gq')
    person_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'person')

# Identifying the number of categories within each control variable for the households, gq's, and persons
    hhld_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'hhld', hhld_control_variables))
    gq_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'gq', gq_control_variables))
    person_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'person', person_control_variables))

#______________________________________________________________________
# Creating the sparse array
    dbc.execute('select * from sparse_matrix1_%s' %(0))
    sp_matrix = numpy.asarray(dbc.fetchall())

#______________________________________________________________________
# Running IPF for Households
    print 'Step 1A: Running IPF procedure for Households... '
    hhld_objective_frequency, hhld_estimated_constraint = ipf.ipf_config_run(db, 'hhld', hhld_control_variables, hhld_dimensions, pumano, tract, bg)
    print 'IPF procedure for Households completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

# Running IPF for GQ
    print 'Step 1B: Running IPF procedure for Gqs... '
    gq_objective_frequency, gq_estimated_constraint = ipf.ipf_config_run(db, 'gq', gq_control_variables, gq_dimensions, pumano, tract, bg)
    print 'IPF procedure for GQ was completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()
    
# Running IPF for Persons
    print 'Step 1C: Running IPF procedure for Persons... '
    person_objective_frequency, person_estimated_constraint = ipf.ipf_config_run(db, 'person', person_control_variables, person_dimensions, pumano, tract, bg)
    print 'IPF procedure for Persons completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()


#______________________________________________________________________
# Creating the weights array
    print 'Step 2: Running IPU procedure for obtaining weights that satisfy Household and Person type constraints... '
    dbc.execute('select rowno from sparse_matrix1_%s group by rowno'%(0))
    result = numpy.asarray(dbc.fetchall())[:,0]
    weights = numpy.ones((1,housing_units), dtype = float)[0] * -99
    weights[result]=1

#______________________________________________________________________
# Creating the control array
    total_constraint = numpy.hstack((hhld_estimated_constraint[:,0], gq_estimated_constraint[:,0], person_estimated_constraint[:,0]))

#______________________________________________________________________
# Running the heuristic algorithm for the required geography
    weights, conv_crit_array, wts_array = heuristic_algorithm.heuristic_adjustment(db, 0, index_matrix, weights, total_constraint, sp_matrix)

    print 'IPU procedure was completed in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()
    

#_________________________________________________________________
    print 'Step 3: Creating the synthetic households and individuals...'
# creating whole marginal values
    
    hhld_order_dummy = adjusting_pums_joint_distribution.create_aggregation_string(hhld_control_variables)
    hhld_frequencies = drawing_households.create_whole_frequencies(db, 'hhld', hhld_order_dummy, pumano, tract, bg)

    gq_order_dummy = adjusting_pums_joint_distribution.create_aggregation_string(gq_control_variables)
    gq_frequencies = drawing_households.create_whole_frequencies(db, 'gq', gq_order_dummy, pumano, tract, bg)
    
    frequencies = numpy.hstack((hhld_frequencies[:,0], gq_frequencies[:,0]))
#______________________________________________________________________
# Drawing Households
#    hhld_controls = adjusting_pums_joint_distribution.choose_control_variables(db, 'hhld')
#    hhld_controls.append('hhlduniqueid')
#    dummy = adjusting_pums_joint_distribution.create_aggregation_string(hhld_controls)
#    hhld_controls.insert(0, 'hhid')
#    hhld_controls.append('frequency')
#    dbc.execute('select %s from hhld_pums' %(dummy))
#    hhld_attribute_pums = numpy.asarray(dbc.fetchall())
#    hhld_layout = ['pumano', 'tract', 'bg', 'hhldid', 'hhldtype', 'hhldsize', 'hhldinc', 'hhlduniqueid', 'frequency']

#    person_controls = adjusting_pums_joint_distribution.choose_control_variables(db, 'person')
#    person_controls.append('personuniqueid')
#    person_controls.insert(0,'personid')
#    person_controls.insert(0,'hhid')
#    dummy = adjusting_pums_joint_distribution.create_aggregation_string(person_controls)
#    dbc.execute('select %s from person_pums' %(dummy))
#    person_attribute_pums = numpy.asarray(dbc.fetchall())
#    person_controls.append('frequency')

# Make Sure that the file is sorted by hhid and personid
    dbc.execute('select * from person_pums')
    person_pums = numpy.asarray(dbc.fetchall())[:,1:]


    p_value = 0
    max_p = 0
    min_chi = 1e10
    draw_count = 0
    while(p_value < 0.9999 and draw_count < 25):
        draw_count = draw_count + 1
        synthetic_housing_units = drawing_households.drawing_housing_units(db, frequencies, weights, index_matrix, sp_matrix, 0)
#        synthetic_housing_units.sort(0)
# Creating synthetic hhld, and person attribute tables

        synthetic_housing_attributes, synthetic_person_attributes = drawing_households.synthetic_population_properties(db, synthetic_housing_units, p_index_matrix, housing_pums, person_pums)
        synth_person_stat, count_person, person_estimated_frequency = drawing_households.checking_against_joint_distribution(person_objective_frequency, 
                                                                                                                                    synthetic_person_attributes, person_dimensions, 
                                                                                                                                     pumano, tract, bg)
        stat = synth_person_stat
        dof = count_person - 1


        p_value = scipy.stats.stats.chisqprob(stat, dof)
        if p_value > max_p or stat < min_chi: 
            max_p = p_value
            max_p_housing_attributes = synthetic_housing_attributes
            max_p_person_attributes = synthetic_person_attributes
            min_chi = stat

    numpy.set_printoptions(precision = 0, suppress = True)
    print numpy.hstack((person_objective_frequency, person_estimated_frequency))

    if draw_count >=25:
        print 'Max Iterations reached for drawing households with the best draw having a p-value of %.4f' %(max_p)
    else:
        print 'Population with desirable p-value of %.4f was obtained in %d iterations' %(max_p, draw_count)

    drawing_households.storing_synthetic_attributes(db, 'housing', max_p_housing_attributes, pumano, tract, bg)
    drawing_households.storing_synthetic_attributes(db, 'person', max_p_person_attributes, pumano, tract, bg)

    dbc.execute('select hhtotal from housing_marginals where pumano = %s and tract = %s and bg = %s'%(pumano, tract, bg))
    housingtotal = dbc.fetchall()[0][0]

    dbc.execute('select sum(gender1 + gender2) from person_marginals where pumano = %s and tract = %s and bg = %s'%(pumano, tract, bg))
    persontotal = dbc.fetchall()[0][0]

    print 'Number of Synthetic Household - %d, and given Household total from the Census SF - %d' %(sum(max_p_housing_attributes[:,-2]), housingtotal)
    print 'Number of Synthetic Persons - %d and given Person total from the Census SF - %d' %(sum(max_p_person_attributes[:,-1]), persontotal)
    print 'Synthetic households created for the geography in %.2f\n' %(time.clock()-ti)

    db.commit()
    dbc.close()
    db.close()


if __name__ == '__main__':

    start = time.clock()
    ti = time.clock()
#    Processes/ methods to be called at the beginning of the pop_synthesis process 
    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'ncpopsynnew')
    dbc = db.cursor()

# Identifying the number of housing units to build the Master Matrix
    dbc.execute('select * from housing_pums')
    housing_units = dbc.rowcount

# Identifying the control variables for the households, gq's, and persons
    hhld_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'hhld')
    gq_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'gq')
    person_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'person')

# Identifying the number of categories within each control variable for the households, gq's, and persons
    hhld_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'hhld', hhld_control_variables))
    gq_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'gq', gq_control_variables))
    person_dimensions = numpy.asarray(adjusting_pums_joint_distribution.create_dimensions(db, 'person', person_control_variables))
        
    print 'Dimensions and Control Variables in %.4f' %(time.clock()-ti)
    ti = time.clock()
    
        
#    update_string = adjusting_pums_joint_distribution.create_update_string(db, hhld_control_variables, hhld_dimensions)
#    adjusting_pums_joint_distribution.add_unique_id(db, 'hhld', update_string)
#    update_string = adjusting_pums_joint_distribution.create_update_string(db, gq_control_variables, gq_dimensions)
#    adjusting_pums_joint_distribution.add_unique_id(db, 'gq', update_string)
#    update_string = adjusting_pums_joint_distribution.create_update_string(db, person_control_variables, person_dimensions)
#    adjusting_pums_joint_distribution.add_unique_id(db, 'person', update_string)
    
    print 'Uniqueid\'s in %.4f' %(time.clock()-ti)
    ti = time.clock()
    
# Populating the Master Matrix	
#    populated_matrix = psuedo_sparse_matrix.populate_master_matrix(db, 0, housing_units, hhld_dimensions, 
#                                                                                               gq_dimensions, person_dimensions)
    print 'Populated in %.4f' %(time.clock()-ti)
    ti = time.clock()

# Sparse representation of the Master Matrix    
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

# Total PUMS Sample x composite_type adjustment for gq    
    adjusting_pums_joint_distribution.create_joint_dist(db, 'gq', gq_control_variables, gq_dimensions, 0, 0, 0)

# Total PUMS Sample x composite_type adjustment for person    
    adjusting_pums_joint_distribution.create_joint_dist(db, 'person', person_control_variables, person_dimensions, 0, 0, 0)
    print 'person_joint_created'
    
#______________________________________________________________________
# creating synthetic_population tables in MySQL
#    drawing_households.create_synthetic_attribute_tables(db)

# This is the serial implementation of the code
#    NC sample geographies
#    geography = [(3300, 970700, 1)]
#    configure_and_run(index_matrix, p_index_matrix, geography[0])
#    print 'Synthesis for %d geographies completed in %.2f' %(len(geography),time.clock()-ti)



# This is the parallel implementation of the code
# Initiating the server and starting the parallelizing process
    ppservers = ()
    if len(sys.argv) > 1:
        ncpus = int(sys.argv[1])
        job_server = pp.Server(ncpus, ppservers = ppservers)
    else:
        job_server = pp.Server(ppservers=ppservers)
    dbc.execute('select pumano from housing_marginals where pumano <>0 group by pumano')
    pumas = numpy.asarray(dbc.fetchall())
    pumas = [[1]]
    for i in pumas:
        dbc.execute('''select pumano, tract, bg from housing_marginals where 
                           pumano = %s and hhtotal <> 0''' %(i[0]))
        blockgroups = list(dbc.fetchall())
        blockgroups = [(3300, 970700, 1)]
        print 'Number of blockgroups in PUMA - %s is %s'%(i[0], len(blockgroups))
        modules = ('heuristic_algorithm','psuedo_sparse_matrix',
                        'drawing_households','adjusting_pums_joint_distribution',
                        'ipf', 'scipy','numpy','pylab','MySQLdb','time',
                        'scipy.stats')
        print 'Using %d cores on the processor' %(job_server.get_ncpus())
        jobs = [(input, job_server.submit(configure_and_run, (index_matrix,
                                                          p_index_matrix,
                                                         input), (), modules)) for input in blockgroups]
    
        for input, job in jobs:
            print job()
        job_server.print_stats()
        print ' Total time for puma - %.2f, Timing per geography - %.2f' %(time.clock()-start, (time.clock()-start)/len(blockgroups))

    dbc.close()
    db.commit()
    db.close()
