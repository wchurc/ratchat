function escape(str) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function update_chat(message) {
  $('#chat_window').append("<p>" + message + "</p>");
  $('#chat_window').scrollTop($('#chat_window')[0].scrollHeight);
}


$(document).ready( function() {

  $('#chat_input').val('').focus();  

  var socket = io.connect('http://' + document.domain + ':' + location.port);


  socket.on('recent_messages', function(msg_list) {
    for (var i = 0; i < msg_list.length; i++) {
      update_chat(msg_list[i]['username'] + ": " + msg_list[i]['msg']);
    }
  });


  socket.on('chat_message', function(data) {
    update_chat(data['username'] + ": " + data['msg']);
  });

    
  socket.on('user_joined', function(joining_user) {
    update_chat(joining_user + " has joined the chat");
    if ( $("#" + joining_user.replace(/ /g,'')).length == 0 ) {
      $('#chat_users').append('<p id="' + joining_user.replace(/ /g, '') + '">' + joining_user + "</p>");
    }
  });


  socket.on('active_users', function(data) {
    if (data.length) {
      $('#chat_users').val('');
      for (var i = 0; i < data.length; i++) {
        if ($("#" + data[i].replace(/ /g,'')).length == 0) {
          $('#chat_users').append('<p id="' + data[i].replace(/ /g,'') + '">' + data[i] + "</p>");
        }
      }
    }
  });


  $('#input_form').submit( function(e) {
      e.preventDefault(); // prevents form from sending http request
      if ($('#chat_input').val()) {
        socket.emit('chat_message', { 
          'msg': escape($('#chat_input').val()),
        });
        $('#chat_input').val('').focus();
      }
  });

});
