# -*- coding: utf-8 -*-
# try something like

from gluon.tools import Crud

@auth.requires_login()
def index():
    
    l = SQLFORM.grid(db.product, orderby='name', maxtextlengths={'product.name' : 50},)
    
    return dict(product_list=l)


@auth.requires_login()
def get_unit():
    unit = db.product(request.vars.product_id).unit
    return unit.id

@auth.requires_login()
def get_unit_name():
    unit = db.product(request.vars.product_id).unit
    return unit.name
