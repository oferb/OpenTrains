{% load staticfiles %}
{% load ot_filters %}
function initMap() {
	var otMap = otCreateMap('tripMap',{
		lat : {{zoom_stop.stop_lat}},
		lon : {{zoom_stop.stop_lon}},
		zoomStopId : {{zoom_stop.stop_id}}
	});
	var shapes = {{trip.get_shapes | shapes_to_points }};
	otMap.createLineAndZoom(shapes,{
		color: 'red',
		weight : 2
	});
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






