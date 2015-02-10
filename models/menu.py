response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description

index_menu = (T('Index'),URL('default','index')==URL(),URL('default','index'),[])

actual_stock_menu = (T('Actual Stock'), True, URL('actual_stock','index'),
                   [ (T('Raw Materials'), True, URL('actual_stock','index', vars=dict(group=1))),
                     (T('Finished Products'), True, URL('actual_stock','index', vars=dict(group=3))),
                     (T('Unfinished Products'), True, URL('actual_stock','index', vars=dict(group=2))),
                     (T('Packaging Materials'), True, URL('actual_stock','index',vars=dict(group=5)))
                   ])

warehouse_menu = (T('Warehouse'), True,URL('warehouse','index'),
 [ actual_stock_menu,
  (T('Movements'), True, URL('movements','index')),
  (T('Partners'), True, URL('partners','index')),
  (T('Products'), True, URL('products','index')),
  (T('Waybills'), True, URL('waybills','index'))])

manufacturing_menu = (T('Manufacturing'), True,URL('manufacturing','index'),
 [(T('Bill of materials'), True, URL('boms','index')),
  (T('Manufacturing orders'), True, URL('manufacturing_orders','index'))])

sales_menu = (T('Sales'), True,URL('sales','index'),
 [(T('Waybills'), True, URL('sales_waybills','index')),
  (T('Daily tour'), True, URL('daily_tour','index'))])

response.menu = [index_menu,
                 warehouse_menu,
                 manufacturing_menu,
                 sales_menu]
