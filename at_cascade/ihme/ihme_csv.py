# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ------------------------------------------------------------------------------
import dismod_at
import at_cascade.ihme
# -----------------------------------------------------------------------------
def ihme_csv_one_job(
    fit_node_database          = None ,
    age_group_id_dict          = None ,
    one_age_group_dict         = None ,
    interpolate_all_covariate  = None ,
) :
    assert type(fit_node_database) is str
    assert type(age_group_dict) is dict
    assert type(one_age_group_dict) is dict
    assert type(interpolate_all_covariate) is dict
    assert one_age_group_dict.keys() == interpolate_all_covariate.keys()
    #
    # all_node_database
    all_node_database = cascade.ihme.all_node_database
    #
    # node_table
    file_name = at_cascade.ihme.csv_file['node']
    node_table = at_cascae.ihme.get_table_csv(file_name)
    #
    # integrand_table, age_table, time_table
    new        = False
    connection      = dismod_at.create_connection(fit_node_database, new)
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    age_table       = dismod_at.get_table_dict(connection, 'age')
    time_table      = dismod_at.get_table_dict(connection, 'time')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # all_option_table, split_reference_table
    new               = False
    connection        = dismod_at.create_connection(all_node_database, new)
    all_option_table  = dismod_at.get_table_dict(connection, 'all_option')
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    connection.close()
    #
    # covariate_list
    covariate_list = interpolate_all_covariate.keys()
    #
    # fit_node_dir
    assert fit_node_database.endswith('/dismod.db')
    index        = fit_node_database.rfind('/')
    fit_node_dir = fit_node_database[0:index]
    #
    # fit_split_reference_id
    cov_info = at_cascade.get_cov_info(
        all_option_table, covariate_table, split_reference_table
    )
    fit_split_reference_id  = cov_info['split_reference_id']
    #
    # integrand_id_list
    integrand_id_list = list()
    for integrand_name in at_cascade.ihme.integrand_name2measure_id :
        integrand_id = at_cascade.table_name2id(
            integrand_table, 'integrand', integrand_name
        )
        integrand_id_list.append( integrand_id )
    #
    # year_grid
    # year_id in output file is in demographer notation
    year_grid = [ 1990.5, 1995.5, 2000.5, 2005.5, 2010.5, 2015.5, 2020.5 ]
    #
    # age_group_id_list
    age_group_id_list = age_group_dict.keys()
    #
    # fit_node_name
    fit_node_name   = at_cascade.get_parent_node(fit_node_database)
    #
    # location_id
    location_id = None
    for row in node_table :
        if row['node_name'] == fit_node_name :
            location_id = int( row['location_id'] )
    index = fit_node_name.find('_')
    assert location_id == int( fit_node_name[0:index] )
    #
    # avgint_table
    avgint_table = list()
    #
    # sex, sex_name, sex_id
    row      = split_reference_table[split_reference_id]
    sex      = row['split_reference_value']
    sex_name = row['split_reference_name']
    sex_id   = at_cascade.ihme.sex_info_dict[sex_name]['sex_id']
    #
    # list_str_x
    list_str_x = list()
    for j in range( len(covariate_list) + 2 ) :
        str_x = f'x_{j}'
        list_str_x.append( str_x )
    #
    #
    # age_index
    for age_index in range( len(age_group_id_list) ) :
        #
        # age_group_id
        age_group_id = age_group_id_list[age_index]
        #
        # age_lower, age_upper, age
        age_lower = age_group_dict[age_group_id]['age_lower']
        age_upper = age_group_dict[age_group_id]['age_upper']
        age       = (age_lower + age_upper) / 2.0
        #
        # x
        x = [ sex, 1.0 ]
        for covariate_name in covariate_list :
            fun = interpolate_all_covariate \
                [covariate_name][location_id][sex_name]
            if one_age_group_dict[covariate_name] :
                val = fun(time)
            else :
                val = fun(age, time, grid = False)
            x.append(val)
        #
        # time
        for time in year_grid :
            #
            for integrand_id in integrand_id_list :
                #
                # row
                # Covariates are in same order as covariate_table in the
                # create_root_node_database routine above.
                row = {
                    'integrand_id'    : integrand_id,
                    'node_id'         : fit_node_id,
                    'subgroup_id'     : 0,
                    'weight_id'       : None,
                    'age_lower'       : age_lower,
                    'age_upper'       : age_upper,
                    'time_lower'      : time,
                    'time_upper'      : time,
                    'c_age_group_id'  : age_group_id,
                }
                for j in range( len(x) ) :
                    row[ list_str_x[j] ] = x[j]
                avgint_table.append( row )
    #
    # avgint_table
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    dismod_at.replace_table(connection, 'avgint', avgint_table)
    connection.close()
    #
    # predict sample
    print( 'sample' )
    trace_file.write( 'sample\n' )
    trace_file.flush()
    command = [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    dismod_at.system_command_prc(command, print_command = False )
    #
    # db2csv
    print( 'db2csv' )
    trace_file.write( 'db2csv\n'  )
    trace_file.flush()
    dismod_at.db2csv_command(fit_node_database)
    #
    # rate.pdf
    pdf_file = f'{fit_node_dir}/rate.pdf'
    print( 'rate.pdf' )
    trace_file.write( 'rate.pdf\n' )
    trace_file.flush()
    plot_title = f'{fit_node_name}.{sex_name}'
    rate_set   = { 'iota', 'chi', 'omega' }
    dismod_at.plot_rate_fit(
        fit_node_database, rate_set, pdf_file, plot_title
    )
    #
    # data.pdf
    pdf_file = f'{fit_node_dir}/data.pdf'
    print( 'data.pdf' )
    trace_file.write( 'data.pdf\n' )
    trace_file.flush()
    plot_title = f'{fit_node_name}.{sex_name}'
    dismod_at.plot_data_fit(
        database   = fit_node_database,
        pdf_file   = pdf_file,
        plot_title = plot_title,
        max_plot   = max_plot,
    )
    #
    # predict_table
    new           = False
    connection    = dismod_at.create_connection(fit_node_database, new)
    predict_table = dismod_at.get_table_dict(connection, 'predict')
    connection.close()
    #
    # n_sample
    assert len(predict_table) % len(avgint_table) == 0
    n_sample = int( len(predict_table) / len(avgint_table) )
    #
    # n_avgint
    n_avgint = len( avgint_table )
    #
    # output_table
    output_table = list()
    #
    # plot_data
    plot_data = dict()
    #
    # avgint_row
    for (avgint_id, avgint_row) in enumerate( avgint_table ) :
        #
        # measure_id
        integrand_id    = avgint_row['integrand_id']
        integrand_name  = integrand_table[integrand_id]['integrand_name']
        measure_id      = integrand_name2measure_id[integrand_name]
        #
        # x
        x = list()
        for j in range( len(list_str_x) ) :
            x.append( avgint_row[ list_str_x[j] ] )
        #
        # plot_data[integrand_name]
        if integrand_name not in plot_data :
            plot_data[integrand_name] = list()
        #
        # age_group_id
        age_group_id  = avgint_row['c_age_group_id']
        #
        # year_id
        assert avgint_row['time_lower'] == avgint_row['time_upper']
        year_id = int( avgint_row['time_lower'] )
        #
        # avg_integrand_list
        avg_integrand_list = list()
        #
        # sample_index
        for sample_index in range( n_sample ) :
            #
            # predict_row
            predict_id = sample_index * n_avgint + avgint_id
            predict_row = predict_table[predict_id]
            #
            # some checks
            assert sample_index  == predict_row['sample_index']
            assert avgint_id     == predict_row['avgint_id']
            #
            # avg_integrand
            avg_integrand = predict_row['avg_integrand']
            avg_integrand_list.append( avg_integrand )
        #
        # row
        row = {
            'location_id'    : location_id,
            'sex_id'         : sex_id,
            'age_group_id'   : age_group_id,
            'year_id'        : year_id,
            'measure_id'     : measure_id,
        }
        for (j, covariate_name) in enumerate(covariate_list) :
            row[ covariate_name ] = x[2+j]
        for sample_index in range( n_sample ) :
            key = f'draw_{sample_index}'
            row[key] = avg_integrand_list[sample_index]
        #
        # output_table
        output_table.append(row)
        #
        # row
        mean      = numpy.mean( avg_integrand_list )
        std       = numpy.std( avg_integrand_list, ddof = 1 )
        age_lower = age_group_dict[age_group_id]['age_lower']
        age_upper = age_group_dict[age_group_id]['age_upper']
        age       = (age_lower + age_upper) / 2.0
        time      = avgint_row['time_lower']
        row = {
            'age'   : age,
            'time'  : time,
            'value' : mean,
            'std'   : std,
        }
        #
        # plot_data[integrand_name]
        plot_data[integrand_name].append( row )
    #
    # z_name
    z_list = list( plot_data.keys() )
    for z_name in z_list :
        #
        # max_std, max_value
        max_std   = 0.0
        max_value = 0.0
        for row in plot_data[z_name] :
            max_value = max(max_value, row['std'])
            max_std   = max(max_std, row['std'])
        #
        if max_value == 0.0 :
            # remove both plots for this integrand
            del plot_data[z_name]
        #
        elif max_std == 0.0 :
            # remove std plot for this integrand
            for row in plot_data[z_name] :
                del row['std']
    #
    # ihme.cs
    output_csv = f'{fit_node_dir}/ihme.csv'
    print('ihme.csv')
    trace_file.write('ihme.csv\n')
    trace_file.flush()
    write_csv(output_csv, output_table)
    #
    # plot_limit
    age_min = min(  [ row['age']  for row in age_table  ] )
    age_max = max(  [ row['age']  for row in age_table  ] )
    time_min = min( [ row['time'] for row in time_table ] )
    time_max = max( [ row['time'] for row in time_table ] )
    plot_limit = {
        'age_min'  : age_min,
        'age_max'  : age_max,
        'time_min' : time_min,
        'time_max' : time_max,
    }
    #
    # ihme.pdf
    pdf_file = f'{fit_node_dir}/ihme.pdf'
    print( 'ihme.pdf' )
    trace_file.write( 'ihme.pdf\n' )
    trace_file.flush()
    plot_title = f'{fit_node_name}.{sex_name}'
    dismod_at.plot_curve(
        pdf_file   = pdf_file      ,
        plot_limit = plot_limit      ,
        plot_title = plot_title      ,
        plot_data  = plot_data       ,
    )
# -----------------------------------------------------------------------------
def ihme_csv(covariate_csv_file_dict) :
    #
    # root_node_database
    root_node_database = at_cascade.imhe.root_node_database
    #
    # all_node_database
    all_node_database = at_cascade.imhe.all_node_database
    #
    #
    # node_table, covariate_table
    new        = False
    connection      = dismod_at.create_connection(root_node_database, new)
    node_table      = dismod_at.get_table_dict(connection, 'node')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # all_option_table, split_reference_table, node_split
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_option_table =  dismod_at.get_table_dict(connection, 'all_option')
    node_split_table =  dismod_at.get_table_dict(connection, 'node_split')
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    connection.close()
    #
    # node_split_set
    node_split_set = set()
    for row in node_split_table :
        node_split_set.add( row['node_id'] )
    #
    # root_node_id
    root_node_name = at_cascade.get_parent_node(root_node_database)
    root_node_id   = at_cascade.table_name2id(
            node_table, 'node', root_node_name
    )
    #
    # root_split_reference_id
    if len(split_reference_table) == 0 :
        root_split_refernence_id = None
    else :
        cov_info = at_cascade.get_cov_info(
            all_option_table      = all_option_table ,
            covariate_table       = covariate_table ,
            split_reference_table = split_reference_table,
        )
        root_split_reference_id = cov_info['split_reference_id']
    #
    # job_table
    job_table = at_cascade.create_job_table(
        all_node_database          = all_node_database       ,
        node_table                 = node_table              ,
        start_node_id              = root_node_id            ,
        start_split_reference_id   = root_split_reference_id ,
        fit_goal_set               = fit_goal_set            ,
    )
    #
    # age_group_id_dict
    age_group_id_table = at_cascade.ihme.get_age_group_id_table()
    age_group_id_dict   = dict()
    for row in age_group_id_table :
        age_group_id = row['age_group_id']
        age_group_id_dict[age_group_id] = row
    #
    # one_age_group_dict, interpolate_all_covariate
    one_age_group_dict        = dict()
    interpolate_all_covariate = dict()
    covariate_list             = covariate_csv_file_dict.keys()
    for covariate_name in covariate_list :
        covariate_file_path = covariate_csv_file_dict[covariate_name]
        (one_age_group, interpolate_covariate) = \
            at_cascade.ihme.get_interpolate_covariate(
                covariate_file_path, age_group_id_dict
        )
        one_age_group_dict[covariate_name] = one_age_group
        interpolate_all_covariate[covariate_name] = interpolate_covariate
    #
    # job_row
    for job_row in job_table :
        #
        # fit_database
        fit_node_id            = job_row['fit_node_id']
        fit_split_reference_id = job_row['split_reference_id']
        database_dir           = at_cascade.get_database_dir(
            node_table              = node_table               ,
            split_reference_table   = split_reference_table    ,
            node_split_set          = node_split_set           ,
            root_node_id            = root_node_id             ,
            root_split_reference_id = root_split_reference_id  ,
            fit_node_id             = fit_node_id              ,
            fit_split_reference_id  = fit_split_reference_id   ,
        )
        fit_node_database = f'{database_dir}/dismod.db'
        #
        # predict_one_job
        predict_one_job(
            fit_node_database        = fit_node_database         ,
            age_group_id_dict        = age_group_id_dict         ,
            one_age_group_dict       = one_age_group_dict        ,
            interpolate_all_covarate = interpolate_all_covariate ,
        )
