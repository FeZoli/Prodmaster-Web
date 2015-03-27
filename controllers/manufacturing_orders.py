# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

import local_settings
import stock


@auth.requires_login()
def index():
    grid = SQLFORM.grid(db.manufacturing_order,
                        links=[dict(header='', body=get_process_link)],
                        maxtextlengths={'manufacturing_order.product' : local_settings.product_name_max_length},
                        orderby='status, ~planned_date')

    return dict(manufacturing_order_list=grid)

def get_process_link(args):
    if not db(db.bom.product==db.manufacturing_order(args.id).product).select().first():
        return T("No BOM available!")
    if db.manufacturing_order(args.id).status != 1 :
        url = '/' + request.application + '/stock/get_mo?mid=' + str(args.id)
        return A(T('Sources'), _href=url)

    url = '/' + request.application + '/manufacturing_orders/calculate_picking?id=' + str(args.id)
    return A(T('Manufacture !'), _href=url)


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

    for item in bom_items:
        block = dict()

        stock_query = (db.stock.product_id==item.product.id)
        stock_set = db(stock_query)
        item_stock_list = stock_set.select(db.stock.id.max(),
                                           db.stock.serial_id,
                                           groupby=db.stock.serial_id,
                                           orderby=db.stock.serial_id)

        # check whether we have any record in stock for the item
        if item_stock_list == None or len(item_stock_list) < 1:
            session.flash += "No stock of product: " + item.product.name + " "
            is_out_of_stock = True

        item_stock_id = 0
        act_prod_id = 0
        actual_stock = 0
        act_prods_info = dict()
        rest_from_order = 0
        requested_stock = mo.quantity * (item.quantity / bom.quantity_of_charge)
        rest_from_order = requested_stock
        i = 1

        for item_stock in item_stock_list:
            item_stock_id = item_stock._extra['MAX(stock.id)']
            product_query = (db.stock.id==item_stock_id)
            #if len(item_stock_list) > 1:
            #    product_query &= (db.stock.new_quantity > 0)
            product_set = db(product_query)
            act_product = product_set(db.product.id==db.stock.product_id).select(db.stock.id,
                                                                                 db.product.id,
                                                                                 db.product.name,
                                                                                 db.stock.new_quantity,
                                                                                 db.stock.serial_id).first()

            #block['last_sql'] = db._lastsql

            if not act_product:
                i += 1
                continue

            act_prod_id = item.product.id
            act_prod_name = ""

            ## show stock by serial_id
            actual_item_stock = act_product.stock.new_quantity

            serial_info = dict()
            serial_info['serial_id'] = act_product.stock.serial_id

            act_prod_name = act_product.product.name

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

            if actual_item_stock > 0 or i >= len(item_stock_list):
                act_prods_info[i] = serial_info

            actual_stock += actual_item_stock

            if not act_prod_name:
                act_prod_name = db.product(item.product.id).name

            block['product_id'] = act_prod_id
            block['name'] = act_prod_name
            block['requested_stock'] = round(requested_stock, 3)
            block['actual_stock'] = actual_stock
            block['is_out_of_stock'] = False
            if i >= len(item_stock_list):
                block['is_out_of_stock'] = actual_stock < requested_stock
            i += 1
            block['missing_stock'] = round(actual_stock-requested_stock, 3)
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
                                created=request.now,
                                remark=''
                                )

    ### insert the newly manufactured product
    q = (db.stock.product_id==request.vars.product_id) & (db.stock.serial_id==request.vars.serial_id)
    row = db(q).select(db.stock.new_quantity,
                       orderby=~db.stock.id,
                       limitby=(0,1)).first()

    product_last_quantity = 0
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
                    created=request.now,
                    remark=''
                    )

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
                        maxtextlengths={'stock.product_name' : 50},)

    actual_stock = stock.get_actual_stock_of_product(product_id=request.vars.product_id)

    return dict(actual_stock=actual_stock['data'], new_stock_items=grid)
