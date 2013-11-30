$(function() {
    var tweets = window.data.tweets;
    var tweets_chart = {
        labels : tweets.map(function(tweet) { return tweet.time; }),
        datasets : [
            {
                fillColor : "rgba(220,220,220,0.5)",
                strokeColor : "rgba(220,220,220,1)",
                pointColor : "rgba(220,220,220,1)",
                pointStrokeColor : "#fff",
                data : tweets.map(function(tweet) { return tweet.count; }) 
            }
        ]
    }
    var ctx = document.getElementById("twitterChart").getContext("2d");
    new Chart(ctx).Line(tweets_chart, {});

    var facebook = window.data.facebook;
    var facebook_chart = {
        labels : facebook.map(function(facebook) { return facebook.time; }),
        datasets : [
            {
                fillColor : "rgba(220,220,220,0.5)",
                strokeColor : "rgba(220,220,220,1)",
                pointColor : "rgba(220,220,220,1)",
                pointStrokeColor : "#fff",
                data : facebook.map(function(facebook) { return facebook.count; }) 
            }
        ]
    }
    var ctx = document.getElementById("facebookChart").getContext("2d");
    new Chart(ctx).Line(facebook_chart, {});

    var twitter = window.data.twoday_tweets;
    var two_day_facebook_chart = {
        labels : twitter.map(function(twitter) { return twitter.time; }),
        datasets : [
            {
                fillColor : "rgba(220,220,220,0.5)",
                strokeColor : "rgba(220,220,220,1)",
                pointColor : "rgba(220,220,220,1)",
                pointStrokeColor : "#fff",
                data : twitter.map(function(twitter) { return twitter.count; }) 
            }
        ]
    }
    var ctx = document.getElementById("twoDayTwitterChart").getContext("2d");
    new Chart(ctx).Line(two_day_facebook_chart, {});

    var facebook = window.data.twoday_facebook;
    var two_day_facebook_chart = {
        labels : facebook.map(function(facebook) { return facebook.time; }),
        datasets : [
            {
                fillColor : "rgba(220,220,220,0.5)",
                strokeColor : "rgba(220,220,220,1)",
                pointColor : "rgba(220,220,220,1)",
                pointStrokeColor : "#fff",
                data : facebook.map(function(facebook) { return facebook.count; }) 
            }
        ]
    }
    var ctx = document.getElementById("twoDayFacebookChart").getContext("2d");
    new Chart(ctx).Line(two_day_facebook_chart, {});
});
