# -*- coding: utf-8 -*-

@auth.requires_login()
def index():
    grid = SQLFORM.smartgrid(db.bom, linked_tables=['bom_item'],
                             onvalidation=validate_item,
                             orderby=dict(bom=['product'], bom_item=['~quantity']),
                             links_in_grid=True,
                             maxtextlengths={'bom.product' : 50},)
    return dict(bom_list=grid)

def validate_item(form):
    if form.vars.product != None:
        right_unit = db.product(form.vars.product).unit
        if form.vars.unit != str(right_unit.id):
            form.errors.unit = T('unit can be only \'%s\' for this product') % right_unit.name
