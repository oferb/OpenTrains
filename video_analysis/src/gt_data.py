import datetime as dt
from enums import Directions

def get_gt(experiment_id):
    return {
        'webcam2': webcam2_gt(),
        'webcam3': webcam3_gt(),
        }.get(experiment_id, None)

def webcam2_gt():
    train_times = []
    train_times.append([dt.datetime(2013, 11, 13, 6, 13), Directions.NORTH])
    train_times.append([dt.datetime(2013, 11, 13, 6, 30), Directions.NORTH])
    train_times.append([dt.datetime(2013, 11, 13, 6, 44), Directions.SOUTH])
    train_times.append([dt.datetime(2013, 11, 13, 6, 55), Directions.SOUTH])
    train_times.append([dt.datetime(2013, 11, 13, 7, 13), Directions.NORTH])
    train_times.append([dt.datetime(2013, 11, 13, 7, 30), Directions.NORTH])
    train_times.append([dt.datetime(2013, 11, 13, 7, 30), Directions.SOUTH])
    train_times.append([dt.datetime(2013, 11, 13, 7, 50), Directions.SOUTH])
    train_times.append([dt.datetime(2013, 11, 13, 7, 55), Directions.NORTH])
    return train_times

def webcam3_gt():
    train_times = webcam2_gt()
    for i in xrange(len(train_times)):
        train_times[i][0] = train_times[i][0].replace(day=17)
    
    train_times.append([dt.datetime(2013, 11, 17, 8, 13), Directions.SOUTH])
    train_times.append([dt.datetime(2013, 11, 17, 8, 15), Directions.NORTH])
    train_times.append([dt.datetime(2013, 11, 17, 8, 30), Directions.SOUTH])
    train_times.append([dt.datetime(2013, 11, 17, 8, 30), Directions.NORTH])
    return train_times

