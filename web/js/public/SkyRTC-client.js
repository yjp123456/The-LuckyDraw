/**
 * Created by the-engine team
 * 2017-07-22
 */

var SkyRTC = function () {

    function EventEmitter() {
        this.events = {};
    }

    EventEmitter.prototype.on = function (eventName, callback) {
        this.events[eventName] = this.events[eventName] || [];
        this.events[eventName].push(callback);
    };

    EventEmitter.prototype.emit = function (eventName, _) {
        var events = this.events[eventName],
            args = Array.prototype.slice.call(arguments, 1),
            i, m;

        if (!events) {
            return;
        }
        for (i = 0, m = events.length; i < m; i++) {
            events[i].apply(null, args);
        }
    };

    function skyrtc() {
        this.socket = null;
    }

    skyrtc.prototype = new EventEmitter();

    skyrtc.prototype.connect = function (server, prizeName, isUserManager, isAFID) {
        var socket,
            that = this;

        socket = this.socket = new WebSocket(server);

        socket.onopen = function () {
            if (!isAFID)
                socket.send(JSON.stringify({
                    "eventName": "__join",
                    "data": {
                        "prizeName": prizeName,
                        "isUserManager": isUserManager
                    }
                }));
            that.emit("socket_opened", socket);
        };

        socket.onmessage = function (message) {
            var json = JSON.parse(message.data);
            if (json.eventName) {
                that.emit(json.eventName, json.data);
            } else {
                that.emit("socket_receive_message", socket, json);
            }
        };

        socket.onerror = function (error) {
            that.emit("socket_error", error, socket);
            alert("socket error");
        };

        socket.onclose = function (data) {
            that.emit('socket_closed', socket);
            alert("socket close");
        };

        this.on('_peers', function (data) {
            that.emit('connected', socket);
        });

        this.on('_remove_peer', function (data) {

            that.emit("remove_peer", data.socketId);
        });
    };

    skyrtc.prototype.sendMessage = function (message) {
        var that = this;
        that.socket.send(JSON.stringify(message));
    };


    return new skyrtc();
};