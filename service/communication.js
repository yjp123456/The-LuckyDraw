/**
 * Created by the-engine team
 * 2017-07-22
 */

var WebSocketServer = require('ws').Server;
var UUID = require('node-uuid');
var events = require('events');
var util = require('util');
var userLogic = require("../work_units/user_logic");
var ErrorCode = require('../constants/error_code.js');
var errorCode = new ErrorCode();

var errorCb = function (rtc) {
    return function (error) {
        if (error) {
            // rtc.emit('error', error);
        }
    };
};

/**
 * Class SkyRTC
 * @constructor
 */
function SkyRTC(tableNumber) {
    this.prizes = {};
    this.guests = {};
    this.users = [];
    this.userAndID = [];
    this.AFID = {};
    this.prizeUsers = {};


    this.on('__join', function (data, socket) {
        var that = this;
        var prize_name = data.prizeName;
        var isUserManager = data.isUserManager;

        if (!prize_name && !isUserManager) {
            console.log('parameter is null, reject');
            socket.close();
            return;
        }

        console.log('on __join, prize name = ' + prize_name);
        socket.prize_name = prize_name;
        socket.isUserManager = isUserManager;
        that.guests[socket.id] = socket;
        that.initGuestData(socket.id);
    });

    this.on('__clearData', function (data, socket) {
        console.log("receive clear db command");
        var that = this;
        that.initDB(true);
    });

    this.on('__addPrizeUser', function (data, socket) {
        var that = this;
        console.log("receive message: " + JSON.stringify(data));
        if (data) {
            var IDs = data.IDs;
            for (var i = 0; i < IDs.length; i++) {
                var ID = IDs[i];
                if (that.prizeUsers[ID]) {
                    console.log("ID " + ID + " alredy in prize users, reject it");
                    continue;
                }
                that.prizeUsers[ID] = true;
                userLogic.findUserByID(ID, function (error_code, users, ID) {
                    if (error_code.code === errorCode.SUCCESS.code) {
                        if (users && users.length > 0) {
                            var user = users[0];
                            var prize_name = socket.prize_name;
                            userLogic.addPrizeUser(prize_name, user, function (err, user) {
                                if (err.code === errorCode.SUCCESS.code) {
                                    if (!that.prizes[prize_name])
                                        that.prizes[prize_name] = [];
                                    that.prizes[prize_name].push(user);
                                    console.log("add prize user:" + JSON.stringify(user) + " success");
                                } else {
                                    console.log("add prize user:" + JSON.stringify(user) + " fail");
                                }
                            });
                        } else {
                            console.log("ID " + ID + " doesn't match any user");
                            that.prizeUsers[ID] = false;
                        }
                    } else {
                        console.log("get user by id fail");
                        that.prizeUsers[ID] = false;
                    }
                });
            }
        }
    });

    this.on('__saveData', function (data, socket) {
        var that = this;
        if (data && socket.isUserManager) {
            for (var i = 0; i < data.length; i++) {
                userLogic.updateUser(data[i], function (error_code, userName) {
                    if (error_code.code === errorCode.SUCCESS.code) {
                        console.log("save user:" + userName + " success");
                    }
                });
            }
            var message = {
                'eventName': '__savUserSuccess',
                'data': {}
            };
            that.sendMessage(socket, message);
            that.users = [];
            that.userAndID = [];
            that.AFID = {};
            userLogic.getAllUser(function (error_code, users) {
                if (error_code.code === errorCode.SUCCESS.code) {
                    if (users && users.length > 0) {
                        for (var i = 0; i < users.length; i++) {
                            if (users[i].ID === "N/A") {
                                that.users.push(users[i].userName);
                            } else {
                                that.userAndID.push(users[i]);
                                that.AFID[users[i].ID] = users[i].userName;
                            }
                        }
                    }
                } else {
                    console.log("get user by id fail");
                }
            });
        }
    });

    this.on('__addUserAFID', function (data, socket) {
        var that = this;
        console.log("receive message: " + JSON.stringify(data));
        if (data) {
            var IDs = data.IDs;
            for (var i = 0; i < IDs.length; i++) {
                var ID = IDs[i];
                if (that.AFID[ID]) {
                    console.log("ID " + ID + " have already used");
                    continue;
                }

                if (that.users.length > 0) {
                    var ran = parseInt(Math.random() * (that.users.length));
                    var userName = that.users[ran];
                    that.users.splice(ran, 1);

                    that.AFID[ID] = userName;
                    userLogic.updateUser({userName: userName, ID: ID}, function (error_code, user) {
                        if (error_code.code === errorCode.SUCCESS.code) {
                            var message = {
                                'eventName': '__addUserAFIDSuccess',
                                'data': {userName: user.userName, ID: user.ID}
                            };
                            that.userAndID.push(user);
                            that.sendMessage(that.guests[socket.id], message);

                        } else {
                            delete that.AFID[user.ID];//recover data
                            that.users.push(user.userName);
                        }
                    });

                } else {
                    console.log("no enough user for AFID");
                }
            }
        }
    });

}

