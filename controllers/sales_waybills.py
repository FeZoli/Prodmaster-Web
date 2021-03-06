# -*- coding: utf-8 -*-

from gluon.tools import Crud
from copy import deepcopy

import stock, sales, local_settings, daily_tour_importer


@auth.requires_login()
def index():
    query = db.waybill.is_delivery==True
    links = [dict(header='', body=get_intake_link),
             dict(header='', body=get_items_link)]
    grid = SQLFORM.grid(query,
                        onvalidation=validate_item,
                        orderby='~id',
                        links=links,
                        links_in_grid=True,
                        ondelete="myondelete")

    return dict(waybill_list=grid)

def validate_item(form):
    if form.vars.product != None:
        myoncreate(form)
        form.errors = True
        right_unit = db.product(form.vars.product).unit
        if form.vars.unit != right_unit.id:
            form.errors.unit = T('unit can be only \'%s\' for this product') % right_unit.name

    form.vars.is_delivery = True


@auth.requires_login()
def pick():
    set = db((db.stock.product_id==request.vars.product_id)&(db.stock.new_quantity>0))
    max_id = db.stock.id.max()
    rows = set.select(max_id, groupby=(db.stock.serial_id))
    max_id_list = []
    fields = []
    for row in rows:
        max_id_list.append(row[max_id])

    set = db((db.stock.id.belongs(max_id_list))&(db.stock.unit==db.unit.id))
    rows = set.select(db.stock.id,
                      db.stock.serial_id,
                      db.stock.new_quantity,
                      db.unit.name,
                      orderby=~db.stock.date_of_delivery)
    i = 0
    for row in rows:
        fields.append(Field('serial_id_' + str(i), 'string', writable=False,
                            default=row.stock.serial_id, label=T('Serial ID')))
        fields.append(Field('actual_stock_' + str(i), 'string', writable=False,
                            default=str(row.stock.new_quantity) + ' ' + str(row.unit.name)))
        fields.append(Field('picked_quantity_' + str(i), 'float', writable=True, default=0.0))
        i += 1

    grid = SQLFORM.factory(*fields)
    return dict(grid=grid)


def get_intake_url(args):
    if db.waybill(args.id).status != 1 : return '' # intake only if recorded
    url = URL(c='delivery',
              f='do_delivery',
              vars=dict(waybill=args.id))
    return url

def get_intake_link(args):
    link = get_intake_url(args)
    if link:
        return A(T('Deliver'), _href=get_intake_url(args))
    else:
        return '' 

def get_items_link(args):
    url = URL('manage_items', vars=dict(waybill=args.id))
    return A(T('Items'), _href=url)

def get_source_link(args):
    url = URL(c='manufacturing_orders',
              f='show_source',
              vars=dict(product_id=args.product, serial_id=args.serial_id))
    return A(T('Source'), _href=url)

@auth.requires_login()
def get_unit():
    unit = db.product(request.vars.product_id).unit
    return unit.id


@auth.requires_login()
def myoncreate():
    redirect(URL('pick'), vars=dict(product_id=form.vars.product))
    return None


@auth.requires_login()
def myondelete():
    db(db.waybill_item.waybill==request.vars.waybill).delete()
    session.flash = T('All records deleted.')
    return None


@auth.requires_login()
def manage_items():
    if len(request.args) > 0 and request.args[0] == 'new': return new(request.vars.waybill)
    elif len(request.args) > 0 and request.args[0] == 'edit': return edit(request.vars.waybill)
    query = (db.waybill_item.waybill==request.vars.waybill)
    links = [dict(header='', body=get_source_link)]
    fields = [db.waybill_item.id, db.waybill_item.product, db.waybill_item.quantity, db.waybill_item.unit,
              db.waybill_item.serial_id, db.waybill_item.best_before_date]
    maxtextlengths = {'waybill_item.product': local_settings.product_name_max_length,
                      'unit' : local_settings.unit_max_length}
    grid = SQLFORM.grid(query,
                        fields=fields,
                        maxtextlengths=maxtextlengths,
                        deletable=False,
                        links=links)
    waybill = db.waybill(request.vars.waybill)

    delivery_form = FORM(TABLE(TR(T('Force Picking'), INPUT(_type='checkbox', _name='forced_picking', value=False)),
                               TR(INPUT(_type='submit',  _value=T('Deliver')))),
                         _action=get_intake_url(waybill),
                        )

    upload_form = FORM(TABLE(TR(T('Day of Month'), INPUT(_name='import_day', _size=2)),
                             TR(INPUT(_type='file', _name='upload', _size=60, _maxlength=100000)),
                             TR(INPUT(_type='hidden', _name='waybill', _value=request.vars.waybill)),
                             TR(INPUT(_type='submit', _value=T('Import data from file')))),
                       _action=URL('import_data'),
                      )
    
    return dict(waybill=waybill, form=grid, is_list=True, delivery_form=delivery_form, upload_form=upload_form)


