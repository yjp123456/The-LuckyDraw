/**
 * Created by jieping on 2017/11/11.
 */
var rtc = SkyRTC();
var rtcForAFID = SkyRTC();
initWebsock();
initAFIDSocket();
var prizeUsers = [];
var IDAndUser = {};
var allPrizeUser = {};

function initWebsock() {
    // initialize web communication
    var prizeName = getParameter("title");
    rtc.connect('ws:' + window.location.href.substring(window.location.protocol.length).split('#')[0],
        prizeName, false);

    /* rtc.on('__addPrizeUserSuccess', function (user) {
     console.log('receive add user message : ' + JSON.stringify(user));
     });*/

    rtc.on('__join', function (data) {
        console.log('receive __join : ' + JSON.stringify(data));
        if (data) {
            prizeUsers = data.prizeUsers;
            IDAndUser = data.IDAndUser;
        }

        //test
        var message = {
            'eventName': '__addPrizeUser',
            'data': {IDs: ["dfsdfsdf","dsfsewfdf","gdsgsde","fewdifdfd","nvbfjfds","ifewufjsdjfs","iefue"]}
        };
        rtc.sendMessage(message);
    });
}

function initAFIDSocket() {
    rtcForAFID.connect('ws://localhost:3002');
    rtcForAFID.on('__AFID', function (data) {
        console.log('receive AFID : ' + data.AFID);
        var ids = data.AFID;
        var message = {
            'eventName': '__addPrizeUser',
            'data': {IDs: ids}
        };
        rtc.sendMessage(message);
        for (var i = 0; i < ids.length; i++) {
            var id = ids[i];
            var userName = IDAndUser[id].userName;
            var PSID = IDAndUser[id].PSID;
            if (userName && PSID && !allPrizeUser[id]) {
                addPrize(userName, PSID, id);
            } else {
                console.log("ID ->" + id + " doesn't match any user or already used");
            }
        }
    });
}

