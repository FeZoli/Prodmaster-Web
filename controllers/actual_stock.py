# -*- coding: utf-8 -*-

@auth.requires_login()
def index():
    return get_actual_stock_of_product()


@auth.requires_login()
def update_item():
    fields = []
    row = db(db.stock.id==request.vars.id).select(db.stock.product_name,
                                                  db.stock.product_id,
                                                  db.stock.unit,
                                                  db.stock.serial_id,
                                                  db.stock.new_quantity
                                                  ).first()
    fields.append(Field('product_name', db.stock, default=row.product_name, writable=False))
    fields.append(Field('serial_id', db.stock, default=row.serial_id, writable=False))
    fields.append(Field('date_of_inventory', 'date', notnull=True))#, default=request.now))
    fields.append(Field('quantity_recorded', 'double', default=row.new_quantity, writable=False))
    fields.append(Field('quantity_real', 'double', notnull=True))
    fields.append(Field('remark', 'text'))

    form = SQLFORM.factory(*fields)

    if form.validate():
        form.vars.id = insert_stock_change(row)
        response.flash = T('Stock has changed successfully')
        session.flash = form.vars.id
        new_vars = {'group' : request.vars.group,
                    'scrollitemid' : str(row.product_id.id)}
        redirect(URL('/index', vars=new_vars))

    return dict(form=form)


@auth.requires_login()
def get_actual_stock_of_product():
    query = (db.product)

    if request.vars.product_id:
        query = db.product.id==request.vars.product_id

    if request.vars.group:
        query = (db.product.product_group==request.vars.group)

    relevant_stock_ids = []

    s = db(query)
    product_rows = s.select(db.product.id)

    for product in product_rows:
        s = db(db.stock==db.product)
        q = (db.stock.product_id==product.id) #&(db.stock.new_quantity>0)
        maxing = db.stock.id.max()
        stock_rows = s(q).select(maxing,
                                 db.stock.new_quantity,
                                 groupby=db.stock.serial_id)

        for stock_row in stock_rows:
            relevant_stock_ids.append(stock_row._extra[maxing])

    s = db(db.stock.product_id==db.product.id)
    q = (db.stock.id.belongs(relevant_stock_ids))&(db.stock.new_quantity>0)
    stock_rows = s(q).select(db.stock.id,
                             db.product.name,
                             db.stock.product_id,
                             db.stock.serial_id,
                             db.stock.new_quantity,
                             orderby=[db.stock.product_name,db.stock.serial_id])
    
    tabledata = []
    prev_prod_id = -1
    prev_prod_name = ''
    prod_total_quantity = 0
    for stock_row in stock_rows:
        tablerow = dict()
        tablerow['id'] = stock_row.stock.id
        tablerow['product_name'] = stock_row.product.name
        tablerow['product_id'] = stock_row.stock.product_id
        tablerow['quantity'] = stock_row.stock.new_quantity
        tablerow['serial_id'] = stock_row.stock.serial_id

        if prev_prod_id == stock_row.stock.product_id:
            prod_total_quantity += stock_row.stock.new_quantity
        else:
            tablerow_sum = dict()
            tablerow_sum['id'] = ''
            tablerow_sum['product_name'] = prev_prod_name
            tablerow_sum['product_id'] = prev_prod_id
            tablerow_sum['quantity'] = prod_total_quantity
            tablerow_sum['serial_id'] = T('Total')
            if prev_prod_id > -1:
                tabledata.append(tablerow_sum)

            prod_total_quantity = stock_row.stock.new_quantity
            prev_prod_id = stock_row.stock.product_id
            prev_prod_name = tablerow['product_name']

        tabledata.append(tablerow)

    return dict(data=tabledata)


@auth.requires_login()
def get_stock_of_product_by_serial_id(product_id, serial_id):
    return None # to be implemented

@auth.requires_login()
def insert_stock_change(old_record):
           id = db.stock.insert(product_id=old_record.product_id,
                                product_name=old_record.product_name,
                                unit=old_record.unit,
                                quantity_change=float(request.vars.quantity_real)-old_record.new_quantity,
                                new_quantity=request.vars.quantity_real,
                                source_partner_id=0,
                                source_partner_name='Ostya 84',
                                source_doc_id=None,
                                source_reference='INV/' + request.vars.date_of_inventory,
                                target_partner_id=0,
                                target_partner_name='Ostya 84',
                                date_of_delivery=request.vars.date_of_inventory,
                                serial_id=old_record.serial_id,
                                created=request.now,
                                remark=request.vars.remark
                                )
