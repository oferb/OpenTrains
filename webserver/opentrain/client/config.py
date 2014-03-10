def get_client_config():
	prefs = {}
	prefs['RECORD_BATCH_SIZE'] = 5
	prefs['TRAIN_INDICATION_TTL'] = 1 * 1 * 30 * 1000
	prefs['LOCATION_API_UPDATE_INTERVAL'] = 5 * 1000
	prefs['MODE_TRAIN_WIFI_FOUND_PERIOD'] = 1*15*1000
	prefs['MODE_TRAIN_WIFI_SCANNIG_PERIOD'] = 5*60*1000;
	prefs['WIFI_MIN_UPDATE_TIME'] = 1000
	prefs['WIFI_MAX_UPDATE_PERIOD'] = 1000
	return prefs
