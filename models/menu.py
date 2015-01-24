response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Index'),URL('default','index')==URL(),URL('default','index'),[]),

(T('Warehouse'), True,URL('warehouse','index'),
 [(T('Actual Stock'), True, URL('actual_stock','index')),
  (T('Movements'), True, URL('movements','index')),
  (T('Partners'), True, URL('partners','index')),
  (T('Products'), True, URL('products','index')),
  (T('Waybills'), True, URL('waybills','index'))]),

(T('Manufacturing'), True,URL('manufacturing','index'),
 [(T('Bill of materials'), True, URL('boms','index')),
  (T('Manufacturing orders'), True, URL('manufacturing_orders','index'))]),

(T('Sales'), True,URL('sales','index'),
 [(T('Waybills'), True, URL('sales_waybills','index')),
  (T('Daily tour'), True, URL('daily_tour','index'))])
]
