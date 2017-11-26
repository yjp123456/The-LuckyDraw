/**
 * Created by jieping on 2017/11/11.
 */
/**
 * Created by the-engine-team
 * 2017-08-31
 */

var db = require('../database/msession');


var ErrorCode = require('../constants/error_code');
var errorCode = new ErrorCode();

/**
 * Player
 * Fields:
 *      playerName (key)
 *      displayName
 *      tableNumber
 */
exports.removeAll = function (callback) {

    db.collection('users', function (err, collection) {
        if (!err) {
            collection.remove({}, function (err) {
                if (!err) {
                    callback(errorCode.SUCCESS);
                } else {
                    console.log('remove users failed : ' + err);
                    callback(errorCode.FAILED);
                }
            });
        } else {
            console.log('get collection user failed : ' + err);
            callback(errorCode.FAILED, null);
        }
    });
};

exports.addUser = function (userName, ID, callback) {
    db.collection('users', function (err, collection) {
        if (!err) {
            collection.insert({userName: userName, ID: ID}, function (err, docs) {
                if (!err) {
                    callback(errorCode.SUCCESS);
                } else {
                    console.log('insert user ' + userName + ' failed : ' + err);
                    callback(errorCode.FAILED, userName);
                }
            });
        } else {
            console.log('get collection user failed : ' + err);
            callback(errorCode.FAILED, userName);
        }
    });
};

exports.updateUser = function (userName, ID, callback) {
    db.collection('users', function (err, collection) {
        if (!err) {
            collection.update({userName: userName}, {
                $set: {
                    ID: ID
                }
            }, function (err, result) {
                if (!err) {
                    callback(errorCode.SUCCESS);
                } else {
                    console.log('update user ' + userName + ' failed: ' + err);
                    callback(errorCode.FAILED);
                }
            });
        } else {
            console.log('get collection user failed : ' + err);
            callback(errorCode.FAILED);
        }
    });
};

exports.findUserByID = function (ID, callback) {
    db.collection('users', function (err, collection) {
        if (!err) {
            collection.find({ID: ID}).toArray(function (err, results) {
                if (!err) {
                    callback(errorCode.SUCCESS, results);
                } else {
                    console.log('get users error : ' + err);
                    callback(errorCode.FAILED, null);
                }
            });
        } else {
            console.log('get collection user failed : ' + err);
            callback(errorCode.FAILED, null);
        }
    });
};

exports.getAllUser = function (callback) {
    db.collection('users', function (err, collection) {
        if (!err) {
            collection.find({}).toArray(function (err, results) {
                if (!err) {
                    callback(errorCode.SUCCESS, results);
                } else {
                    console.log('get users error : ' + err);
                    callback(errorCode.FAILED, null);
                }
            });
        } else {
            console.log('get collection user failed : ' + err);
            callback(errorCode.FAILED, null);
        }
    });
};
