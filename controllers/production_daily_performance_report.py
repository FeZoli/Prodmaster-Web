# -*- coding: utf-8 -*-
# try something like
def index():

    table = db.v_daily_sum_performance_financial
    q = table.id > 0

    if request.vars.report_name == 'daily_place_sum':
        table = db.v_daily_place_sum_performance_financial
        q = table.id > 0
        q = q & (table.date_of_production==request.vars.date_of_production)
    elif request.vars.report_name == 'daily_place_product':
        table = db.v_daily_performance_financial
        q = table.id

    if request.vars.show_only_finished_products:
        q = q & (table.finished.product==True)
        
        
    links=[dict(header='Extract', body=get_daily_place_sum_link)]

    grid = SQLFORM.grid(q,
                        orderby='~date_of_production',
                        deletable=False,
                        editable=False,
                        details=False,
                        links=links,
                        links_in_grid=True)

    ### set up filter for finished products ###
    finished_product_filter_link = ''
    if request.vars.show_only_finished_products:
        del(request.vars['show_only_finished_products'])
        url = URL(vars=request.vars)
        finished_product_filter_link = A(T('Show Finished and Unfinished Products'), _href=url)
    else:
        request.vars['show_only_finished_products']=1
        url = URL(vars=dict(request.vars))
        finished_product_filter_link = A(T('Show only Finished Products'), _href=url)

    return dict(finished_product_filter_link=finished_product_filter_link, grid=grid)


def get_daily_place_sum_link(args):
    url = URL(vars=dict(report_name='daily_place_sum',
                        date_of_production=args.date_of_production))
    return A(T('by places...'), _href=url)
