/**
 * Created by jieping on 2017/10/27.
 */

var tableNumber;
var hideTimeout;

$(document).ready(function () {
    tableNumber = getParameter('table');
});

function showPrize() {
    var msg = '';
    var title = $('#title').val().replace(/(^\s*)/g, '');
    var number = $('#number').val().replace(/(^\s*)/g, '');
    if (title && number) {
        location.href = "show_prize.html?title=" + title + "&number=" + number
    } else {
        msg = 'No empty input';
    }

    $('#content').val('');
    showHint(msg);
}



function showHint(message) {
    var hint = $('#msg');

    hint.html(message);
    hint.show('fast');

    clearTimeout(hideTimeout);
    hideTimeout = setTimeout(function () {
        hideHint();
    }, 2000);
}

function hideHint() {
    var hint = $('#msg');
    hint.hide();
}


