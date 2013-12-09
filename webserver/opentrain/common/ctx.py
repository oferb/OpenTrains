def get_global_context(active):
    menu_items = [dict(title="Search Between",name = 'gtfs:search-between'),
              dict(title="Search In",name = 'gtfs:search-in'),
            ]
    for item in menu_items:
        if item['name'] == active:
            item['active'] = True
        else:
            item['active'] = False
    return dict(ot_global = dict(menu_items = menu_items))
    
    
    