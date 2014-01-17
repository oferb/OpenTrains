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
			lat : {{report.my_loc.lat}},
			lon : {{report.my_loc.lon}}, 
			timestamp : new Date('{{report.timestamp.isoformat}}'),
		});
	{% endfor %}
	otMap.createReportsLine(reports);
}

var mapmargin = 200;
$(window).on("resize", resize);
resize();
function resize(){
	var height = ($(window).height() - 20 - $("#map").offset().top);
	console.log(height);
    $('#map').css("height", height);    
    $('#map').css("margin-top",20);
}




