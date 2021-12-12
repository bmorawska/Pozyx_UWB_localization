var express = require('express');
var socket = require('socket.io');

var app = express();
var server = app.listen(3000);

app.use(express.static('public'));

console.log('My socket server is running.')

var io = socket(server, {
    cors: {
        origin: "http://localhost:3000",
        methods: ["GET", "POST"],
        credentials: true,
    },
});


io.sockets.on('connection', newConnection);

function newConnection(socket) {
    console.log('new connection: ' + socket.id);

    socket.on('position', mouseMsg);
    function mouseMsg(data) {
        socket.broadcast.emit('position', data);
        console.log(data);
    }

}
