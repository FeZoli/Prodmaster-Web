# -*- coding: utf-8 -*-

from gluon import current

from datetime import timedelta

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
request.requires_https()

#if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
db = DAL('mysql://minux:nemerdekel@localhost/foodmaster', migrate=True)

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

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

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


db.define_table('product_group',
                Field('name', 'string', length=32, unique=True, notnull=True),
                Field('remark', 'text')
                )


db.define_table('product',
                Field('name', 'string', length=64, unique=True, notnull=True),
                Field('unit', db.unit),
                Field('product_group', db.product_group),
                Field('can_be_purchased', 'boolean', notnull=True),
                Field('can_be_sold', 'boolean', notnull=True),
                Field('can_be_manufactured', 'boolean', notnull=True),
                Field('unit_price', 'double', notnull=True),
                Field('best_before_days', 'integer'),
                Field('remark', 'text')
                )

db.product.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.product.product_group.represent = lambda id,row: db.product_group(id).name
db.product.unit.represent = lambda id,row: db.unit(id).name
db.product.product_group.requires = IS_IN_DB(db, db.product_group.id, '%(name)s')

db.define_table('waybill_status',
                Field('name', 'string', length=16, notnull=True),
                Field('remark', 'text')
                )

db.define_table('waybill',
                Field('partner', db.partner),
                Field('date_of_delivery', 'date', notnull=True),
                Field('reference', 'string', length=16),
                Field('status', db.waybill_status, writable=False, notnull=True, default=1),
                Field('is_delivery', 'boolean', notnull=True, default=True, writable=False, readable=False),
                Field('remark', 'text')
                )

db.waybill.partner.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.waybill.partner.represent = lambda id,row: db.partner(id).name
db.waybill.status.requires = IS_IN_DB(db, db.waybill_status.id, '%(name)s')
db.waybill.status.represent = lambda id,row: db.waybill_status(id).name

db.define_table('waybill_item',
                Field('waybill', db.waybill),
                Field('product', db.product),
                Field('product_name', 'string', length=32, notnull=True),
                Field('unit', db.unit),
                Field('quantity', 'double', notnull=True),
                Field('unit_price_recorded', 'double', notnull=True),
                Field('serial_id', 'string', length=32),
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

db.define_table('stock',
                Field('product_id', db.product),
                Field('product_name', 'string', length=32, notnull=True),
                Field('unit', db.unit),
                Field('quantity_change', 'double', notnull=True),
                Field('new_quantity', 'double', writable=False, notnull=True),
                Field('source_partner_id', db.partner),
                Field('source_partner_name', 'string', length=32),
                Field('source_doc_id', 'integer'),
                Field('source_reference', 'string', length=16),
                Field('target_partner_id', db.partner),
                Field('target_partner_name', 'string', length=32),
                Field('date_of_delivery', 'date', default=request.now),
                Field('serial_id', 'string'),
                Field('best_before_date', 'date'),
                Field('unit_price_recorded', 'double', notnull=True),
                Field('value_recorded', 'double', notnull=True),
                Field('created', 'datetime', writable=False, default=request.now),
                Field('remark', 'text')
                )

db.stock.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.stock.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.stock.source_partner_id.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.stock.target_partner_id.requires = IS_IN_DB(db, db.partner.id, '%(name)s')
db.stock.date_of_delivery.requires = IS_DATE(format=('%Y-%m-%d'))
db.stock.unit.represent = lambda id,row: db.unit(id).name

db.define_table('bom',
                Field('product', db.product),
                Field('unit', db.unit),
                Field('quantity_of_charge', 'double', notnull=True),
                Field('created', 'datetime', writable=False, default=request.now),
                Field('remark', 'text')
                )

db.bom.product.requires = IS_IN_DB(db(db.product.can_be_manufactured==True), db.product.id, '%(name)s')
db.bom.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.bom.product.represent = lambda id,row: db.product(id).name
db.bom.unit.represent = lambda id,row: db.unit(id).name

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
                Field('product', db.product),
                Field('unit', db.unit),
                Field('planned_date', 'date', notnull=True, requires=IS_DATE(format=('%Y-%m-%d'))),
                Field('quantity', 'double', notnull=True),
                Field('status', db.waybill_status, writable=False, default=1),
                Field('remark', 'text')
                )

db.manufacturing_order.product.requires = IS_IN_DB(db(db.product.can_be_manufactured==True), db.product.id, '%(name)s')
db.manufacturing_order.unit.requires = IS_IN_DB(db, db.unit.id, '%(name)s')
db.manufacturing_order.product.represent = lambda id,row: db.product(id).name
db.manufacturing_order.unit.represent = lambda id,row: db.unit(id).name
db.manufacturing_order.status.requires = IS_IN_DB(db, db.waybill_status.id, '%(name)s')
db.manufacturing_order.status.represent = lambda id,row: db.waybill_status(id).name

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
