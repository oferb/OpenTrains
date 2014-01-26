var directives = angular.module('my.directives', []);

directives.directive('fileUpload', function() {
	return {
		scope : true, // create a new scope
		link : function(scope, el, attrs) {
			var name = attrs.name;
			el.bind('change', function(event) {
				var files = event.target.files;
				scope.fileSelected(name, files[0]);
			});
		}
	};
});

