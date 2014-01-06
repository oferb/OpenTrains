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
	var shapes = [];
	{% for shape in trip.get_shapes %}
		shapes.push([{{shape.shape_pt_lat}},{{shape.shape_pt_lon}}]);
	{% endfor %}
	otMap.createLine(shapes,{
		color: 'red',
		weight : 2
		});
	{% endfor %}
	
}




