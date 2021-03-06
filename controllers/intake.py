# -*- coding: utf-8 -*-
# try something like

from gluon.tools import Crud

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
def do_intake():

    wid = request.vars.waybill

    waybill = db.waybill(wid)
    if waybill.status != 1:
        response.flash = T('Invalid operation')
        redirect(URL(c='waybills', f='index'))

    partner = db.partner(waybill.partner)
    waybill_items = db(db.waybill_item.waybill==wid).select()

    source_reference = 'WB/' + str(waybill.id)

    for item in waybill_items:
        # summation of the same serial number items
        query = (db.stock.product_id==item.product)&(db.stock.serial_id==waybill.date_of_delivery)
        row = db(query).select(db.stock.new_quantity, orderby=db.stock.id).last()
        last_quantity = 0
        if row:
            last_quantity = row.new_quantity

        db.stock.insert(product_id=item.product,
                        product_name=item.product_name,
                        unit=item.unit,
                        quantity_change=item.quantity,
                        new_quantity=last_quantity+item.quantity,
                        source_partner_id=partner.id,
                        source_partner_name=partner.name,
                        source_doc_id=waybill.id,
                        source_reference=source_reference,
                        target_partner_id=0,
                        target_partner_name='Ostya 84',
                        place_from=10, # 'beszallito raktara'
                        place_to=6, # 'alapanyag raktár'
                        date_of_delivery=waybill.date_of_delivery,
                        serial_id=waybill.date_of_delivery,
                        unit_price_recorded=item.unit_price_recorded,
                        value_recorded=round(item.value_recorded),
                        created=request.now,
                        remark=''
                        )

        db(db.waybill.id==waybill.id).update(status=2) #delivered

    f = [db.stock.product_id,
         db.stock.product_name,
         db.stock.unit,
         db.stock.quantity_change,
         db.stock.new_quantity,
         db.stock.source_partner_name,
         db.stock.source_doc_id,
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
                        csv=True)

    return dict(new_stock_items=grid)
