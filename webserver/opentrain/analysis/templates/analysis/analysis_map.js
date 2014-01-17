{% load staticfiles %}
{% load ot_filters %}
function initMap() {
	var otMap = otCreateMap('map',
	{
		lat : {{center.lat}},
		lon : {{center.lon}}
	});
	{%for report in reports %}
		otMap.createReportDot({ 
								lat : {{report.my_loc.lat}},
								lon : {{report.my_loc.lon}},
								});
	{% endfor %} 
}






