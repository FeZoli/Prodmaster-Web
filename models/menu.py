response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = []

is_general_manager = auth.has_membership('general manager')
is_packaging_registrator = auth.has_membership('packaging registrator')
is_public_market_manager = auth.has_membership('public market manager')

index_menu = [T('Index'),URL('default','index')==URL(),URL('default','index'),[]]
response.menu.append(index_menu)

if is_general_manager:
    basic_data_menu = [T('Basic Data'), True,URL('warehouse','index'),
     [(T('Partners'), True, URL('partners','index')),
      (T('Products'), True, URL('products','index')),
     (T('Product Groups'), True, URL('product_groups','index'))]]
    response.menu.append(basic_data_menu)

if is_general_manager or is_packaging_registrator:
    actual_stock_submenu = []
    if is_general_manager:
        actual_stock_submenu.append([T('Raw Materials'), True, URL('actual_stock','index', vars=dict(group=1))])
    actual_stock_submenu.append([T('Finished Products'), True, URL('actual_stock','get_actual_stock_of_finished_product')])
    actual_stock_submenu.append([T('Unfinished Products'), True, URL('actual_stock','get_actual_stock_of_unfinished_product')])
    actual_stock_submenu.append([T('Packaging Materials'), True, URL('actual_stock','get_actual_stock_of_packaging_material')])
    actual_stock_menu = [T('Actual Stock'), True, URL('actual_stock','index'), actual_stock_submenu]
    warehouse_additional_items = []
    warehouse_additional_items.append(actual_stock_menu)
    if is_general_manager:
        warehouse_additional_items.append([T('Movements'), True, URL('movements','index')])
        warehouse_additional_items.append([T('Waybills'), True, URL('waybills','index')])
        warehouse_additional_items.append([T('Places'), True, URL('places','index')])
    warehouse_menu = [T('Warehouse'), True,URL('warehouse','index'), warehouse_additional_items] #, warehouse_additional_items)
    response.menu.append(warehouse_menu)

if is_general_manager or is_packaging_registrator:
    manufacturing_submenu = []
    if is_general_manager:
        manufacturing_submenu.append((T('Bill of materials'), True, URL('boms','index')))
    manufacturing_submenu.append((T('Manufacturing orders'), True, URL('manufacturing_orders','index')))
    manufacturing_menu = (T('Manufacturing'), True,URL('manufacturing_orders','index'), manufacturing_submenu)
    response.menu.append(manufacturing_menu)

if is_general_manager:
    sales_menu = (T('Sales'), True,URL('sales','index'),
     [(T('Orders'), True, URL('sales_orders','index')),
      (T('Waybills'), True, URL('sales_waybills','index')),
      (T('Daily tour'), True, URL('daily_tour','index'))])
    response.menu.append(sales_menu)

if is_general_manager:
    reports_menu = (T('Reports'), True, URL('reports','index'),
     [(T('Production'), True, URL('production_reports','index'),
      [(T('Daily performance'), True, URL('production_daily_performance_report','index'))]),
       (T('Sales'), True, URL('sales_reports','index')),
       (T('Purchase'), True, URL('purchase_reports','index'),
        [(T('By product'), True, URL('purchase_by_product_report','index'))])
     ])
    response.menu.append(reports_menu)

if is_general_manager:
    maps_menu = (T('Maps'), True, URL('maps','index'),
     [(T('Zoli'), True, URL('where_is_zoli','index'))])
    response.menu.append(maps_menu)

if is_general_manager or is_public_market_manager:
    markets_menu = (T('Markets'), True, URL('markets','index'),
     [(T('Event Categories'), True, URL('market_event_categories','index')),
      (T('Cassa'), True, URL('market_cassa','index'))
     ])
    response.menu.append(markets_menu)
