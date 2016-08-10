function escape(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

$(document).ready( function() {

    $('#input_form').submit( function(e) {
        e.preventDefault(); // prevents form from sending http request
        $('#chat_window').append( escape($('#chat_input').val()) + "<br>");
        $('#chat_input').val('').focus();
    });

});
