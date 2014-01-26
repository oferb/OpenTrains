"use strict";

var services = angular.module('my.leaflet', ['my.services']);

services.factory('MyLeaflet', ['MyUtils',
function(MyUtils) {
	return {
		trainIcon : L.icon({
			iconUrl : '/static/common/img/open-train.png',
			iconSize : [26, 26]
		}),
		showReports : function(map, reports, toZoom) {
			var that = this;
			var points = [];
			var result = {
				noLocCount : 0,
				locCount : 0,
			};
			reports.forEach(function(r) {
				if (r.loc) {
					points.push([r.loc.lat, r.loc.lon]);
				} 
			});
			var polyline = this.createLine(map, points, toZoom, {
				color : '#0000CD',
				weight : 3,
				stroke : true,
			});
			points.forEach(function(pt, index) {
				var report = reports[index];
				var text = '<a href="/analysis/report-details/?report_id=' + report.id + '">' + report.id + '</a><br/>' + MyUtils.toHourMinSec(report.timestamp);
				if (report.is_station) {
					L.marker(pt, {
						icon : that.trainIcon
					}).addTo(map).bindPopup(text);
				} else {
					L.circleMarker(pt, {
						radius : 5,
						color : '#0000CD',
						fill : true,
					}).addTo(map).bindPopup(text);
				}
			});
			return result;
		},
		createLine : function(map, points, toZoom, options) {
			console.log('In createLine toZoom = ' + toZoom);
			var polyline = L.polyline(points, options).addTo(map);
			if (toZoom) {
				map.fitBounds(polyline.getBounds());
			}
			return polyline;
		},
	};
}]);
