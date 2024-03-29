# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

import adjusting_sample_joint_distribution
import numpy

def ipf_config_run (db, synthesis_type, control_variables, varCorrDict, controlAdjDict, 
                    dimensions, state, county, pumano, tract, bg, parameters, hhldsizeMargsMod=False):

    dbc = db.cursor()
# Creating objective joint distributions to match the resulting sunthetic populations against
    #adjusting_sample_joint_distribution.create_joint_dist(db, synthesis_type, control_variables, dimensions, pumano, tract, bg)
    #adjusting_sample_joint_distribution.adjust_weights(db, synthesis_type, control_variables, 
    #                                                   varCorrDict, controlAdjDict,
    #                                                   state, county, pumano, tract, bg, parameters, hhldsizeMargsMod)
    order_dummy = adjusting_sample_joint_distribution.create_aggregation_string(control_variables)

    #dbc.execute('select frequency from %s_%s_joint_dist where tract = %s and bg = %s order by %s'%(synthesis_type, pumano, tract, bg, order_dummy))
    #objective_frequency = numpy.asarray(dbc.fetchall())
# Creating the joint distributions corrected for Zero-cell and Zero-marginal problems
# Example puma x composite_type adjustment for the synthesis type obtained as a parameter
    adjusting_sample_joint_distribution.create_joint_dist(db, synthesis_type, control_variables, dimensions, pumano, tract, bg)
    adjusting_sample_joint_distribution.create_adjusted_frequencies(db, synthesis_type, control_variables, pumano, tract, bg)
    adjusting_sample_joint_distribution.adjust_weights(db, synthesis_type, control_variables, 
                                                       varCorrDict, controlAdjDict,
                                                       state, county, pumano, tract, bg, parameters, hhldsizeMargsMod)
    dbc.execute('select frequency from %s_%s_joint_dist where tract = %s and bg = %s order by %s'%(synthesis_type, pumano, tract, bg, order_dummy))
    estimated_constraint = numpy.asarray(dbc.fetchall())
    objective_frequency = estimated_constraint
    return objective_frequency, estimated_constraint
