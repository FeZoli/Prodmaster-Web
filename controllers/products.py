# -*- coding: utf-8 -*-
# try something like

from gluon.tools import Crud

import stock

@auth.requires_login()
def index():

    l = SQLFORM.grid(db.product, orderby='name', maxtextlengths={'product.name' : 50},)

    return dict(product_list=l)


@auth.requires_login()
def get_product():
    return dict(data=db.product(request.vars.product_id))

@auth.requires_login()
def get_unit():
    unit = db.product(request.vars.product_id).unit
    return unit.id

@auth.requires_login()
def get_unit_name():
    unit = db.product(request.vars.product_id).unit
    return unit.name

@auth.requires_login()
def get_last_or_recorded_price_of_product():
    price = stock.get_last_or_recorded_price_of_product(request.vars.product_id, request.vars.partner_id)
    return price
