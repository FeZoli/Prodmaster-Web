# -*- coding: utf-8 -*-

from gluon import current
from datetime import timedelta,date
import dbdata

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

#if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
db = dbdata.get_db()
current.db = db ## to be available from modules

# db = DAL('sqlite:///home/fekete/backup/FoodMaster/FoodMaster.db', migrate=True)
#else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
#    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
#    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] # if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

#### module development purposes. Comment out, when finished!
from gluon.custom_import import track_changes; track_changes(True)
from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=True)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.actions_disabled.append('register')
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.janrain_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('partner',
                Field('name','string', length=64, unique=True, notnull=True),
                Field('reg_number','string', length=32),
                Field('bank_account','string', length=32),
                Field('head_city','string', length=32),
                Field('head_zip','string', length=8),
                Field('head_address','string', length=64),
                Field('customer', 'boolean', notnull=True),
                Field('supplier', 'boolean', notnull=True),
                Field('is_active', 'boolean', notnull=True, default=True),
                Field('remark', 'text')
                )

db.define_table('unit',
                Field('name', 'string', length=8, unique=True, notnull=True),
                Field('remark', 'text')
                )

db.define_table('product_subgroup',
                Field('name', 'string', length=32, unique=True, notnull=True),
                Field('remark', 'text')
                )

db.define_table('product_group',
                Field('name', 'string', length=32, unique=True, notnull=True),
                Field('remark', 'text')
                )

db.define_table('product',
                Field('name', 'string', length=128, unique=True, notnull=True),
                Field('unit', db.unit),
                Field('product_group', db.product_group),
                Field('can_be_purchased', 'boolean', notnull=True),
                Field('can_be_sold', 'boolean', notnull=True),
                Field('can_be_manufactured', 'boolean', notnull=True),
                Field('unit_price', 'double', notnull=True),
                Field('best_before_days', 'integer'),
                Field('remark', 'text'),
                migrate=False
                )

db.product.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.product.product_group.represent = lambda id,row: db.product_group(id).name
db.product.unit.represent = lambda id,row: db.unit(id).name
db.product.product_group.requires = IS_IN_DB(db, db.product_group.id, '%(name)s')

db.define_table('product_subgroup_map',
                Field('product', db.product),
                Field('product_subgroup', db.product_subgroup)
                )

db.product_subgroup_map.product.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.product_subgroup_map.product.represent = lambda id,row: db.product(id).name
db.product_subgroup_map.product_subgroup.represent = lambda id,row: db.product_subgroup(id).name
db.product_subgroup_map.product_subgroup.requires = IS_IN_DB(db, db.product_subgroup.id, '%(name)s')

db.define_table('car',
                Field('name', 'string', length=32, notnull=True, unique=True),
                Field('plate_number', 'string', length=16, notnull=True, unique=True),
                Field('remark', 'text')
                )

db.define_table('worker',
                Field('name', 'string', length=32, notnull=True, unique=True),
                Field('remark', 'text')
                )

db.define_table('waybill_status',
                Field('name', 'string', length=16, notnull=True),
                Field('weight', 'integer'),
                Field('remark', 'text')
                )

db.define_table('waybill',
                Field('partner', db.partner),
                Field('date_of_delivery', 'date', notnull=True),
                Field('reference', 'string', length=32),
                Field('worker', db.worker),
                Field('car', db.car),
                Field('status', db.waybill_status, writable=False, notnull=True, default=1),
                Field('is_delivery', 'boolean', notnull=True, default=True, writable=False, readable=False),
                Field('remark', 'text')
                )

db.waybill.partner.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.waybill.partner.represent = lambda id,row: db.partner(id).name
db.waybill.worker.requires = IS_IN_DB(db, db.worker.id, '%(name)s')
db.waybill.worker.represent = lambda id,row: db.worker(id).name
db.waybill.car.requires = IS_IN_DB(db, db.car.id, '%(plate_number)s')
db.waybill.car.represent = lambda id,row: db.car(id).plate_number
db.waybill.status.requires = IS_IN_DB(db, db.waybill_status.id, '%(name)s')
db.waybill.status.represent = lambda id,row: db.waybill_status(id).name

