#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.tools import Crud


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
