# -*- coding: utf-8 -*-

import stock


def index():

    links = [dict(header='', body=get_stock_link)]
    places = SQLFORM.grid(db.place,
                          links=links,
                          links_in_grid=True)

    return dict(places=places,  message="hello from places.py")


@auth.requires(auth.has_membership(role='general manager') or
               auth.has_membership(role='packaging registrator'))
def get_actual_stock_of_place():
    data = stock.get_actual_stock_of_place(request.vars.place)['data']
    # table = SQLTABLE(data)

    #return stock.get_actual_stock_of_place(product_id=request.vars.place)
    return dict(data=data)

def get_stock_link(args):
    url = URL(f='get_actual_stock_of_place', vars=dict(place=args.id))
    return A(T('Stock'), _href=url)
