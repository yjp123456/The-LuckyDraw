/**
 * Created by the-engine team
 * 2017-09-08
 */
// db : MongoDB
var MONGO_DB_URI = "";
var MONGO_DB_SERVER_ADDRESS = "127.0.0.1";
var MONGO_DB_NAME = "default_db2";
var MONGO_DB_USER = null;
var MONGO_DB_PASSWORD = null;

var Db = require('mongodb').Db;
var Server = require('mongodb').Server;

var db = new Db(MONGO_DB_NAME, new Server(MONGO_DB_SERVER_ADDRESS, 27017, {auto_reconnect: true, poolSize: 4}),{safe:true});

module.exports = db;