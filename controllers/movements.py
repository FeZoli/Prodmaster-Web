# -*- coding: utf-8 -*-

@auth.requires_login()
def index():

    l = SQLFORM.grid(db.stock, orderby=~db.stock.id)

    return dict(movement_list=l)
