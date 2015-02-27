# -*- coding: utf-8 -*-

import local_settings

@auth.requires_login()
def index():
    grid = SQLFORM.smartgrid(db.bom, linked_tables=['bom_item'],
                             onvalidation=validate_item,
                             orderby=dict(bom=['product'], bom_item=['~quantity']),
                             links_in_grid=True,
                             maxtextlengths={'bom.product' : local_settings.product_name_max_length})
    return dict(bom_list=grid)

def validate_item(form):
    if form.vars.product != None:
        right_unit = db.product(form.vars.product).unit
        if form.vars.unit != str(right_unit.id):
            form.errors.unit = T('unit can be only \'%s\' for this product') % right_unit.name


@auth.requires_login()
def get_available_boms():
    boms = []
    
    for bom in db(db.bom.product==request.vars.product_id).select():
        boms.append({'id':bom.id,
                     'name':bom.name,
                     'place_from': bom.place_from.id,
                     'place_to': bom.place_to.id})

    return dict(data=boms)
