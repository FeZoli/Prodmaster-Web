# -*- coding: utf-8 -*-

import local_settings

### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires




def index():
    f = [db.sales_order.partner,
         db.sales_order.delivery_date,
         db.sales_order_item.product,
         db.sales_order.remark]

    q1 = (db.sales_order.status==db.waybill_status.id)&(db.waybill_status.name.contains(['recorded'], ['ordered']))
    q1 = q1&(db.sales_order_item.sales_order==db.sales_order.id)
    ods = SQLFORM.grid(q1,
                       fields=f,
                       maxtextlengths={'sales_order.partner' : local_settings.partner_name_max_length,
                                       'sales_order_item.product' : local_settings.product_name_max_length},
                       orderby='sales_order.delivery_date, sales_order.status',
                       create=False,
                       editable=False,
                       deletable=False,
                       searchable=False,
                       csv=False)

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
                       csv=False)

    return dict(ods=ods, mos=mos)


def error():
    return dict()
