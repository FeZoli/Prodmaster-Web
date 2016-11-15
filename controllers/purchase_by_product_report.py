# -*- coding: utf-8 -*-

def index():

    dataset = db(db.product.product_group==1)
    rows = dataset.select(db.product.id,
                          db.product.name,
                          orderby=db.product.name)

    options = []
    options.append(OPTION(T('All products'), _value=-9999))


    for product in rows:
        o = OPTION(product.name, _value=product.id)
        options.append(o)

    form = FORM(TABLE(TR(T('First day'), INPUT(_name='start_date', _class='date')),
                      TR(T('Last day'), INPUT(_name='end_date', _class='date')),
                      TR(T('Product'),
                         SELECT(*options, _id='product_select', _name='product_id')),
                      TR(INPUT(_type='submit')))
                )

    if form.process().accepted:
        vars = {'start_date' : request.vars.start_date,
                'end_date' : request.vars.end_date,
                'product_id' : request.vars.product_id,
                'show_sum' : request.vars.show_sum}
        url = URL('show_sales_report', vars=vars)
        redirect(url)

    response.title = T('Purchase by product')
    response.subtitle = ''

    return dict(form=form)


def show_sales_report():
    q = (db.product.id==db.waybill_item.product) & (db.unit.id==db.product.unit) # inner joins first
    q = q & (db.waybill_item.waybill==db.waybill.id) & (db.waybill_item.product==request.vars.product_id) & (db.waybill_item.quantity>0)

    if request.vars.start_date:
        q = q & (db.waybill.date_of_delivery >= request.vars.start_date)

    if request.vars.end_date:
        q = q & (db.waybill.date_of_delivery <= request.vars.end_date)


    # select the actual report rows
    quantity = db.waybill_item.quantity.sum()
    netto = db.waybill_item.value_recorded.sum()
    avg_price = db.waybill_item.unit_price_recorded.avg()
    count_orders = db.waybill_item.id.count()

    s = db(q)
    rows = s.select(db.waybill_item.product,
                    quantity,
                    db.product.unit,
                    netto,
                    avg_price,
                    count_orders,
                    groupby=(db.product.id, db.product.unit))

    headers = {'SUM(waybill_item.quantity)' : T('Quantity'),
               'waybill_item.product' : T('Product'),
               'SUM(waybill_item.value_recorded)' : T('Sum Value'),
               'AVG(waybill_item.unit_price_recorded)' : T('Average Price'),
               'COUNT(waybill_item.id)' : T('Count of Deliveries'),
               'product.unit' : T('Unit') }
    grid = SQLTABLE(rows,
                    headers=headers)

    sql = '' # s._select(groupby=db.waybill.id) # DEBUG

    #sum_data = dict()
    #if request.vars.show_sum == 'on':
    #    sum_row = db(q).select(netto,
    #                           afa,
    #                           brutto).first()

    #    sum_data['netto'] = format(sum_row._extra[netto], ',.2f')
    #    sum_data['afa'] = format(sum_row._extra[afa], ',.2f')
    #    sum_data['brutto'] = format(sum_row._extra[brutto], ',.2f')

    return dict(sql=sql, vars=request.vars, grid=grid)
