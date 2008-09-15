6# Running IPF on Person and Household data

from heuristic_algorithm import *
from psuedo_sparse_matrix import *
from drawing_households import *
from adjusting_pums_joint_distribution import *

from scipy import stats
from numpy import hstack
import pylab

if __name__ == '__main__':

    db = MySQLdb.connect(user = 'root', passwd = 'mashima', db = 'popsyntrb')
    dbc = db.cursor()
    
    tii = time.clock()
    ti = time.clock()

# Global Variables / Inputs
    pumano = 101
    tract = 40505 
    bg = 1

#    101, 30312, 2
    dbc.execute('select * from hhld_pums')
    rows = dbc.rowcount
    hhld_dimensions = arr(create_dimensions(db, 'hhld'))
    person_dimensions = arr(create_dimensions(db, 'person'))
    
#______________________________________________________________________
# Creating the sparse array
#    populated_matrix = populate_master_matrix(db, 413, 0, rows, hhld_dimensions, person_dimensions)
#    print 'Populated Matrix created in %.2f sec\n'%(time.clock()-ti)
#    ti = time.clock()

#    ps_sp_matrix = psuedo_sparse_matrix(db, populated_matrix, 0)
#    print 'Psuedo Sparse Matrix created in %.2f sec\n'%(time.clock()-ti)
#    ti = time.clock()

#______________________________________________________________________
#Creating Index Matrix
    index_matrix = generate_index_matrix(db, 0)
    print 'Index Matrix created in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()

    dbc.execute('select * from sparse_matrix1_%s' %(0))
    sp_matrix = arr(dbc.fetchall())
#______________________________________________________________________
# creating person index_matrix
    p_index_matrix = person_index_matrix(db)
    print 'The person index matrix was created in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()

#______________________________________________________________________
# Running IPF for Households
    hhld_control_variables = choose_control_variables(db, 'hhld')
# Creating hhld objective joint distributions
    update_string = create_update_string(db, hhld_control_variables, hhld_dimensions)
    add_unique_id(db, 'hhld', update_string)
    create_joint_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, pumano, tract, bg)
    adjust_weights(db, 'hhld', hhld_control_variables, pumano, tract, bg)
    hhld_order_dummy = create_aggregation_string(hhld_control_variables)
    dbc.execute('select frequency from hhld_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, hhld_order_dummy))
    hhld_objective_frequency = arr(dbc.fetchall())
# Total PUMS Sample x composite_type adjustment for hhld    
    create_joint_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, 0, 0, 0)
    create_joint_prob_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, 0, 0, 0)
# Example puma x composite_type adjustment for hhld    
    create_joint_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, pumano, tract, bg)
    upper_bound, sum_puma_frequency = create_joint_prob_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, pumano, tract, bg)
    create_adjusted_joint_prob_dist(db, 'hhld', hhld_control_variables,  upper_bound, sum_puma_frequency, pumano, tract, bg)
    adjust_weights(db, 'hhld', hhld_control_variables, pumano, tract, bg)
    print ('Hhld IPF for PUMA - %s, tract - %s, bg - %s conducted in %.2f sec \n'%(pumano, tract, bg, time.clock()-ti))
    ti = time.clock()

# Running IPF for Households
    person_control_variables = choose_control_variables(db, 'person')
