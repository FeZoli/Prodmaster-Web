# -*- coding: utf-8 -*-

from gluon.tools import Crud
from copy import deepcopy

import stock


@auth.requires_login()
def index():
    query = db.waybill.is_delivery==True
    links = [dict(header='', body=get_intake_link),
             dict(header='', body=get_items_link)]
    grid = SQLFORM.grid(query,
                         onvalidation=validate_item,
                         orderby='~id',
                         links=links,
                         links_in_grid=True)
                         #oncreate=myoncreate)
                         #onupdate=myoncreate)
    
    return dict(waybill_list=grid)

def validate_item(form):
    if form.vars.product != None:
        myoncreate(form)
        form.errors = True
        right_unit = db.product(form.vars.product).unit
        if form.vars.unit != str(right_unit.id):
            form.errors.unit = T('unit can be only \'%s\' for this product') % right_unit.name

    form.vars.is_delivery = True


@auth.requires_login()
def pick():
    set = db((db.stock.product_id==request.vars.product_id)&(db.stock.new_quantity>0))
    max_id = db.stock.id.max()
    rows = set.select(max_id, groupby=(db.stock.serial_id))
    max_id_list = []
    fields = []
    for row in rows:
        max_id_list.append(row[max_id])

    set = db((db.stock.id.belongs(max_id_list))&(db.stock.unit==db.unit.id))
    rows = set.select(db.stock.id,
                      db.stock.serial_id,
                      db.stock.new_quantity,
                      db.unit.name,
                      orderby=~db.stock.date_of_delivery)
    i = 0
    for row in rows:
        fields.append(Field('serial_id_' + str(i), 'string', writable=False,
                            default=row.stock.serial_id, label=T('Serial ID')))
        fields.append(Field('actual_stock_' + str(i), 'string', writable=False,
                            default=str(row.stock.new_quantity) + ' ' + str(row.unit.name)))
        fields.append(Field('picked_quantity_' + str(i), 'float', writable=True, default=0.0))
        i += 1

    grid = SQLFORM.factory(*fields)
    return dict(grid=grid)


def get_intake_link(args):
    if db.waybill(args.id).status != 1 : return '' # intake only if recorded

    url = '/' + request.application + '/delivery/?waybill=' + str(args.id)
    return A(T('Deliver'), _href=url)

def get_items_link(args):
    url = URL('manage_items', vars=dict(waybill=args.id))
    return A(T('Items'), _href=url)

def get_source_link(args):
    url = URL(c='manufacturing_orders',
              f='show_source',
              vars=dict(product_id=args.product, serial_id=args.serial_id))
    return A(T('Source'), _href=url)

@auth.requires_login()
def get_unit():
    unit = db.product(request.vars.product_id).unit
    return unit.id


def myoncreate(form):
    redirect(URL('pick', vars=dict(product_id=form.vars.product)))
    pass

@auth.requires_login()
def manage_items():
    if len(request.args) > 0 and request.args[0] == 'new': return new(request.vars.waybill)
    query = (db.waybill_item.waybill==request.vars.waybill)#&(db.waybill_item.product==db.product.id)&(db.product.can_be_sold==1)
    links = [dict(header='', body=get_source_link)]
    return dict(form=SQLFORM.grid(query, links=links), product_rows=None)


def new(args):
    dataset = db(db.product.can_be_sold==True)
    rows = dataset.select(db.product.id,
                          db.product.name,
                          orderby=db.product.name)

    options = []
    
    for product in rows:
        o = OPTION(product.name, _value=product.id)
        options.append(o)
    
    form = FORM(TABLE(TR(T('Product Name'),
                SELECT(*options, _id='product_select', _name='product_id')),
                TR(T('Valagam'),
                INPUT(_id='valagam')),
                TR(INPUT(_type='submit')))
                )


    return dict(form=None, product_rows=rows)


@auth.requires_login()
def add_item():
    product = db(db.product.id==request.vars.product_id).select(db.product.id,
                                                                db.product.name,
                                                                db.product.unit).first()
    for selling_item in request.vars:
        if selling_item.startswith('sid'):
            selling_data = selling_item.split(':')
            serial_id = selling_data[1]
            quantity = 0.0
            if request.vars[selling_item]:
                quantity = float(request.vars[selling_item])

            if quantity > 0:
                db.waybill_item.insert(waybill=request.vars.waybill_id,
                                       product=product.id,
                                       product_name=product.name,
                                       unit=product.unit,
                                       quantity=quantity,
                                       unit_price_recorded=float(request.vars.unit_price_recorded),
                                       serial_id=serial_id,
                                       remark='')

    redirect(URL('manage_items', vars=dict(waybill=request.vars.waybill_id)))
    return None
