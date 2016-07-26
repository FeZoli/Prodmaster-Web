# -*- coding: utf-8 -*-

from gluon.tools import Crud

import stock
import local_settings


@auth.requires_login()
def index():
    r = db.waybill_item.waybill==request.vars.waybill
    grid = SQLFORM.grid(r,
                        create=False,
                        searchable=False,
                        csv=False)

    waybill = db.waybill(request.vars.waybill)
    partner = db.partner(waybill.partner)

    return dict(waybill_item_list=grid,
                partner_name=partner.name,
                date=waybill.date_of_delivery.isoformat(),
                reference=waybill.reference,
                waybill=request.vars.waybill)

@auth.requires_login()
def do_delivery():
    waybill = db.waybill(request.vars.waybill)
    if waybill.status != 1:
        response.flash = T('Invalid operation')
        redirect(URL(c='sales_waybills', f='index'))

    partner = db.partner(waybill.partner)
    waybill_items = db(db.waybill_item.waybill==waybill.id).select()

    source_reference = 'SWB/' + str(waybill.id)
    last_quantity = 0.0


    for item in waybill_items:
        last_quantity = stock.get_stock_of_product_by_serial_id(product_id=item.product, serial_id=item.serial_id)

        if last_quantity < item.quantity:
            session.flash = T('Not enough stock of product: ') + item.product_name + ", " + item.serial_id + " Nr.:" + str(item.id)
            db(db.waybill.id==waybill.id).update(status=1) #recorded
            db(db.stock.source_reference == source_reference).delete()
            redirect(URL(c='sales_waybills', f='manage_items', vars=dict(waybill=request.vars.waybill)))
            return

        db.stock.insert(product_id=item.product,
                        product_name=item.product_name,
                        unit=item.unit,
                        quantity_change=0-item.quantity,
                         new_quantity=last_quantity-item.quantity,
                        source_partner_id=0,
                        source_partner_name='Ostya 84',
                        source_doc_id=waybill.id,
                        source_reference=source_reference,
                        target_partner_id=partner.id,
                        target_partner_name=partner.name,
                        date_of_delivery=waybill.date_of_delivery,
                        serial_id=item.serial_id,
                        created=request.now,
                        remark=''
                        )

    db(db.waybill.id==waybill.id).update(status=2) #delivered

    check_and_update_sales_order_status(waybill_items)

    f = [db.stock.product_name,
         db.stock.unit,
         db.stock.quantity_change,
         db.stock.new_quantity,
         db.stock.source_partner_name,
         db.stock.source_reference,
         db.stock.date_of_delivery,
         db.stock.serial_id,
         db.stock.remark]

    r = db.stock.source_reference==source_reference
    grid = SQLFORM.grid(r,
                        fields=f,
                        create=False,
                        editable=False,
                        deletable=False,
                        searchable=False,
                        csv=True,
                        maxtextlengths={'stock.product_name' : local_settings.product_name_max_length})

    return dict(new_stock_items=grid)


def check_and_update_sales_order_status(waybill_items):

    q = None
    s = None

    for item in waybill_items:
        if item.reference and item.reference.startswith("SOI"):
            sum_of_delivered = db(db.sales_order_item.reference==item.reference).select(db.sales_waybill_item.quantity.sum())
            # TODO: update record in sales_order_item
