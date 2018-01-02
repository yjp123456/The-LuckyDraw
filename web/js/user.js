/**
 * Created by jieping on 2017/11/11.
 */
var rtcForAFID = SkyRTC();
var rtc = SkyRTC();
var totalUserNumber = 0;

initWebsock();
initAFIDSocket();
$("#total").text("用户总数: " + totalUserNumber);

function initWebsock() {
    // initialize web communication
    var isUserManager = true;
    rtc.connect('ws:' + window.location.href.substring(window.location.protocol.length).split('#')[0], "",
        isUserManager);

    rtc.on('__addUserAFIDSuccess', function (user) {
        console.log('receive add user message : ' + JSON.stringify(user));
        addUser(user);
    });

    rtc.on('__savUserSuccess', function (data) {
        alert("save success");
    });

    rtc.on('__join', function (data) {
        console.log('receive __join : ' + JSON.stringify(data));
        if (data) {
            for (var i = 0; i < data.length; i++) {
                addUser(data[i]);
            }
            totalUserNumber = data.length;
            $("#total").text("用户总数: " + totalUserNumber);
        }
        //test
        var message = {
            'eventName': '__addUserAFID',
            'data': {IDs: ["dfsdfsdf","dsfsewfdf","gdsgsde","fewdifdfd","nvbfjfds","ifewufjsdjfs","iefue"]}
        };
        rtc.sendMessage(message);
    });
}


function initAFIDSocket() {
    rtcForAFID.connect('ws://localhost:3002', null, null, true);
    rtcForAFID.on('__AFID', function (data) {
        console.log('receive AFID : ' + data.AFID);
        var message = {
            'eventName': '__addUserAFID',
            'data': {IDs: data.AFID}
        };
        rtc.sendMessage(message);
    });
    rtcForAFID.on('socket_opened', function (data) {
        console.log('AFID socket open');
    });
}

function addUser(user) {
    var tr = $("<tr/>").appendTo($("#content tbody"));
    $("<td/>").text(user.userName).appendTo(tr);
    $("<td/>").text(user.PSID).appendTo(tr);
    $("<td/>").text(user.ID).appendTo(tr);
    var cardNumber = $("<td/>").appendTo(tr);
    $("<input/>", {
        placeholder: "number",
        value: user.number || ""
    }).appendTo(cardNumber);
    totalUserNumber++;
    $("#total").text("用户总数: " + totalUserNumber);
}

function exportUsers() {
    $.post("/exportUser", {}, function (data) {
        if (data.error_code == 0) {
            window.open("files/result_users.xlsx");
        } else {
            alert("generate file error");
        }
    }, "json");

}

function exportPrizes() {
    $.post("/exportPrize", {}, function (data) {
        if (data.error_code == 0) {
            window.open("files/result_prizes.xlsx");
        } else {
            alert("generate file error");
        }
    }, "json");
}

function clearData() {
    if (confirm("确定清空数据库吗？")) {
        var message = {
            'eventName': '__clearData',
            'data': {}
        };
        rtc.sendMessage(message);
        $("#content tbody").empty();
        totalUserNumber = 0;
        $("#total").text("用户总数: " + totalUserNumber);
    }
}

function addData() {
    var trs = $("#content tbody").find("tr");
    var users = [];
    for (var i = 0; i < trs.length; i++) {
        var tr = trs[i];

        var userName = $($(tr).find("td")[0]).text();
        var PSID = $($(tr).find("td")[1]).text();
        var AFID = $($(tr).find("td")[2]).text();
        var number = $($($(tr).find("td")[3]).find("input")).val();
        users.push({userName: userName, PSID: PSID, ID: AFID, number: number});
    }
    var message = {
        'eventName': '__saveData',
        'data': users
    };
    rtc.sendMessage(message);
}