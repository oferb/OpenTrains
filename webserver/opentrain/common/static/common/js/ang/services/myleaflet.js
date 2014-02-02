"use strict";

var services = angular.module('my.leaflet', ['my.services']);

services.factory('MyLeaflet', ['MyUtils',
function(MyUtils) {
	return {
		trainIcon : L.icon({
			iconUrl : '/static/common/img/open-train.png',
			iconSize : [26, 26],
		}),
		drawShapes : function(shapes) {
			var that = this;
			var points = shapes.map(function(shape) {
				return [parseFloat(shape.shape_pt_lat), parseFloat(shape.shape_pt_lon)];
			});
			var polyline = that.createLine(null, points, {
				color : '#0000CD',
				weight : 3,
				stroke : true,
			});
			return polyline;
		},
		drawStops : function(stops) {
			var that = this;
			var result = [];
			stops.forEach(function(stop) {
				var text = stop.stop_name;
				var pt = [stop.stop_lat,stop.stop_lon];
				var marker = L.marker(pt, {
					icon : that.trainIcon
				}).bindPopup(text);
				result.push(marker);
			});
			return result;
		},
		findBoundBox : function(points) {
			var initialBox = [[points[0][0], points[0][1]], [points[0][0], points[0][1]]];
			return points.reduce(function(box, p) {
				return [[Math.min(box[0][0], p[0]),
						Math.min(box[0][1], p[1])],
						[Math.max(box[1][0], p[0]),
						Math.max(box[1][1], p[1])]]; 
			}, initialBox);
		},
		showReports : function(map, reports, showConfig) {
			showConfig = showConfig || {};
			var box = showConfig.box;
			var initialPoint = showConfig.initialPoint;
			var that = this;
			var points = [];
			if (initialPoint) {
				points.push(initialPoint);
			}
			reports.forEach(function(r) {
				if (r.loc) {
					points.push([r.loc.lat, r.loc.lon]);
				}
			});
			var polyline = this.createLine(map, points, {
				color : '#0000CD',
				weight : 3,
				stroke : true,
			});
			if (box) {
				map.fitBounds(box);
			};
			reports.forEach(function(report) {
				if (report.loc) {
					var pt = [report.loc.lat, report.loc.lon];
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
				}
			});
		},
		createLine : function(map, points, options) {
			var polyline = L.polyline(points, options);
			if (map != null) {
				polyline.addTo(map);
			};
			return polyline;
		},
	};
}]);
