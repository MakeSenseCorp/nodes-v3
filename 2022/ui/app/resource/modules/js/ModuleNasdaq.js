function Nasdaq() {
    return this;
}

Nasdaq.prototype.UpcommingEvents = function(callback) {
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "get_nasdaq_events", {
        "event": "upcomming"
    }, function(res) {
        var payload = res.data.payload;
        callback(payload.data.data);
    });
}

Nasdaq.prototype.RecentArticles = function(callback) {
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "get_nasdaq_events", {
        "event": "recent-articles"
    }, function(res) {
        var payload = res.data.payload;
        callback(payload.data);
    });
}