/**
 * Created by jieping on 2017/11/11.
 */
var db = require('../database/msession');


var ErrorCode = require('../constants/error_code');
var errorCode = new ErrorCode();

exports.addPrizeUser = function (prizeName, userName, ID, callback) {
    db.collection('prizes', function (err, collection) {
        if (!err) {
            collection.find({prizeName: prizeName}).toArray(function (err, results) {
                if (!err) {
                    if (results && results.length > 0) {
                        var users = results[0].users;
                        users.push({userName: userName, ID: ID});

                        collection.update({prizeName: prizeName}, {
                            $set: {
                                users: users
                            }
                        }, function (err, result) {
                            if (!err) {
                                callback(errorCode.SUCCESS,userName);
                            } else {
                                console.log('update prize ' + prizeName + ' failed: ' + err);
                                callback(errorCode.FAILED);
                            }
                        });
                    } else {
                        var data = {prizeName: prizeName, users: [{userName: userName, ID: ID}]};
                        collection.insert(data, function (err, docs) {
                            if (!err) {
                                callback(errorCode.SUCCESS,userName);
                            } else {
                                console.log('insert prize ' + prizeName + ' failed : ' + err);
                                callback(errorCode.FAILED);
                            }
                        });
                    }

                } else {
                    console.log('get prize table error : ' + err);
                    callback(errorCode.FAILED, null);
                }
            });
        } else {
            console.log('get prize collection failed : ' + err);
            callback(errorCode.FAILED, userName);
        }
    });
};

exports.getAllPrize = function (callback) {
    db.collection('prizes', function (err, collection) {
        if (!err) {
            collection.find({}).toArray(function (err, results) {
                if (!err) {
                    callback(errorCode.SUCCESS, results);
                } else {
                    console.log('get prizes table error : ' + err);
                    callback(errorCode.FAILED, null);
                }
            });
        } else {
            console.log('get prize collection failed : ' + err);
            callback(errorCode.FAILED, null);
        }
    });
};

exports.removeAll = function (callback) {

    db.collection('prizes', function (err, collection) {
        if (!err) {
            collection.remove({}, function (err) {
                if (!err) {
                    callback(errorCode.SUCCESS);
                } else {
                    console.log('remove prize failed : ' + err);
                    callback(errorCode.FAILED);
                }
            });
        } else {
            console.log('get collection prize failed : ' + err);
            callback(errorCode.FAILED, null);
        }
    });
};