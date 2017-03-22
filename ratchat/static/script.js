function escape(str) {
	var div = document.createElement('div');
	div.appendChild(document.createTextNode(str));
	return div.innerHTML;
}

function update_chat(message, _cls) {
	var cls = _cls ? _cls : '';
	var p = document.createElement('p');
	p.classList.add(cls);
	p.innerHTML = message;
	$('#chat-window').append(p);
	$('#chat-window').scrollTop($('#chat-window')[0].scrollHeight);
}


$(document).ready(function() {

	/*
	 * SocketIO
	 */

	$('#chat-input').val('').focus();

	var socket = io.connect('http://' + document.domain + ':' + location.port);


	socket.on('recent_messages', function(msg_list) {
		for (var i = 0; i < msg_list.length; i++) {
			update_chat('<span class="username">' + msg_list[i]['username'] 
					+ "</span>" + ": " + msg_list[i]['msg'], 'reg-msg');
		}
	});


	socket.on('chat_message', function(data) {
		var msg_cls = data['username'] === 'server' ? 'server-msg' : 'reg-msg';
		update_chat('<span class="username">' + data['username']
				+ "</span>" + ": " + data['msg'], msg_cls);
	});


	socket.on('private_message', function(data) {
		update_chat(data['sender'] + '->' + data['receiver'] + ': ' + data['msg'],
				'priv-msg');
	});


	socket.on('user_joined', function(joining_user) {
		update_chat(joining_user + " has joined the chat", 'notify-msg');
	});


	socket.on('active_users', function(data) {
		if (data.length) {
			$('#users-window').empty();
			for (var i = 0; i < data.length; i++) {
				$('#users-window').append('<p id="' + data[i] + '">' + data[i] + "</p>");
			}
		}
	});


	$('#input-form').submit(function(e) {
		e.preventDefault(); // prevents form from sending http request
		if ($('#chat-input').val()) {
			socket.emit('chat_message', {
				'msg': $('#chat-input').val(),
			});
		}
		$('#chat-input').val('').focus();
	});
});
