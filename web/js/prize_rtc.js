/**
 * Created by jieping on 2017/11/11.
 */
var rtc = SkyRTC();
var rtcForAFID = SkyRTC();
initWebsock();
initAFIDSocket();
var prizeUsers = [];

function initWebsock() {
    // initialize web communication
    var prizeName = getParameter("title");
    rtc.connect('ws:' + window.location.href.substring(window.location.protocol.length).split('#')[0],
        prizeName,false);

    rtc.on('__addPrizeUserSuccess', function (user) {
        console.log('receive add user message : ' + JSON.stringify(user));
        addPrize(user.userName);
    });

    rtc.on('__join', function (data) {
        console.log('receive __join : ' + JSON.stringify(data));
        if (data) {
            prizeUsers = data;
        }
    });
}

function initAFIDSocket() {
    rtcForAFID.connect('ws://localhost:3002');
    rtcForAFID.on('__AFID', function (data) {
        console.log('receive AFID : ' + data.AFID);
        var message = {
            'eventName': '__addPrizeUser',
            'data': {ID: data.AFID}
        };
        rtc.sendMessage(message);
    });
}

