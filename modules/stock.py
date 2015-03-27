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
    product_rows = s.select(db.product.id, db.product.name, orderby=db.product.name)

    tabledata = []

    for product in product_rows:
        s = db(db.stock==db.product)
        q = (db.stock.product_id==product.id)
        maxing = db.stock.id.max()
        stock_rows = s(q).select(maxing,
                                 db.stock.new_quantity,
                                 groupby=db.stock.serial_id)

        ### prepare store for summary
        tablerow_sum = dict()
        tablerow_sum['id'] = ''
        tablerow_sum['product_name'] = product.name
        tablerow_sum['product_id'] = product.id
        tablerow_sum['quantity'] = 0.0
        tablerow_sum['serial_id'] = T('Total')

        for stock_row in stock_rows:
            # relevant_stock_ids.append(stock_row._extra[maxing])

            q = (db.stock.product_id==product.id)&(db.stock.id==stock_row._extra[maxing])
            stock_rows = db(q).select(db.stock.id,
                                      db.stock.product_id,
                                      db.stock.serial_id,
                                      db.stock.new_quantity,
                                      orderby=[db.stock.product_name,db.stock.serial_id])

            for stock_row in stock_rows:
                if stock_row.new_quantity > 0:
                    tablerow = dict()
                    tablerow['id'] = stock_row.id
                    tablerow['product_name'] = product.name
                    tablerow['product_id'] = stock_row.product_id
                    tablerow['quantity'] = stock_row.new_quantity
                    tablerow['serial_id'] = stock_row.serial_id
                    tabledata.append(tablerow)
                    tablerow_sum['quantity'] += stock_row.new_quantity

        tabledata.append(tablerow_sum)

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
    if row and row.unit_price_recorded > 0:
        return row.unit_price_recorded

    return db.product(product_id).unit_price
