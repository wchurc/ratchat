function escape(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

function update_chat(message) {
  $('#chat_window').append(message + "<br>");
  $('#chat_window').scrollTop($('#chat_window')[0].scrollHeight);
}

var username = "new user";

$(document).ready( function() {

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    //console.log("Doc domain: " + document.domain + " location.port " + location.port);
    socket.on('connect', function() {
        socket.emit('connected' ,{data: 'I\'m connected!'});
    });

    socket.on('chat_message', function(data) {
        update_chat(data['username'] + ": " + data['msg']);
        $('#chat_input').val('').focus();
    });

    socket.on('user_joined', function(data) {
      update_chat(data);
    });

    socket.on('assign_username', function(data) {
      username = data['username'];
      update_chat('You have joined the chat as ' + username);
    });

    $('#input_form').submit( function(e) {
        e.preventDefault(); // prevents form from sending http request

        socket.emit('chat_message', { 
          'msg': escape($('#chat_input').val()),
          'username': username
        });

        //$('#chat_window').append( escape($('#chat_input').val()) + "<br>");
        //$("#chat_window").scrollTop($("#chat_window")[0].scrollHeight);
        //$('#chat_input').val('').focus();
    });

});
