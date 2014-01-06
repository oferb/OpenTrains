{% load staticfiles %}
{% load ot_filters %}
function initMap() {
	var center       = getLonLat({{zoom_stop.stop_lon}}, {{ zoom_stop.stop_lat }});
	var otIcon = getOtIcon();
	var popups = [];
	var markers = new OpenLayers.Layer.Markers("Markers");
	var points = [];
	{% for shape in trip.get_shapes %}
		points.push(getPoint({{shape.shape_pt_lon}},{{shape.shape_pt_lat}}));
	{% endfor %}
	//var otIcon = new OpenLayers.Icon("http://www.openlayers.org/dev/img/marker.png",{w:26,h:26});
	{%for stop_time in trip.get_stop_times%}
	{
		var pos = getLonLat({{stop_time.stop.stop_lon}}, {{stop_time.stop.stop_lat}});
		var marker = new OpenLayers.Marker(pos, otIcon.clone());	
		markers.addMarker(marker);
		var popup = new OpenLayers.Popup.FramedCloud("stop_id_{{stop_time.stop.stop_id}}", pos.clone(), null, 'Stop {{stop_time.stop.stop_name}}<br/>@ {{stop_time.arrival_time | denorm_time}}', null, true);
		popups.push(popup);
	}
	{% endfor %}
	
	// add the points
	var lineLayer = new OpenLayers.Layer.Vector("Line Layer");                                                          
	var line = new OpenLayers.Geometry.LineString(points);

	var style = { 
	  strokeColor: '#0000ff', 
	  strokeOpacity: 0.5,
	  strokeWidth: 5
	};

	var lineFeature = new OpenLayers.Feature.Vector(line, null, style);
	lineLayer.addFeatures([lineFeature]);
	
	
	
	var map = new OpenLayers.Map('tripMap');
	map.addLayer(new OpenLayers.Layer.OSM());
	//popups.forEach(function(it) {
	//	map.addPopup(it);
	//});
	map.addLayer(markers);
	map.addLayer(lineLayer);
	map.setCenter(center , 10);
}



