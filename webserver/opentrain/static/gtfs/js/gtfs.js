"use strict";

function SearchResult() {
	var that = this;
	this.ready = function() {
		this.details = $("#trip-details-in-result");
		this.detailsButton = $("#trip-details-in-result-toggle");
		this.detailsOn = false;
		this.refresh();
		this.detailsButton.click(function() {
			that.detailsOn = !that.detailsOn;
			that.refresh();
		});
	};
	this.refresh = function() {
		if (this.detailsOn) {
			this.details.removeClass("hidden");
			this.details.addClass("show");
		} else {
			this.details.removeClass("hidden");
			this.details.addClass("show");
		};
	};
}


$(document).ready(function() {
	var seachResult = SearchResult();
	seachResult.ready();
});
