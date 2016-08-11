function escape(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

$(document).ready( function() {

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    //console.log("Doc domain: " + document.domain + " location.port " + location.port);
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });

    socket.on('chat_message', function(data) {
        $('#chat_window').append(data['msg'] + "<br>");
        $('#chat_window').scrollTop($('#chat_window')[0].scrollHeight);
        $('#chat_input').val('').focus();
    });

    $('#input_form').submit( function(e) {
        e.preventDefault(); // prevents form from sending http request

        socket.emit('chat_message', { msg: escape($('#chat_input').val())});

        //$('#chat_window').append( escape($('#chat_input').val()) + "<br>");
        //$("#chat_window").scrollTop($("#chat_window")[0].scrollHeight);
        //$('#chat_input').val('').focus();
    });

});
