import codecs
import re
import datetime
from traindata.models import TrainData

LINE_RE = re.compile(r'^\s*' +
                     r'(?P<date>\d+)\s+"' +
                     r'(?P<train_num>\d+)"\s+' +
                     r'(?P<exp_arrival>\d+)\s+' +
                     r'(?P<actual_arrival>\d+)\s+' +
                     r'(?P<exp_departure>\d+)\s+' +
                     r'(?P<actual_departure>\d+)\s+' +
                     r'(?P<raw_stop_id>\d+)\s+' +
                     r'"(?P<raw_stop_name>.*)"\s*$')
    
class TrainTrip():
    def __init__(self,date,train_num):
        self.date = date
        self.train_num = train_num
        self.times = TrainData.objects.filter(date=date,train_num=train_num).order_by('exp_arrival')
        
    def print_nice(self):
        print '--------------------------------------------------'
        print '%s @%s' % (self.train_num,self.date)
        for t in self.times:
            print '%5d %-30s exp: %4s -> %4s act: %4s -> %4s' % (t.line,
                                                                 t.stop.stop_name,
                                                                 t.actual_arrival,
                                                                 t.actual_departure,
                                                                 t.exp_arrival,
                                                                 t.exp_departure)
                                           

                     
def _parse_date(date):
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
    return datetime.date(year=year,month=month,day=day)
                     
def get_stop_ids():
    import gtfs.models
    stop_ids = set(gtfs.models.Stop.objects.all().values_list('stop_id',flat=True))
    return stop_ids
                     
def read_file(fname):
    stop_ids = get_stop_ids()
    with codecs.open(fname,encoding="windows-1255") as fh:
        tds = []
        for idx,line in enumerate(fh):
            m = LINE_RE.match(line)
            if m:
                td = TrainData()
                gd = m.groupdict()
                td.date = _parse_date(gd['date'])
                td.train_num = gd['train_num']
                td.exp_arrival = gd['exp_arrival']
                td.actual_arrival = gd['actual_arrival']
                td.exp_departure = gd['exp_departure']
                td.actual_departure = gd['actual_departure']
                td.raw_stop_id = int(gd['raw_stop_id'])
                td.raw_stop_name = gd['raw_stop_name']
                td.file = fname
                td.line = idx
                if td.raw_stop_id in stop_ids:
                    td.stop_id = td.raw_stop_id
                    tds.append(td)
            else:
                raise Exception('Illegal line %d at %s' % (idx,fname))
    print 'Created %d entries. Saving to db' % (len(tds))
    TrainData.objects.bulk_create(tds)
    print 'Saved'
    
def read_year_month(year,month):
    """ read file of month/year """
    read_file('traindata/data/%02d_%s.txt' % (month,year))
    
def get_trains_for_day(d):
    """ return all train nums for specific day """
    trains = TrainData.objects.filter(date=d).values_list('train_num',flat=True).distinct()
    return trains

