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

    for item in waybill_items:
        batches_of_product = stock.get_actual_stock_of_product(product_id=item.product, max_serial_id=item.serial_id)
        rest_quantity = item.quantity

        for batch in reversed(batches_of_product["data"]):
            if batch["serial_id"] == "Total": continue ### TODO: complete rewrite of library !

            quantity_change = 0
            new_quantity = 0
            
            if rest_quantity > batch["quantity"]:
                quantity_change = -batch["quantity"]
                new_quantity = 0
            else:
                quantity_change = -rest_quantity
                new_quantity =  batch["quantity"] - rest_quantity

            rest_quantity -= batch["quantity"]
                
            db.stock.insert(product_id=item.product,
                            product_name=item.product_name,
                            unit=item.unit,
                            quantity_change=quantity_change,
                            new_quantity=new_quantity,
                            source_partner_id=0,
                            source_partner_name='Ostya 84',
                            source_doc_id=waybill.id,
                            source_reference=source_reference,
                            target_partner_id=partner.id,
                            target_partner_name=partner.name,
                            date_of_delivery=waybill.date_of_delivery,
                            serial_id=batch["serial_id"],
                            created=request.now,
                            remark=''
                            )

            if rest_quantity <= 0:
                '''No more stock cycle is necessary'''
                break
            
            pass
        pass # End of for

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
