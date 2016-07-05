# -*- coding: utf-8 -*-

import local_settings
from collections import OrderedDict

### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires

@auth.requires_login()
def index():

    order_dict = OrderedDict()

    f = [db.sales_order.id,
         db.sales_order.partner,
         db.sales_order.delivery_date,
         db.sales_order.remark]

    # links = [dict(header='', body=get_details_link),]

    q1 = (db.sales_order.status==db.waybill_status.id)&(db.waybill_status.name.contains(['recorded'], ['ordered']))
    # q1 = q1&(db.sales_order_item.sales_order==db.sales_order.id)

    rows = db(q1).select(db.sales_order.id,
                         db.sales_order.partner,
                         db.sales_order.delivery_date,
                         db.sales_order.place_of_delivery,
                         db.sales_order.worker,
                         db.sales_order.car,
                         db.sales_order.remark,
                         orderby=db.sales_order.delivery_date)

    for row in rows:
        order_items = db(db.sales_order_item.sales_order==row.id).select(db.sales_order_item.product,
                                                                         db.sales_order_item.quantity,
                                                                         db.sales_order_item.remark)
        order_dict[row] = order_items


    f = [db.manufacturing_order.product,
         db.manufacturing_order.planned_date,
         db.manufacturing_order.quantity,
         db.manufacturing_order.unit,
         db.sales_order.remark]

    q2 = (db.manufacturing_order.status==db.waybill_status.id)&(db.waybill_status.name=="recorded")
    mos = SQLFORM.grid(q2,
                       fields=f,
                       maxtextlengths={'manufacturing_order.product' : local_settings.product_name_max_length},
                       orderby='manufacturing_order.status, ~planned_date',
                       create=False,
                       editable=False,
                       deletable=False,
                       searchable=False,
                       details=False,
                       csv=False)

    return dict(ods=order_dict, mos=mos)


def get_details_link(args):
    url = URL(f='sales_orders', vars=dict(sales_order=args.sales_order.id))
    return A(T('Details'), _href=url)


@auth.requires_login()
def sales_orders():
    s = db((db.partner.id==db.sales_order.partner)&(db.sales_order.id==request.vars.sales_order))
    sales_order = s.select(db.partner.name,
                           db.sales_order.delivery_date,
                           db.sales_order.place_of_delivery).first()

    sales_order_items = db(db.sales_order_item.sales_order==request.vars.sales_order).select()


    return dict(so=sales_order, soi=sales_order_items)


def error():
    return dict()