db.define_table('waybill_item',
                Field('waybill', db.waybill),
                Field('product', db.product),
                Field('product_name', 'string', length=32, notnull=True),
                Field('unit', db.unit),
                Field('quantity', 'double', notnull=True),
                Field('unit_price_recorded', 'double', notnull=True),
                Field('serial_id', 'string', length=64, default=date.today()),
                Field('best_before_date', 'date'),
                Field('value_recorded', 'double', writable=False, notnull=True,
                      compute=lambda r: r.quantity*r.unit_price_recorded),
                Field('remark', 'text')
                )

db.waybill_item.waybill.requires = IS_IN_DB(db, db.waybill.id, '%(id)s %(partner)s %(date_of_delivery)s')
db.waybill_item.product.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.waybill_item.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.waybill_item.product.represent = lambda id,row: db.product(id).name
db.waybill_item.unit.represent = lambda id,row: db.unit(id).name
db.waybill_item.quantity.requires = IS_EXPR('value>0')

db.define_table('place',
                Field('name', 'string', length=64, notnull=True),
                Field('remark', 'text')
                )

db.define_table('stock',
                Field('product_id', db.product),
                Field('product_name', 'string', length=128, notnull=True),
                Field('unit', db.unit),
                Field('quantity_change', 'double', notnull=True),
                Field('new_quantity', 'double', writable=False, notnull=True),
                Field('source_partner_id', db.partner),
                Field('source_partner_name', 'string', length=32),
                Field('source_doc_id', 'integer'),
                Field('source_reference', 'string', length=16),
                Field('target_partner_id', db.partner),
                Field('target_partner_name', 'string', length=32),
                Field('place_from', db.place),
                Field('place_to', db.place),
                Field('date_of_delivery', 'date', default=request.now),
                Field('serial_id', 'string', length=64),
                Field('best_before_date', 'date'),
                Field('unit_price_recorded', 'double', notnull=True),
                Field('value_recorded', 'double', notnull=True),
                Field('additional_value', 'double', notnull=True, default=0.0),
                Field('created', 'datetime', writable=False, default=request.now),
                Field('remark', 'text')
                )

db.stock.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.stock.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.stock.place_from.requires = IS_IN_DB(db, db.place.id, '%(name)s')
db.stock.place_to.requires = IS_IN_DB(db, db.place.id, '%(name)s')
db.stock.source_partner_id.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.stock.target_partner_id.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.stock.date_of_delivery.requires = IS_DATE(format=('%Y-%m-%d'))
db.stock.unit.represent = lambda id,row: db.unit(id).name
db.stock.place_from.represent = lambda id,row: db.place(id).name if db.place(id) else 'N/A'
db.stock.place_to.represent = lambda id,row: db.place(id).name if db.place(id) else 'N/A'

db.define_table('bom',
                Field('product', db.product),
                Field('name', 'string', length=128, default=T('default')),
                Field('unit', db.unit),
                Field('quantity_of_charge', 'double', notnull=True),
                Field('place_from', db.place),
                Field('place_to', db.place),
                Field('created', 'datetime', writable=False, default=request.now),
                Field('remark', 'text')
                )

db.bom.product.requires = IS_IN_DB(db(db.product.can_be_manufactured==True), db.product.id, '%(name)s')
db.bom.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.bom.place_from.requires = IS_IN_DB(db, db.place.id, '%(name)s')
db.bom.place_to.requires = IS_IN_DB(db, db.place.id, '%(name)s')
db.bom.product.represent = lambda id,row: db.product(id).name
db.bom.unit.represent = lambda id,row: db.unit(id).name
db.bom.place_from.represent = lambda id,row: db.place(id).name
db.bom.place_to.represent = lambda id,row: db.place(id).name

db.define_table('bom_item',
                Field('bom', db.bom),
                Field('product', db.product),
                Field('unit', db.unit),
                Field('quantity', 'double', notnull=True),
                Field('remark', 'text')
                )

