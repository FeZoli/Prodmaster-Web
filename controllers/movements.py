# -*- coding: utf-8 -*-

import stock


@auth.requires_login()
def index():

    l = SQLFORM.grid(db.stock, orderby=~db.stock.id)

    return dict(movement_list=l)


@auth.requires_login()
def get_last_name_of_product():
    return stock.get_last_name_of_product(request.vars.product_id)


@auth.requires_login()
def get_last_unit_price_of_product():
    return stock.get_last_or_recorded_price_of_product(product_id=request.vars.product_id, partner_id=None)
