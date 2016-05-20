# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

import local_settings
import stock


@auth.requires_login()
def index():
    grid = SQLFORM.grid(db.manufacturing_order,
                        links=[dict(header='', body=get_process_link)],
                        maxtextlengths={'manufacturing_order.product' : local_settings.product_name_max_length},
                        orderby='status, ~planned_date',
                        deletable=False)

    return dict(manufacturing_order_list=grid)

def get_process_link(args):
    if not db(db.bom.product==db.manufacturing_order(args.id).product).select().first():
        return T("No BOM available!")
    if db.manufacturing_order(args.id).status != 1 :
        url = URL('get_source', vars=dict(mid=str(args.id)))
        return A(T('Sources'), _href=url)

    url = '/' + request.application + '/manufacturing_orders/calculate_picking?id=' + str(args.id)
    return A(T('Manufacture !'), _href=url)

@auth.requires_login()
def get_source():
    mo_id_str = "MO/" + request.vars.mid
    q = db.stock.source_reference==mo_id_str
    date_of_manufacturing = db.manufacturing_order(request.vars.mid).planned_date

    f = [db.stock.product_name,
         db.stock.unit,
         db.stock.quantity_change,
         db.stock.serial_id]

    grid = SQLFORM.grid(q,
                        fields=f,
                        create=False,
                        editable=False,
                        deletable=False,
                        searchable=False,
                        csv=True,
                        maxtextlengths={'stock.product_name' : local_settings.product_name_max_length},)

    return dict(grid=grid, mo_id_str=mo_id_str, date_of_manufacturing=date_of_manufacturing)

@auth.requires_login()
def calculate_picking():
    mo = db.manufacturing_order(request.vars.id)
    product = db.product(mo.product)
    if product.best_before_days > 45:
        mo.best_before_date = mo.planned_date + relativedelta(months=int(round(product.best_before_days/30)))
    else:
        mo.best_before_date = mo.planned_date + timedelta(product.best_before_days)
    bom = db.bom(mo.bom)
    bom_items = db(db.bom_item.bom==bom.id).select()
    is_out_of_stock = False
    o = dict()
    stocks_data = []
    session.flash = ""

    for item in bom_items:
        item_stock_list = stock.get_actual_stock_of_product(product_id=item.product.id)

        block = dict()
        item_stock_id = 0
        act_prod_id = 0
        actual_stock = 0
        act_prods_info = dict()
        rest_from_order = 0
        requested_stock = mo.quantity * (item.quantity / bom.quantity_of_charge)
        rest_from_order = requested_stock
        i = 1
        actual_item_stock = 0.0

        for item_stock in item_stock_list['data']:
            item_stock_id = item_stock['id']

            act_prod_id = item_stock['product_id']
            act_prod_name = item_stock['product_name']

            ## show stock by serial_id
            if item_stock['id']:
                actual_item_stock = item_stock['quantity']
                actual_stock += actual_item_stock

            serial_info = dict()
            serial_info['serial_id'] = item_stock['serial_id']

            serial_info['actual_stock'] = actual_item_stock

            if rest_from_order > 0:
                if actual_item_stock >= rest_from_order:
                    serial_info['reserved_stock'] = round(rest_from_order, 3)
                    rest_from_order = 0
                else:
                    serial_info['reserved_stock'] = round(actual_item_stock, 3)
                    rest_from_order = rest_from_order - actual_item_stock
            else:
                serial_info['reserved_stock'] = 0.000

            if item_stock['id']: # this is the last row, aka. 'Total'
                act_prods_info[i] = serial_info
                i += 1

            if not act_prod_name:
                act_prod_name = db.product(item.product.id).name

            block['product_id'] = act_prod_id
            block['name'] = act_prod_name
            block['requested_stock'] = round(requested_stock, 3)
            block['actual_stock'] = actual_stock
            block['is_out_of_stock'] = False
            if not item_stock['id']:
                rest_stock = round(actual_stock-requested_stock, 3)
                block['is_out_of_stock'] = rest_stock < 0
                block['missing_stock'] = rest_stock
            block['info'] = act_prods_info

            is_out_of_stock = is_out_of_stock or block['is_out_of_stock']

            ### debug
            #block['mo.quantity'] = mo.quantity
            #block['item.quantity'] = item.quantity
            #block['bom.quantity_of_charge'] = bom.quantity_of_charge
            #block['last_sql'] = db._lastsql

            o[act_prod_name] = block

    if is_out_of_stock:
           response.flash = T("One or more products are out of stock !")

    return dict(o=o,
                 product=product,
                 mo=mo,
                 bom=bom,
                 is_out_of_stock=is_out_of_stock)

