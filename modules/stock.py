#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.tools import Crud


def get_actual_stock_of_product(product_id=None, group_id=None):
    db = current.db
    T = current.T
    query = (db.product)

    if product_id:
        query = db.product.id==product_id

    if group_id:
        query = (db.product.product_group==group_id)

    relevant_stock_ids = []

    s = db(query)
    product_rows = s.select(db.product.id)

    for product in product_rows:
        s = db(db.stock==db.product)
        q = (db.stock.product_id==product.id) #&(db.stock.new_quantity>0)
        maxing = db.stock.id.max()
        stock_rows = s(q).select(maxing,
                                 db.stock.new_quantity,
                                 groupby=db.stock.serial_id)

        for stock_row in stock_rows:
            relevant_stock_ids.append(stock_row._extra[maxing])

    s = db(db.stock.product_id==db.product.id)
    q = (db.stock.id.belongs(relevant_stock_ids))&(db.stock.new_quantity>0)
    stock_rows = s(q).select(db.stock.id,
                             db.product.name,
                             db.stock.product_id,
                             db.stock.serial_id,
                             db.stock.new_quantity,
                             orderby=[db.stock.product_name,db.stock.serial_id])

    tabledata = []
    prev_prod_id = -1
    prev_prod_name = ''
    prod_total_quantity = 0
    for stock_row in stock_rows:
        tablerow = dict()
        tablerow['id'] = stock_row.stock.id
        tablerow['product_name'] = stock_row.product.name
        tablerow['product_id'] = stock_row.stock.product_id
        tablerow['quantity'] = stock_row.stock.new_quantity
        tablerow['serial_id'] = stock_row.stock.serial_id

        if prev_prod_id == stock_row.stock.product_id:
            prod_total_quantity += stock_row.stock.new_quantity
        else:
            tablerow_sum = dict()
            tablerow_sum['id'] = ''
            tablerow_sum['product_name'] = prev_prod_name
            tablerow_sum['product_id'] = prev_prod_id
            tablerow_sum['quantity'] = prod_total_quantity
            tablerow_sum['serial_id'] = T('Total')
            if prev_prod_id > -1:
                tabledata.append(tablerow_sum)

            prod_total_quantity = stock_row.stock.new_quantity
            prev_prod_id = stock_row.stock.product_id
            prev_prod_name = tablerow['product_name']

        tabledata.append(tablerow)

    return dict(data=tabledata)

def get_stock_of_product_by_serial_id(product_id, serial_id):
    db = current.db
    query = (db.stock.product_id==product_id) & (db.stock.serial_id==serial_id)
    row = db(query).select(db.stock.id,
                           db.stock.new_quantity,
                           db.stock.serial_id,
                           orderby=~db.stock.id,
                           limitby=(0,1)).first()
    if row:
        return row.new_quantity

    return 0


def get_stock_id_of_product_by_serial_id(product_id, serial_id):
    db = current.db
    query = (db.stock.product_id==product_id) & (db.stock.serial_id==serial_id)
    row = db(query).select(db.stock.id,
                           orderby=~db.stock.id,
                           limitby=(0,1)).first()
    if row:
        return row.id

    return 0


def get_last_or_recorded_price_of_product(product_id, partner_id):
    db = current.db
    query = (db.stock.product_id==product_id) & (db.stock.target_partner_id==partner_id)
    row = db(query).select(db.stock.id,
                           db.stock.unit_price_recorded,
                           orderby=~db.stock.id,
                           limitby=(0,1)).first()
    if row:
        return row.unit_price_recorded

    return db.product(product_id).unit_price
