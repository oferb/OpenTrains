var myFilters = angular.module('my.filters',[]);

myFilters.filter('filterCount',function() {
	return function(input) {
		if ( input > 0) {
			return '(' + input +')';
		} else {
			return '';
		}
	};
});

myFilters.filter('yesNo',function() {
	return function(input) {
	    if (input) {
		return 'Yes';
	    } else {
		return 'No';
	    }
	};
});

myFilters.filter('splitn',function() {
	return function(input) {
		return input.split(/\n/g);
	};
});

myFilters.filter('igDate',function() {
	return function(input) {
		return new Date(1000*input);
	};
});

myFilters.filter('parseDate',function() {
	return function(str) {
		return new Date(str);
	};
});

myFilters.filter('toString',function() {
	return function(input) {
		return input.toString();
	};
});

myFilters.filter('joinList',function() {
	return function(input) {
		if (!input) {
			return '';
		};
		return input.join(',');
	};
});

myFilters.filter('blankIfNull',function() {
	return function(input) {
		if (!input) {
			return '';
		}
		return input;
	};
});

myFilters.filter('spaceList',function() {
	return function(input) {
		if (!input) {
			return '';
		}
		return input.join(" ");
	};
});

myFilters.filter('spaceListParen',function() {
	return function(input) {
		if (!input) {
			return '';
		}
	    input = input.map(function(it) {
		return '"' + it + '"';
	    });
		return input.join(" ");
	};
});

myFilters.filter('ago',function() {
	return function(input) {
		// pass null for the current time
		var delta = {
				printUnitsPlural : function(num,unit) {
					if (num > 1) {
						return num + ' ' + unit + 's';
					} else {
						return num + ' ' + unit; 
					};
				}
		};
		var early = new Date(input);
		var late = new Date();
		var secsLeft = Math.floor((late.getTime() - early.getTime()) / 1000);
		delta.days = Math.floor(secsLeft / (60 * 60 * 24));
		secsLeft = secsLeft - delta.days * 60 * 60 * 24;
		delta.hours = Math.floor(secsLeft / (60 * 60));
		secsLeft = secsLeft - delta.hours * 60 * 60;
		delta.minutes = Math.floor(secsLeft / 60);
		delta.seconds = secsLeft - delta.minutes * 60;

		if (delta.days > 0) {
			return delta.printUnitsPlural(delta.days, 'day') + ' ago';
		}
		// if in hours, we return hours + minutes
		if (delta.hours > 0) {
			return delta.printUnitsPlural(delta.hours, 'hour') + ' and '
					+ delta.printUnitsPlural(delta.minutes, 'minute') + ' ago';
		}
		if (delta.minutes > 0) {
			return delta.printUnitsPlural(delta.minutes, 'min') + ' ago';
		}
		if (delta.seconds >= 0) {
			return delta.printUnitsPlural(delta.seconds, 'second') + ' ago';
		}
		return 'sometime...';
	};
});

myFilters.filter('denormalTime',function() {
	return function(value,withSeconds) {
		var s = value % 60;
    	var value = value - s;
    	var value = (value - s)/ 60;
    	var m = value % 60;
    	var h = (value - m) / 60;
    	h = h < 10 ? '0' + h : h;
    	m = m < 10 ? '0' + m : m;
    	s = s < 10 ? '0' + s : s;
    	if (withSeconds) {
    		return h + ':' + m + ':' + s;
    	} else {
    		return h + ':' + m;
    	} 
	};
});

myFilters.filter('newlines', function () {
    return function(text) {
        return text.replace(/\n/g, '<br/>');
    };
});

myFilters.filter('noHTML', function () {
    return function(text) {
        return text
                .replace(/&/g, '&amp;')
                .replace(/>/g, '&gt;')
                .replace(/</g, '&lt;');
    };
});

myFilters.filter('show2',function() {
	return function(text) {
		return text.substring(0,20);		
	};
});

myFilters.filter('show50',function() {
	return function(text) {
		if (text.length > 50) {
			return text.substring(0,50) + '...';
		} else {
			return text;
		}	
	};
});

myFilters.filter('reverse',function() {
	return function(arr) {
		if (arr) {
			return arr.slice().reverse();
		} else {
			return arr;
		}
	};
});

myFilters.filter('trans',function() {
	return function(w) {
		var res = gettext(w);
		//if (res == w) {
		//	console.log('ugettext_noop("' + res + '")');
		//}
		return res;
	};
});