@auth.requires_login()
def finish_manufacturing():

    mo_id = request.vars.mo_id
    mo = db.manufacturing_order(mo_id)
    date_of_production = request.vars.date_of_production
    best_before_date = request.vars.best_before_date

    # insert raw material movement
    for picking_item in request.vars:
        if picking_item.startswith('reserved-stock'):
            picking_data = picking_item.split('|')
            product_id = picking_data[2]
            serial_id = picking_data[1]
            quantity = 0.0
            if request.vars[picking_item]:
                quantity = float(request.vars[picking_item])

            if quantity > 0:
                set = db((db.stock.product_id==product_id)&(db.stock.serial_id==serial_id))
                row = set(db.stock.product_id==db.product.id).select(db.stock.new_quantity,
                                                                     db.stock.place_to,
                                                                     db.stock.best_before_date,
                                                                     db.product.name,
                                                                     db.product.unit,
                                                                     db.stock.unit_price_recorded,
                                                                     orderby=~db.stock.id,
                                                                     limitby=(0,1)).last()
                last_quantity = 0
                last_place_id = 6 # alapanyag raktar
                last_best_before_date = None
                if row:
                    last_quantity = row.stock.new_quantity
                    last_place = row.stock.place_to
                    last_best_before_date = row.stock.best_before_date

                new_quantity = last_quantity-quantity
                if new_quantity < 0.001:
                    new_quantity = 0.0

                db.stock.insert(product_id=product_id,
                                product_name=row.product.name,
                                unit=row.product.unit,
                                quantity_change=0-quantity,
                                new_quantity=new_quantity,
                                source_partner_id=0,
                                source_partner_name='Ostya 84',
                                source_doc_id=mo_id,
                                source_reference='MO/' + mo_id,
                                target_partner_id=0,
                                target_partner_name='Ostya 84',
                                place_from=last_place,
                                place_to=last_place,
                                date_of_delivery=date_of_production,
                                serial_id=serial_id,
                                best_before_date=last_best_before_date,
                                unit_price_recorded=row.stock.unit_price_recorded,
                                value_recorded=round(row.stock.unit_price_recorded*quantity),
                                created=request.now,
                                remark=''
                                )

    ### insert the newly manufactured product
    q = (db.stock.product_id==request.vars.product_id) & (db.stock.serial_id==request.vars.serial_id)
    row = db(q).select(db.stock.new_quantity,
                       orderby=~db.stock.id,
                       limitby=(0,1)).first()

    product_last_quantity = 0
    product_recorded_price = db.product(request.vars.product_id).unit_price
    if row:
        product_last_quantity = row.new_quantity
    db.stock.insert(product_id=request.vars.product_id,
                    product_name=request.vars.product_name,
                    unit=request.vars.product_unit,
                    quantity_change=request.vars.product_quantity,
                    new_quantity=product_last_quantity+float(request.vars.product_quantity),
                    source_partner_id=0,
                    source_partner_name='Ostya 84',
                    source_doc_id=mo_id,
                    source_reference='MO/' + mo_id,
                    target_partner_id=0,
                    target_partner_name='Ostya 84',
                    place_from=mo.place_from,
                    place_to=mo.place_to,
                    date_of_delivery=date_of_production,
                    serial_id=request.vars.serial_id,
                    best_before_date=request.vars.best_before_date,
                    unit_price_recorded=product_recorded_price,
                    value_recorded=round(product_recorded_price*float(request.vars.product_quantity)),
                    created=request.now,
                    remark=''
                    )

    # calculate some financial indicators
    actual_stock = stock.get_actual_stock_of_product(product_id=request.vars.product_id)
    value_of_raw_materials = stock.get_value_of_raw_materials_in_manufacturing_order(mo_id, request.vars.product_id)
    value_of_finished_product = stock.get_value_of_product_in_manufacturing_order(mo_id, request.vars.product_id)
    additional_value = value_of_finished_product - value_of_raw_materials
    cover = round((additional_value*100)/value_of_finished_product, 1)

    # record the additional value of the production to the actual finished product
    db((db.stock.source_reference=='MO/'+mo_id)&(db.stock.product_id==request.vars.product_id)).update(additional_value=additional_value)

    ### set the status
    db(db.manufacturing_order.id==mo_id).update(status=2) #processed

    f = [db.stock.product_id,
         db.stock.product_name,
         db.stock.unit,
         db.stock.quantity_change,
         db.stock.new_quantity,
 #        db.stock.source_partner_name,
 #        db.stock.source_doc_id,
         db.stock.source_reference,
 #        db.stock.date_of_delivery,
         db.stock.serial_id,
         db.stock.unit_price_recorded,
         db.stock.remark]

    ### show what happened
    r = (db.stock.source_reference=='MO/' + mo_id)&(db.stock.quantity_change!=0)
    grid = SQLFORM.grid(r,
                        fields=f,
                        create=False,
                        editable=False,
                        deletable=False,
                        searchable=False,
                        csv=True,
                        maxtextlengths={'stock.product_name' : local_settings.product_name_max_length},)

    return dict(actual_stock=actual_stock['data'], new_stock_items=grid,
                vrm=value_of_raw_materials, vfp=value_of_finished_product, addv=additional_value, cover=cover)