# Creating hhld objective joint distributions
    update_string = create_update_string(db, person_control_variables, person_dimensions)
    add_unique_id(db, 'person', update_string)
    create_joint_dist(db, 'person', person_control_variables, person_dimensions, pumano, tract, bg)
    adjust_weights(db, 'person', person_control_variables, pumano, tract, bg)
    person_order_dummy = create_aggregation_string(person_control_variables)
    dbc.execute('select frequency from person_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, person_order_dummy))
    person_objective_frequency = arr(dbc.fetchall())
# Total PUMS Sample x composite_type adjustment for hhld    
    create_joint_dist(db, 'person', person_control_variables, person_dimensions, 0, 0, 0)
    create_joint_prob_dist(db, 'person', person_control_variables, person_dimensions, 0, 0, 0)
# Example puma x composite_type adjustment for hhld    
    create_joint_dist(db, 'person', person_control_variables, person_dimensions, pumano, tract, bg)
    upper_bound, sum_puma_frequency = create_joint_prob_dist(db, 'person', person_control_variables, person_dimensions, pumano, tract, bg)
    create_adjusted_joint_prob_dist(db, 'person', person_control_variables,  upper_bound, sum_puma_frequency, pumano, tract, bg)
    adjust_weights(db, 'person', person_control_variables, pumano, tract, bg)
    print "Person IPF for PUMA - %s, tract - %s, bg - %s conducted in %.2f sec \n"%(pumano, tract, bg, time.clock()-ti)
    ti = time.clock()
#______________________________________________________________________
# creating synthetic_population tables in MySQL
    create_synthetic_attribute_tables(db, hhld_control_variables, person_control_variables)
    print "Synthetic Data Tables were created in %.2f sec\n"%(time.clock()-ti)
    ti = time.clock()

#______________________________________________________________________
# Creating the weights array
    dbc.execute('select rowno from sparse_matrix1_%s group by rowno'%(0))
    result = arr(dbc.fetchall())[:,0]
    weights = ones((1,rows), dtype = float)[0] * -99
    weights[result]=1
    print 'Weights Array created in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()


#______________________________________________________________________
# Creating the control array
    dbc.execute('select * from person_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, person_order_dummy))
    result = arr(dbc.fetchall())
    person_controls = result[:, -1]
    dbc.execute('select * from hhld_%s_joint_dist where tract = %s and bg = %s order by %s'%(pumano, tract, bg, hhld_order_dummy))
    result = arr(dbc.fetchall())
    hhld_controls = result[:, -1]
    control = hstack((hhld_controls, person_controls))
    print 'Control Array created in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()

#______________________________________________________________________
# Running the heuristic algorithm for the required geography
    weights, conv_crit_array, wts_array = heuristic_adjustment(db, 0, index_matrix, weights, control, hhld_dimensions, sp_matrix)

    sum_heuristic =0
    for i in weights:
        if i <0 and i <>-99:
            print 'wrong weight modified'
        if i>=0:
            sum_heuristic = sum_heuristic +i

    sum_ipf =0
    for j in hhld_controls:
        sum_ipf = sum_ipf + j

    
    print '\nSum of weights from heuristic algo - %.2f, and weights from ipf - %.2f' %(sum_heuristic, sum_ipf)
    print 'The heuristic algorithm was run in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()

#______________________________________________________________________
# creating whole marginal values

    hhld_marginals = create_whole_marginals(db, hhld_order_dummy, pumano, tract, bg)
    print 'The hhld marginals were corrected to reflect whole numbers in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()

#______________________________________________________________________
# Drawing Households
    hhld_controls = choose_control_variables(db, 'hhld')
    hhld_controls.append('hhlduniqueid')
    dummy = create_aggregation_string(hhld_controls)
    hhld_controls.insert(0, 'hhldid')
    hhld_controls.append('frequency')
    dbc.execute('select %s from hhld_pums' %(dummy))
    hhld_attribute_pums = arr(dbc.fetchall())


    person_controls = choose_control_variables(db, 'person')
    person_controls.append('personuniqueid')
    person_controls.insert(0,'personid')
    person_controls.insert(0,'hhldid')
    dummy = create_aggregation_string(person_controls)
    dbc.execute('select %s from person_pums' %(dummy))
    person_attribute_pums = arr(dbc.fetchall())
    person_controls.append('frequency')
    
    p_value = 0
    max_p = 0    
    draw_count = 0
    while(p_value < .9999 and draw_count <25):
        draw_count = draw_count + 1
        synthetic_households = drawing_households(db, hhld_marginals, weights, index_matrix, sp_matrix, 0)
        synthetic_households.sort(0)

# Creating synthetic hhld, and person attribute tables

        person_attributes, hhld_attributes = synthetic_population_properties(db, synthetic_households, p_index_matrix, hhld_attribute_pums, person_attribute_pums)
        synth_hhld_stat, count_hhld = checking_against_joint_distribution(hhld_objective_frequency, hhld_attributes, hhld_dimensions, pumano, tract, bg)
        synth_person_stat, count_person = checking_against_joint_distribution(person_objective_frequency, person_attributes, person_dimensions, pumano, tract, bg)
        stat = synth_hhld_stat + synth_person_stat
        dof = count_hhld + count_person - 1
        p_value = stats.stats.chisqprob(stat, dof)
        if p_value > max_p:
            max_p_synthetic_households = synthetic_households
            max_p = p_value
            max_p_hhld_attributes = hhld_attributes
            max_p_person_attributes = person_attributes

        print 'Draw number - %d, Chi Square Statistic - %.2f, degrees of freedom - %d, p value - %.4f' %(draw_count, stat, dof, p_value)


    print 'SYNTHETIC HOUSEHOLD ATTRIBUTES'
    print hhld_controls
    print max_p_hhld_attributes.astype(int)


    print 'SYNTHETIC PERSON ATTRIBUTES'
    print person_controls
    print max_p_person_attributes.astype(int)

    tiii = time.clock()

    storing_synthetic_attributes(db, 'hhld', max_p_hhld_attributes, pumano, tract, bg)
    storing_synthetic_attributes(db, 'person', max_p_person_attributes, pumano, tract, bg)

    print "Synthetic Data Tables were populated for this geography in %.2f sec\n"%(time.clock()-tiii)

    print 'The attribute matrices and statistic with the desired p-value were created in in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()

    print ('For one Geography the process was completed in %.2f sec\n'%(time.clock()-tii))

    dbc.execute('drop table hhld_0_joint_dist')
    dbc.execute('drop table hhld_0_prob_dist')
    dbc.execute('drop table person_0_joint_dist')
    dbc.execute('drop table person_0_prob_dist')

    for i, idx in enumerate(weights):
        pass

    dbc.close()
    db.close()


