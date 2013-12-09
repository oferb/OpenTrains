"use strict";

function SearchResult(index) {
	console.log("index = " + index);
	var that = this;
	this.index = index;
	this.state = true;
	this.btn = $("#trip_details_button_" + index);
	this.details = $("#trip_details_" + index);
	this.btn.click(function() {
		that.clicked();
	});
	this.clicked = function() {
		this.state = !this.state;
		this.refresh();
	};
	this.refresh = function() {
		if (this.state) {
			this.details.addClass('show');
			this.details.removeClass('hidden');
			this.btn.html('<span class="glyphicon glyphicon-minus-sign"></span>');
		} else {
			this.details.addClass('hidden');
			this.details.removeClass('show');
			this.btn.html('<span class="glyphicon glyphicon-plus-sign"></span>');
		}
	};
	this.refresh();
}

