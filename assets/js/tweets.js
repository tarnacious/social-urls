$(function() {
    var ws = new WebSocket('ws://' + window.location.hostname + '/tweetstream');

    ws.onopen = function(){
        ws.send("hello");
        console.log("Open")
    };
    ws.onmessage = function(ev){
        tweet = JSON.parse(ev.data);
        container = $("<div/>");
        $(".tweets").prepend(container.append("@" + tweet.user.screen_name + ": " + tweet.text))
    };
    ws.onclose = function(ev){
        console.log("Closed")
    };
    ws.onerror = function(ev){
        console.log("Error")
    };
});
