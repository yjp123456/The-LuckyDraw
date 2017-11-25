/**
 * Created by the-engine team
 * 2017-10-26
 */

var express = require('express');
var bodyParser = require('body-parser');
var app = module.exports = express();
var db = require('./database/msession');
var userLogic = require("./work_units/user_logic");
var ErrorCode = require('./constants/error_code.js');
var errorCode = new ErrorCode();
var isReset = parseInt(process.argv[2]) || true;

var httpServer = require('http').createServer(app);
var httpPort = normalizePort('3000');
httpServer.listen(httpPort);

db.open(function (err, db) {
    var SkyRTC = require('./service/communication.js').listen(httpServer, isReset);
});

console.log('server is listening on port ' + httpPort);

function normalizePort(val) {
    var port = parseInt(val, 10);

    if (isNaN(port)) {
        return val;
    }
    if (port >= 0) {
        // port number
        return port;
    }
    return false;
}


// app.use(flash());
app.use(bodyParser.urlencoded({
    extended: false
}));
app.use(bodyParser.json());

app.use('/', express.static(__dirname + '/web/'));

app.post('/exportUser', function (req, res) {
    userLogic.exportUser(function (error_code) {
        if (error_code.code === errorCode.SUCCESS.code)
            res.send({error_code: 0});
        else
            res.send({error_code: -1});
        res.end();
    });
});

app.post('/exportPrize', function (req, res) {
    userLogic.exportPrize(function (error_code) {
        if (error_code.code === errorCode.SUCCESS.code)
            res.send({error_code: 0});
        else
            res.send({error_code: -1});
        res.end();
    });
});

