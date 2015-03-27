# -*- coding: utf-8 -*-

import stock


@auth.requires(auth.has_membership(role='general manager'))
def index():
    return get_actual_stock_of_product()


@auth.requires(auth.has_membership(role='general manager'))
def update_item():
    fields = []
    row = db(db.stock.id==request.vars.id).select(db.stock.product_name,
                                                  db.stock.product_id,
                                                  db.stock.unit,
                                                  db.stock.serial_id,
                                                  db.stock.new_quantity,
                                                  db.stock.best_before_date,
                                                  ).first()
    fields.append(Field('product_name', db.stock, default=row.product_name, writable=False))
    fields.append(Field('serial_id', db.stock, default=row.serial_id, writable=False))
    fields.append(Field('best_before_date', 'date', notnull=False, default=row.best_before_date, writable=False))
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


@auth.requires_membership('general manager')
def get_actual_stock_of_product():
    return stock.get_actual_stock_of_product(product_id=request.vars.product_id,
                                              group_id=request.vars.group)

@auth.requires(auth.has_membership(role='general manager') or
               auth.has_membership(role='packaging registrator'))
def get_actual_stock_of_finished_product():
    response.view = 'actual_stock/index.html'
    request.vars.group = 3
    return stock.get_actual_stock_of_product(product_id=request.vars.product_id,
                                              group_id=3)

@auth.requires(auth.has_membership(role='general manager') or
               auth.has_membership(role='packaging registrator'))
def get_actual_stock_of_unfinished_product():
    response.view = 'actual_stock/index.html'
    request.vars.group = 2
    return stock.get_actual_stock_of_product(product_id=request.vars.product_id,
                                              group_id=2)

@auth.requires(auth.has_membership(role='general manager') or
               auth.has_membership(role='packaging registrator'))
def get_actual_stock_of_packaging_material():
    response.view = 'actual_stock/index.html'
    request.vars.group = 5
    return stock.get_actual_stock_of_product(product_id=request.vars.product_id,
                                              group_id=5)

@auth.requires(auth.has_membership(role='general manager'))
def get_stock_of_product_by_serial_id(product_id, serial_id):
    return None # to be implemented

@auth.requires(auth.has_membership(role='general manager'))
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
                                best_before_date=old_record.best_before_date,
                                created=request.now,
                                remark=request.vars.remark
                                )
