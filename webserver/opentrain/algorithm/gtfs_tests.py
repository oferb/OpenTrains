import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
from unittest import TestCase
import gtfs.models
import unittest
import numpy as np

def get_field(services, name):
    service_ids = services.all().values_list(name)
    service_ids = [x[0] for x in service_ids]
    return service_ids

class gtfs_test(TestCase):
    
    def setUp(self):
        self.services = gtfs.models.Service.objects.all()
        services = self.services
        self.service_ids = get_field(services, 'service_id')
        self.service_sundays = np.array(get_field(services, 'sunday'))+0
        self.service_mondays = np.array(get_field(services, 'monday'))+0
        self.service_tuesdays = np.array(get_field(services, 'tuesday'))+0
        self.service_wednesdays = np.array(get_field(services, 'wednesday'))+0
        self.service_thursdays = np.array(get_field(services, 'thursday'))+0
        self.service_fridays = np.array(get_field(services, 'friday'))+0
        self.service_saturdays = np.array(get_field(services, 'saturday'))+0
        self.service_start_dates = get_field(services, 'start_date')
        self.service_end_dates = get_field(services, 'end_date')    
        
    
    def test_is_every_service_different_weekday(self):
        service_sum_days = self.service_sundays+self.service_mondays+self.service_tuesdays+self.service_wednesdays+self.service_thursdays+self.service_fridays+self.service_saturdays
        is_every_service_different_weekday = np.all(service_sum_days == 1)
        self.assertTrue(is_every_service_different_weekday)
        
    
    def is_date_fits_weekday(self, weekdays, weekday):
        check = True
        weekday_inds = np.where(weekdays)[0]
        for i in weekday_inds:
            if not self.service_start_dates[i].isoweekday() == weekday:
                print('%s is on day %d, not on day %d' % (self.service_start_dates[i], self.service_start_dates[i].isoweekday(), weekday))
                check = False
    
        return check
    
    def test_is_all_dates_fit_weekdays(self):
        res = np.zeros(7)
        res[0] = self.is_date_fits_weekday(self.service_sundays, 7)
        res[1] = self.is_date_fits_weekday(self.service_mondays, 1)
        res[2] = self.is_date_fits_weekday(self.service_tuesdays, 2)
        res[3] = self.is_date_fits_weekday(self.service_wednesdays, 3)
        res[4] = self.is_date_fits_weekday(self.service_thursdays, 4)
        res[5] = self.is_date_fits_weekday(self.service_fridays, 5)
        res[6] = self.is_date_fits_weekday(self.service_saturdays, 6)
        res = res == 1
        self.assertTrue(np.all(res))


    def test_is_start_and_end_dates_the_same(self):
        check = True
        for dates in zip(self.service_start_dates, self.service_end_dates):
            if dates[0] != dates[1]:
                print('start date %s and end date %s are not the same' % (dates[0], dates[1]))
                check = False
        self.assertTrue(check)
    
    #def setup_func():
    #    "set up test fixtures"
    
    #def teardown_func():
    #    "tear down test fixtures"
    
    #@with_setup(setup_func, teardown_func)
    
if __name__ == '__main__':
    unittest.main()