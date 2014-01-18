from django.core.urlresolvers import reverse
def menu(req):
    menu_items = [#dict(title="Search Between",name = 'gtfs:search-between'),
                  dict(title="Search In",name = 'gtfs:search-in'),
                  #dict(title="Show labels",name = 'analysis:show-labels'),
                  dict(title="Show Reports",name = 'analysis:select-device-reports'),
                  dict(title="Report Details",name='analysis:report-details')
                  ]
    for mi in menu_items:
        if req.path == reverse(mi['name']):
            mi['active'] = True
        else:
            mi['active'] = False
    return dict(menu_items = menu_items)



    
    
    