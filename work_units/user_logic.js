/**
 * Created by the-engine team
 * 2017-09-08
 */

// global inclusion

// local inclusion
var userDao = require('../models/user_dao.js');
var prizeDao = require('../models/prizeDao.js');
var xlsx = require('node-xlsx');
var fs = require('fs');
var userFile = __dirname + "/../constants/users.xlsx";
var exportUserPath = __dirname + "/../web/files/result_users.xlsx";
var exportPrizePath = __dirname + "/../web/files/result_prizes.xlsx";

var ErrorCode = require('../constants/error_code.js');
var errorCode = new ErrorCode();


exports.readUser = function (callback) {
    userDao.removeAll(function (error_code) {
        if (error_code.code === errorCode.SUCCESS.code) {
            var data = xlsx.parse(userFile);
            if (data) {
                var users = data[0].data;
                var num = 0;
                for (var i = 0; i < users.length; i++) {
                    var userName = users[i][0];
                    if (userName) {
                        userDao.addUser(userName, "N/A", function (error_code, user) {
                            if (error_code.code !== errorCode.SUCCESS.code) {
                                console.log("add user " + user + "fail");
                            }
                            num++;
                            if (num === users.length) {
                                callback();
                            }
                        });
                    }
                }
            }
            console.log(JSON.stringify(data));
        } else {
            console.log("remove users fail");
        }
    });
};

exports.exportUser = function (callback) {
    userDao.getAllUser(function (error_code, results) {
        var data = [{name: "sheet1", data: [["姓名", "number", "AFID"]]}];
        var users = data[0].data;
        if (error_code.code === errorCode.SUCCESS.code) {
            if (results && results.length >= 0) {
                for (var i = 0; i < results.length; i++) {
                    var user = [results[i].userName, results[i].number, results[i].ID];
                    users.push(user);
                }
                var buffer = xlsx.build(data);
                fs.writeFile(exportUserPath, buffer, function (err) {
                    if (err) {
                        console.log("export user fail");
                        callback(errorCode.FAILED);
                    }
                    console.log('has finished');
                    callback(errorCode.SUCCESS);
                });
            }
        } else {
            callback(errorCode.FAILED);
        }
    });
};

exports.exportPrize = function (callback) {
    prizeDao.getAllPrize(function (error_code, prizes) {
        var data = [{name: "sheet1", data: [["奖项", "姓名", "number"]]}];
        var results = data[0].data;
        if (error_code.code === errorCode.SUCCESS.code) {
            if (prizes && prizes.length >= 0) {
                for (var i = 0; i < prizes.length; i++) {
                    var prizeUser = prizes[i].user;
                    var prizeName = prizes[i].prizeName;
                    var prize = [prizeName, prizeUser.userName, prizeUser.number];
                    results.push(prize);
                }
                var buffer = xlsx.build(data);
                fs.writeFile(exportPrizePath, buffer, function (err) {
                    if (err) {
                        console.log("export prize fail");
                        callback(errorCode.FAILED);
                    }
                    console.log('has finished');
                    callback(errorCode.SUCCESS);
                });
            }
        } else {
            callback(errorCode.FAILED);
        }
    });
};

exports.findUserByID = function (ID, callback) {
    userDao.findUserByID(ID, callback);
};

exports.getAllUser = function (callback) {
    userDao.getAllUser(callback)
};

exports.updateUser = function (user, callback) {
    userDao.updateUser(user, callback)
};

exports.removeAllPrize = function (callback) {
    prizeDao.removeAll(callback);
};

exports.addPrizeUser = function (prizeName, user, callback) {
    prizeDao.addPrizeUser(prizeName, user, callback);
};

exports.getAllPrize = function (callback) {
    prizeDao.getAllPrize(callback)
};
