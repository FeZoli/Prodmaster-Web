# -*- coding: utf-8 -*-
# try something like

from gluon.tools import Crud

@auth.requires_login()
def index():
    grid = SQLFORM.smartgrid(db.waybill,
                             constraints=dict(waybill=(db.waybill.is_delivery==False)), # this is a purchase
                             linked_tables=['waybill_item'],
                             onvalidation=validate_item,
                             orderby=dict(waybill='~id', waybill_item='id'),
                             links=[dict(header='', body=get_intake_link)],
                             links_in_grid=True)

    return dict(waybill_list=grid)

def validate_item(form):
    if form.vars.product != None:
        right_unit = db.product(form.vars.product).unit
        if form.vars.unit != str(right_unit.id):
            form.errors.unit = T('unit can be only \'%s\' for this product') % right_unit.name

    form.vars.is_delivery = False # it's a purchase

def get_intake_link(args):
    if hasattr(args, 'waybill'): return '' # hide on child
    if db.waybill(args.id).status != 1 : return '' # intake only if recorded

    url = '/' + request.application + '/intake/index/?waybill=' + str(args.id)
    return A(T('Intake'), _href=url)