util.inherits(SkyRTC, events.EventEmitter);


SkyRTC.prototype.initGuestData = function (guest) {
    var that = this;
    var prize_name = that.guests[guest].prize_name;
    var isUserManager = that.guests[guest].isUserManager;
    var data;
    if (isUserManager)
        data = that.userAndID;
    else
        data = {"prizeUsers": that.prizes[prize_name] || [], "IDAndUser": that.AFID};
    var message = {
        'eventName': '__join',
        'data': data
    };
    that.sendMessage(that.guests[guest], message);
};

SkyRTC.prototype.sendMessage = function (socket, message) {
    var errorFunc = function (error) {
        if (error) {
            if (socket) {
                console.log('client:' + socket.id + ' socket error, msg: ' + error);
            } else
                console.log('socket error, msg: ' + error);
        }
    };

    try {
        if (socket)
            socket.send(JSON.stringify(message), errorFunc);
    } catch (e) {
        var player = socket ? socket.id : '';
        console.log('client:' + player + ' socket error, msg:' + e.message);
    }
};

SkyRTC.prototype.broadcastInUser = function (prizeName, message) {
    var that = this;
    for (var guest in that.guests) {
        if (that.guests[guest].prize_name === prizeName)
            that.sendMessage(that.guests[guest], message);
    }
};

SkyRTC.prototype.init = function (socket) {
    var that = this;
    socket.id = UUID.v4();

    socket.on('message', function (data) {
        try {
            var json = JSON.parse(data);
            if (json.eventName) {
                that.emit(json.eventName, json.data, socket);
            } else {
                that.emit('socket_message', json.data, socket);
            }
        } catch (e) {
            console.log(e.message);
        }
    });

    socket.on('error', function (err) {
        console.log('socket ' + socket.id + ' error, msg:' + err);
        delete that.guests[socket.id];
    });

    socket.on('close', function () {
        console.log('client ' + socket.id + ' exit');
        delete that.guests[socket.id];
    });
};

SkyRTC.prototype.initDB = function (isReset) {
    var that = this;
    that.prizes = {};
    that.users = [];
    that.userAndID = [];
    that.AFID = {};
    that.prizeUsers = {};
    if (isReset) {
        console.log("start reset all user");
        userLogic.readUser(function () {
            userLogic.getAllUser(function (error_code, users) {
                if (error_code.code === errorCode.SUCCESS.code) {
                    if (users && users.length > 0) {
                        for (var i = 0; i < users.length; i++) {
                            if (users[i].ID === "N/A") {
                                that.users.push(users[i].userName);
                            } else {
                                that.userAndID.push(users[i]);
                                that.AFID[users[i].ID] = users[i].userName;
                            }
                        }
                    }
                } else {
                    console.log("get user by id fail");
                }
            });
        });

        userLogic.removeAllPrize(function () {
        });
    } else {
        userLogic.getAllUser(function (error_code, users) {
            if (error_code.code === errorCode.SUCCESS.code) {
                if (users && users.length > 0) {
                    for (var i = 0; i < users.length; i++) {
                        if (users[i].ID === "N/A") {
                            that.users.push(users[i].userName);
                        } else {
                            that.userAndID.push(users[i]);
                            that.AFID[users[i].ID] = users[i].userName;
                        }
                    }
                }
            } else {
                console.log("get user by id fail");
            }
        });
    }

    userLogic.getAllPrize(function (error_code, prizes) {
        if (error_code.code === errorCode.SUCCESS.code) {
            if (prizes && prizes.length > 0) {
                for (var i = 0; i < prizes.length; i++) {
                    if (!that.prizes[prizes[i].prizeName])
                        that.prizes[prizes[i].prizeName] = [];
                    that.prizes[prizes[i].prizeName].push(prizes[i].user);
                    that.prizeUsers[prizes[i].user.ID] = true;
                }
            }
        } else {
            console.log("get prize fail");
        }
    });
};

exports.listen = function (server, isReset, tableNumber) {
    var SkyRTCServer;
    if (typeof server === 'number') {
        SkyRTCServer = new WebSocketServer({
            port: server
        });
    } else {
        SkyRTCServer = new WebSocketServer({
            server: server
        });
    }

    SkyRTCServer.rtc = new SkyRTC(tableNumber);
    errorCb = errorCb(SkyRTCServer.rtc);
    SkyRTCServer.on('connection', function (socket, req) {
        this.rtc.init(socket);
    });

    SkyRTCServer.rtc.initDB(isReset);


    return SkyRTCServer;
};
