#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.tools import Crud


def create_new_sales_item_form(request):
    db = current.db
    T = current.T

    dataset = db(db.product.can_be_sold==True)
    rows = dataset.select(db.product.id,
                          db.product.name,
                          db.product.unit_price,
                          orderby=db.product.name)

    options = []
    options.append(OPTION('', _value=''))

    for product in rows:
        o = OPTION(product.name, _value=product.id)
        options.append(o)

    form = FORM(TABLE(
                TR(INPUT(_type='submit')),
                TR(INPUT(_type='hidden', _name='waybill_id', _value=request.vars.waybill)),
                TR(T('Product Name'), SELECT(*options, _id='product_select', _name='product_id')),
                TR(T('Unit'), TD(_id='unit_text')),
                TR(T('Unit Price'), INPUT(_name='unit_price_recorded', _id='unit_price_recorded', _value=product.unit_price)),
                _id='datatable'),
                _action = URL('add_item')
                )

    return form


def create_edit_sales_item_form(request):
    db = current.db
    T = current.T

    waybill_item = db.waybill_item(request.args[2])
    dataset = db((db.product.can_be_sold==True)&(db.product.id==waybill_item.product))
    rows = dataset.select(db.product.id,
                          db.product.name,
                          db.product.unit_price,
                          orderby=db.product.name)

    options = []

    for product in rows:
        o = OPTION(product.name, _value=product.id)
        options.append(o)

    form = FORM(TABLE(
                TR(INPUT(_type='button', _value=T('Back'), _onClick="parent.location='%s'" % request.env.http_referer)),
                TR(INPUT(_type='submit')),
                TR(INPUT(_type='hidden', _name='waybill_id', _value=request.vars.waybill)),
                TR(INPUT(_type='hidden', _name='waybill_item_id', _value=waybill_item.id)),
                TR(T('Product Name'), SELECT(*options, _id='product_select', _name='product_id')),
                TR(T('Unit'), TD(_id='unit_text')),
                TR(T('Quantity'), TD(waybill_item.quantity, _name='quantity', _id='quantity', _disabled=True)),
                TR(T('Serial ID recorded'), TD(waybill_item.serial_id, _name='sid_recorded', _id='sid_recorded', _disabled=True)),
                TR(T('Unit Price'), INPUT(_name='unit_price_recorded', _id='unit_price_recorded', _value=product.unit_price)),
                _id='datatable'),
                _action = URL('update_item')
                )

    return form