def new(args):
    form = sales.create_new_sales_item_form(request)
    return dict(waybill=db.waybill(request.vars.waybill), form=form, is_list=False, intake_link="")


def edit(args):
    form = sales.create_edit_sales_item_form(request)
    return dict(waybill=db.waybill(request.vars.waybill), form=form, is_list=False, intake_link="")


@auth.requires_login()
def add_item():
    product = db(db.product.id==request.vars.product_id).select(db.product.id,
                                                                db.product.name,
                                                                db.product.unit).first()
    for selling_item in request.vars:
        if selling_item.startswith('sid'):
            selling_data = selling_item.split(':')
            serial_id = selling_data[1]
            best_before_date = db.stock(stock.get_stock_id_of_product_by_serial_id(request.vars.product_id,
                                                                          serial_id)).best_before_date
            quantity = 0.0
            if request.vars[selling_item]:
                quantity = float(request.vars[selling_item])

            if quantity > 0:
                db.waybill_item.insert(waybill=request.vars.waybill_id,
                                       product=product.id,
                                       product_name=product.name,
                                       unit=product.unit,
                                       quantity=quantity,
                                       unit_price_recorded=float(request.vars.unit_price_recorded),
                                       serial_id=serial_id,
                                       best_before_date=best_before_date,
                                       remark='')

    redirect(URL('manage_items', vars=dict(waybill=request.vars.waybill_id)))
    return None


@auth.requires_login()
def update_item():
    delete_is_required = True
    was_updated = False

    for selling_item in request.vars:
        if selling_item.startswith('sid'):
            selling_data = selling_item.split(':')
            serial_id = selling_data[1]
            best_before_date = db.stock(stock.get_stock_id_of_product_by_serial_id(request.vars.product_id,
                                                                          serial_id)).best_before_date
            quantity = 0.0
            if request.vars[selling_item]:
                quantity = float(request.vars[selling_item])

            if quantity > 0 and not was_updated:
                db(db.waybill_item.id==request.vars.waybill_item_id).update(
                                       quantity=quantity,
                                       unit_price_recorded=float(request.vars.unit_price_recorded),
                                       serial_id=serial_id,
                                       best_before_date=best_before_date,
                                       remark='')
                # leave at the 1st Non zero
                delete_is_required = False
                was_updated = True
            elif quantity > 0 and was_updated:
                product = db(db.product.id==request.vars.product_id).select(db.product.id,
                                                                db.product.name,
                                                                db.product.unit).first()
                db.waybill_item.insert(waybill=request.vars.waybill_id,
                                       product=product.id,
                                       product_name=product.name,
                                       unit=product.unit,
                                       quantity=quantity,
                                       unit_price_recorded=float(request.vars.unit_price_recorded),
                                       serial_id=serial_id,
                                       best_before_date=best_before_date,
                                       remark='')

    if delete_is_required:
        db(db.waybill_item.id==request.vars.waybill_item_id).delete()
        response.flash = T("Item deleted.")

    redirect(URL('manage_items', vars=dict(waybill=request.vars.waybill_id)))
    return None


@auth.requires_login()
def import_data():
    import shutil
    if request.vars:
        filename = request.vars.upload.filename
        import_day = request.vars.import_day
        file = request.vars.upload.file
        filename = 'applications/FoodMaster/daily_tour_data/' + filename
        shutil.copyfileobj(file, open(filename, 'wb'))

    data = []

    for rows in daily_tour_importer.get_raw_data(filename, import_day):
        if rows[1] != None:
            cell_date = None
            for cell in rows:
                if cell.row >= 50: ### TODO: repair

                    cell_value = 0
                    if cell.column in ('C', 'E', 'G', 'I', 'K', 'M', 'O'):
                        try: cell_date = cell.value
                        except: pass
                    elif cell.column in ('D', 'F', 'H', 'J', 'L', 'N', 'P'):
                        try: cell_value = cell.value
                        except: pass

                    if cell_value > 0 and cell_date != None:
                        product = db(db.daily_tour_import_mapping.row_number==cell.row).select(db.daily_tour_import_mapping.product).first().product
                        db.waybill_item.insert(waybill=request.vars.waybill,
                                               product=product.id,
                                               product_name=product.name,
                                               unit=product.unit,
                                               quantity=cell_value,
                                               unit_price_recorded=product.unit_price,
                                               serial_id=cell_date.date(),
                                               best_before_date=cell_date.date(),
                                               remark=T('Imported record'))
                        cell_date = None


    if request.env.http_referer:
        redirect(request.env.http_referer)

    return dict(data=None)
