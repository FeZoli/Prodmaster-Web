# -*- coding: utf-8 -*-

import local_settings, stock


@auth.requires_login()
def index():
    q = db.sales_order
    mos = SQLFORM.smartgrid(q,
                            linked_tables=['sales_order_item'],
                            links=[dict(header='', body=get_direct_delivery_link)],
                            maxtextlengths={'sales_order.partner' : local_settings.partner_name_max_length},
                            orderby='~id',
                            deletable=False)

    return dict(mos=mos)


def get_direct_delivery_link(args):
    if hasattr(args, 'sales_order_item'): return '' # hide on child
    # if db.waybill(args.id).status != 1 : return '' # intake only if recorded

    url = URL(f="direct_delivery", vars={'sales_order' : str(args.id)})
    return A(T('Direct Delivery'), _href=url)


@auth.requires(auth.has_membership(role='general manager'))
def direct_delivery():
    sales_order = db.sales_order(request.vars.sales_order)

    partner_name = db.partner(sales_order.partner).name
    delivery_date = sales_order.delivery_date
    remark = sales_order.remark
    reference = 'SOR/' + request.vars.sales_order
    if remark:
        reference += " (%s)" % remark

    f = [db.sales_order_item.id,
         db.sales_order_item.product,
         db.sales_order_item.unit,
         db.sales_order_item.quantity,
         db.sales_order_item.remark]

    q = db.sales_order_item
    s = db(db.sales_order_item.sales_order==request.vars.sales_order)
    grid = SQLFORM.grid(s,
                        fields=f,
                        maxtextlengths={'sales_order_item.product' : local_settings.product_name_max_length},
                        searchable=False,
                        csv=False)

    url = URL(f="do_direct_delivery", vars={'sales_order' : request.vars.sales_order})

    submit_button = FORM(INPUT(_type='submit', _value=T('Direct Delivery')),
                  _action=url)

    return dict(grid=grid, submit_button=submit_button,
                 reference=reference, remark=remark,
                 partner_name=partner_name, date=delivery_date)


@auth.requires(auth.has_membership(role='general manager'))
def do_direct_delivery():

    sor = db.sales_order(request.vars.sales_order)

    wid = db.waybill.insert(partner=sor.partner,
                            date_of_delivery=sor.delivery_date,
                            reference=None,
                            worker=sor.worker,
                            car=sor.car,
                            status=sor.status,
                            is_delivery=True,
                            remark="%s (%s)" % (sor.remark, sor.reference))

    for row in db(db.sales_order_item.sales_order==sor.id).select():
        db.waybill_item.insert(waybill=wid,
                               product=row.product,
                               product_name=row.product.name,
                               unit=row.unit,
                               quantity=row.quantity,
                               unit_price_recorded=0,
                               remark=row.remark)

    redirect(URL(c='sales_waybills', f='index'))
    return


@auth.requires(auth.has_membership(role='general manager') or
               auth.has_membership(role='packaging registrator'))
def check_order_fulfillment():
    sales_order_items = []
    sor = db.sales_order(request.vars.order_id)
    for item in db(db.sales_order_item.sales_order==sor.id).select():
        stock_data = stock.get_actual_stock_of_product(item.product)
        sales_order_items.append(stock_data)
        sales_order_items.append(item)


    return dict(sales_order=sor, items=sales_order_items)
