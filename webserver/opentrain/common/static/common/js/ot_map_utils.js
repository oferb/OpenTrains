// utility functions for open layers
"use strict";

function MapWrapper() {
	this.trainIcon = L.icon({
		iconUrl : '/static/common/img/open-train.png',
		iconSize : [26, 26]
	});
	this.createTrainMarker = function(stop) {
		var marker = L.marker([stop.lat, stop.lon], {
			icon : this.trainIcon
		}).addTo(this.map);
		var popup = marker.bindPopup('(' + stop.seqId + ') ' + gettext(stop.name) + "<br/>@" + stop.time);
		if (stop.stopId == this.zoomStopId) {
			popup.openPopup();
		}
	};
	this.createReportsLine = function(reports) {
		var points = [];
		reports.forEach(function(r) {
			points.push([r.loc.lat, r.loc.lon]);
		});
		var that = this;
		var polyline = this.createLineAndZoom(points, {
			color : '#0000CD',
			weight : 3,
			stroke : true,
		});
		points.forEach(function(pt, index) {
			var report = reports[index];
			var text = '<a href="/analysis/report-details/?report_id=' + report.id + '">' + report.id + '</a><br/>';// + toHourMinSec(report.timestamp);
			if (/*report.is_station*/false) {
				L.marker(pt, {
					icon : that.trainIcon
				}).addTo(that.map).bindPopup(text);
			} else {
				L.circleMarker(pt, {
					radius : 5,
					color : '#0000CD',
					fill : true,
				}).addTo(that.map).bindPopup(text);
			}
		});

	};
	this.createLine = function(points, options) {
		var polyline = L.polyline(points, options).addTo(this.map);
		return polyline;
	};
	this.createLineAndZoom = function(points, options) {
		var polyline = this.createLine(points, options);
		this.map.fitBounds(polyline.getBounds());
		return polyline;
	};
	this.setDefaultZoom = function() {
		this.map.setView(this.center, 13);
	};
}

function otCreateMap(mapDiv, options) {
	options = options || {};
	var map = L.map(mapDiv);
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom : 22,
		attribution : 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>'
	}).addTo(map);
	var result = new MapWrapper();
	if (options.zoomStopId) {
		result.zoomStopId = options.zoomStopId;
	}
	result.map = map;
	result.center = [options.lat, options.lon];
	return result;
}


