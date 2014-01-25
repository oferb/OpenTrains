{% load staticfiles %}
{% load ot_filters %}
function initMap() {
	var otMap = otCreateMap('map',
	{
		lat : {{center.lat}},
		lon : {{center.lon}}
	});
	var reports = [];
	{%for report in reports %}
		reports.push({
			id : {{report.id}},
			lat : {{report.my_loc.lat}},
			lon : {{report.my_loc.lon}}, 
			is_station : {{report.is_station | truefalse }},
			timestamp : new Date('{{report.timestamp.isoformat}}'),
		});
	{% endfor %}
	otMap.createReportsLine(reports);
}




