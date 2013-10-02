$(function() {
	$("#login-form").submit(function(e) {
		// lock fields
		$("#login-form button[type='submit']").button('loading');
		$("#username").attr('readonly', true);
		$("#password").attr('readonly', true);
		// send request
		$.post("", {
			username: $("#username").val(),
			password: $("#password").val()
		}, function(data) {
			// unlock fields
		});
		e.preventDefault();
	});
});
