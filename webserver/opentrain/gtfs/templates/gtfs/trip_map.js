{% load staticfiles %}
{% load ot_filters %}
function initMap() {
	var otMap = otCreateMap('tripMap',{{zoom_stop.stop_lat}},{{zoom_stop.stop_lon}},{{zoom_stop.stop_id}});
	{%for stop_time in trip.get_stop_times%}
		otMap.createTrainMarker({ 
								lat : {{stop_time.stop.stop_lat}},
								lon : {{stop_time.stop.stop_lon}},
								name : "{{stop_time.stop.stop_name}}",
								time : "{{stop_time.arrival_time | denorm_time}}",
								stopId : {{stop_time.stop.stop_id}},
								seqId : {{stop_time.stop_sequence}}
								});
	{% endfor %}
	
}




