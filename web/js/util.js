/**
 * Created by jieping on 2017/11/11.
 */
function getQueryStringRegExp(name) {
    var reg = new RegExp('(^|\\?|&|)' + name + '=([^&]*)(\\s|&|$|)', 'i');
    if (reg.test(decodeURI(location.href))) return unescape(RegExp.$2.replace(/\+/g, ' '));
    return '';
}

function getParameter(name) {
    var rawParam = getQueryStringRegExp(name);
    var sharpPos = rawParam.indexOf('#');
    var p = rawParam;
    if (sharpPos >= 0) {
        p = p.substring(0, sharpPos);
    }
    return p;
}