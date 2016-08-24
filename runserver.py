from ratchat import app, socketio

if __name__ == '__main__':
    #app.run(debug=True)
    app.config['TESTING'] = False
    socketio.run(app, host='0.0.0.0')