db.bom_item.bom.requires = IS_IN_DB(db, db.bom.id)
db.bom_item.product.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.bom_item.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.bom_item.product.represent = lambda id,row: db.product(id).name
db.bom_item.unit.represent = lambda id,row: db.unit(id).name

db.define_table('manufacturing_order',
                Field('product', db.product, label=T('Product')),
                Field('bom', db.bom, label=T('BOM')),
                Field('unit', db.unit, label=T('Unit')),
                Field('planned_date', 'date', notnull=True, requires=IS_DATE(format=('%Y-%m-%d')), label=T('Planned Date')),
                Field('quantity', 'double', notnull=True, label=T('Quantity')),
                Field('place_from', db.place, label=T('Place From')),
                Field('place_to', db.place, label=T('Place To')),
                Field('status', db.waybill_status, writable=False, default=1, label=T('Status')),
                Field('remark', 'text', label=T('Remark'))
                )

db.manufacturing_order.product.requires = IS_IN_DB(db(db.product.can_be_manufactured==True), db.product.id, '%(name)s')
db.manufacturing_order.bom.requires = IS_IN_DB(db, db.bom.id, '%(name)s')
db.manufacturing_order.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.manufacturing_order.place_from.requires = IS_IN_DB(db, db.place.id, '%(name)s')
db.manufacturing_order.place_to.requires = IS_IN_DB(db, db.place.id, '%(name)s')
db.manufacturing_order.product.represent = lambda id,row: db.product(id).name
db.manufacturing_order.bom.represent = lambda id,row: db.bom(id).name
db.manufacturing_order.unit.represent = lambda id,row: db.unit(id).name
db.manufacturing_order.status.requires = IS_IN_DB(db, db.waybill_status.id, '%(name)s')
db.manufacturing_order.status.represent = lambda id,row: db.waybill_status(id).name
db.manufacturing_order.place_from.represent = lambda id,row: db.place(id).name
db.manufacturing_order.place_to.represent = lambda id,row: db.place(id).name


db.define_table('sales_order',
                Field('partner', db.partner, label=T('Partner')),
                Field('place_of_delivery', 'string', length=64),
                Field('worker', db.worker),
                Field('car', db.car),
                Field('delivery_date', 'date', notnull=True, requires=IS_DATE(format=T('%Y-%m-%d')), label=T('Delivery Date')),
                Field('status', db.waybill_status, writable=True, default=1, label=T('Status')),
                Field('remark', 'text', label=T('Remark'))
                )

db.sales_order.partner.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.sales_order.partner.represent = lambda id,row: db.partner(id).name
db.sales_order.worker.requires = IS_IN_DB(db, db.worker.id, '%(name)s')
db.sales_order.worker.represent = lambda id,row: db.worker(id).name
db.sales_order.car.requires = IS_IN_DB(db, db.car.id, '%(plate_number)s')
db.sales_order.car.represent = lambda id,row: db.car(id).plate_number
db.sales_order.status.requires = IS_IN_DB(db, db.waybill_status.id, '%(name)s')
db.sales_order.status.represent = lambda id,row: db.waybill_status(id).name

db.define_table('sales_order_item',
                Field('sales_order', db.sales_order, label=T('Order'), writable=False),
                Field('product', db.product),
                Field('bom', db.bom),
                Field('unit', db.unit),
                Field('quantity', 'double', notnull=True, label=T('Quantity')),
                Field('remark', 'text', label=T('Remark'))
                )

db.sales_order_item.sales_order.requires = IS_IN_DB(db, db.sales_order.id, '%(id)s %(partner)s %(delivery_date)s')
db.sales_order_item.product.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.sales_order_item.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.sales_order_item.product.represent = lambda id,row: db.product(id).name
db.sales_order_item.unit.represent = lambda id,row: db.unit(id).name
db.sales_order_item.quantity.requires = IS_EXPR('value>0')


db.define_table('partner_tour_map',
                Field('tour_name', 'string', length='64', notnull=True, unique=True),
                Field('partner', db.partner)
                )

db.partner_tour_map.partner.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.partner_tour_map.partner.represent = lambda id,row: db.partner(id).name


