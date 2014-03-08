from django.core.urlresolvers import reverse

def menu(req):
    menu_items = [dict(title="Search In",name = 'gtfs:search-in'),
                  dict(title="Device Reports",name = 'analysis:device-reports'),
                  dict(title="Live Trains",name = 'analysis:live-trips'),
                  dict(title="Report Details",name='analysis:report-details'),
                  dict(title="API",name='ot_api:show_docs')
                  ]
    for mi in menu_items:
        if req.path == reverse(mi['name']):
            mi['active'] = True
        else:
            mi['active'] = False
    return dict(menu_items = menu_items)



    
    
    