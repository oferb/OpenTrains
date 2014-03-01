"use strict";

function GlobalSearchResults() {
	var that = this;
	this.all = [];
	this.state = true;
	this.clicked = function() {
		this.state = !this.state;
		this.refresh();
	};
	this.refresh = function() {
		if (this.state) {
			this.btn.html('<span class="glyphicon glyphicon-minus-sign"></span>');
		} else {
			this.btn.html('<span class="glyphicon glyphicon-plus-sign"></span>');
		}
		var state  = this.state;
		this.all.forEach(function(it) {
			it.setState(state);
		});
	};
	this.init = function() {
		this.btn = $("#trip_details_button_global");
		this.btn.click(function() {
			that.clicked();
		});
		this.refresh();
	};
}

window.GLOBAL_SEARCH_RESULTS = new GlobalSearchResults();

function SearchResult(index) {
	var that = this;
	this.index = index;
	this.state = true;
	this.btn = $("#trip_details_button_" + index);
	this.details = $("#trip_details_" + index);
	this.btn.click(function() {
		that.clicked();
	});
	this.clicked = function() {
		this.setState(!this.state);
	};
	this.setState = function(state) {
		this.state = state;
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
	window.GLOBAL_SEARCH_RESULTS.all.push(this);
}