db.define_table('driver',
                Field('name', 'string', length='64', notnull=True),
                Field('remark', 'text')
                )

db.define_table('daily_tour',
                Field('partner', db.product),
                Field('driver', db.driver),
                Field('date', 'date', default=request.now),
                Field('brutto_income', 'integer', writable=False, default=0),
                Field('net_income', 'integer', writable=False, default=0),
                Field('cash_1', 'integer', writable=False, default=0),
                Field('cash2', 'integer', writable=False, default=0),
                Field('deposit', 'integer', writable=False, default=0),
                Field('rabatt', 'integer', writable=False, default=0),
                Field('delayed_weekly', 'integer', writable=False, default=0),
                Field('delayed_monthly', 'integer', writable=False, default=0),
                Field('remark', 'text')
                )

db.daily_tour.partner.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.daily_tour.partner.represent = lambda id,row: db.partner(id).name
db.daily_tour.driver.requires = IS_IN_DB(db, db.driver.id, '%(name)s')
db.daily_tour.driver.represent = lambda id,row: db.driver(id).name

db.define_table('daily_tour_import_mapping',
                Field('product', db.product, unique=True),
                Field('row_number', 'integer', notnull=True, unique=False),
                Field('remark', 'text')
                )

db.daily_tour_import_mapping.product.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.daily_tour_import_mapping.represent = lambda id,row: db.pproduct(id).name

db.define_table('market',
                Field('name', 'string', length=128, notnull=True),
                Field('remark', 'text', label=T('Remark'))
                )

db.define_table('market_event_owner',
                Field('name', 'string', length=128, notnull=True),
                Field('remark', 'text', label=T('Remark'))
                )

db.define_table('market_event_category',
                Field('name', 'string', length=128, notnull=True),
                Field('tax', 'double', notnull=True, default=27, label=T('Tax (%)')),
                Field('remark', 'text', label=T('Remark'))
                )

db.define_table('market_cassa',
                Field('name', 'string', length=128, notnull=True),
                Field('date', 'date', requires=IS_DATE(format=('%Y-%m-%d')), notnull=True, default=request.now),
                Field('market', db.market),
                Field('event_category', db.market_event_category),
                Field('movement_amount', 'double', notnull=True),
                Field('balance_before', 'integer', notnull=True, writable=False),
                Field('balance_after', 'integer', notnull=True, writable=False),
                Field('event_owner', db.market_event_owner),
                Field('remark', 'text', label=T('Remark'))
                )

db.market_cassa.market.requires = IS_IN_DB(db, db.market.id, '%(name)s')
db.market_cassa.market.represent = lambda id,row: db.market(id).name
db.market_cassa.event_owner.requires = IS_IN_DB(db, db.market_event_owner.id, '%(name)s')
db.market_cassa.event_owner.represent = lambda id,row: db.market_event_owner(id).name
db.market_cassa.event_category.requires = IS_IN_DB(db, db.market_event_category.id, '%(name)s')
db.market_cassa.event_category.represent = lambda id,row: db.market_event_category(id).name

#### defining views ####
db.define_table('v_daily_performance_financial',
                Field('product_id', db.product),
                Field('date_of_production', 'date'),
                Field('place_from', db.place),
                Field('place_to', db.place),
                Field('value_recorded', 'double'),
                migrate=False
                )

db.v_daily_performance_financial.product_id.represent = lambda id,row: db.product(id).name
db.v_daily_performance_financial.place_from.represent = lambda id,row: db.place(id).name
db.v_daily_performance_financial.place_to.represent = lambda id,row: db.place(id).name

db.define_table('v_daily_place_sum_performance_financial',
                Field('date_of_production', 'date'),
                Field('place_from', db.place),
                Field('value_recorded_sum', 'double'),
                Field('additional_value_sum', 'double'),
                migrate=False
                )

db.v_daily_place_sum_performance_financial.place_from.represent = lambda id,row: db.place(id).name

db.define_table('v_daily_sum_performance_financial',
                Field('date_of_production', 'date'),
                Field('value_recorded_sum', 'double'),
                Field('additional_value_sum', 'double'),
                migrate=False
                )

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
