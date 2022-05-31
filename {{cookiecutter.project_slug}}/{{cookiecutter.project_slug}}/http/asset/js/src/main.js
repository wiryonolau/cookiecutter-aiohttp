'use strict';
const extend = function() {
    let result = {};
    let obj;
    for (let i = 0; i < arguments.length; i++) {
        obj = arguments[i];
        for (let key in obj) {
            if (Object.prototype.toString.call(obj[key]) === '[object Object]') {
                if (typeof result[key] === 'undefined') {
                    result[key] = {};
                }
                result[key] = extend(result[key], obj[key]);
            } else {
                result[key] = obj[key];
            }
        }
    }
    return result;
}

const WebsocketClient = function(options = {}) {
    let _client = null;
    let _instance = new Date().getTime();

    let _defaults = {
        path: "",
        onopen: undefined,
        onmessage: undefined,
        onclose: undefined,
        reconnect: true
    }

    let _options = extend(_defaults, options);

    let start = () => {
        connect();
        setEvent();

        if (_options.reconnect) {
            setInterval(() => {
                if (_client.readyState === WebSocket.CLOSED) {
                    connect();
                    setEvent();
                }
            }, 5000);
        }
    }

    let setEvent = () => {
        _client.onopen = (event) => {
            try {
                _options.onopen(_client);
            } catch (err) {
                console.log(err.message);
            }
        }

        _client.onmessage = (event) => {
            try {
                let msg = JSON.parse(event.data);
                _options.onmessage(msg);
            } catch (err) {
                console.log(err.message);
            }
        }

        _client.onclose = (event) => {
            try {
                _options.onclose(event);
            } catch (err) {
                console.log(err.message);
            }

            if (event.wasClean) {
                console.log("Connection end");
            } else {
                console.log("Connection broken");
            }
        }
    }

    let stop = () => {
        _client.close();
    }

    let connect = () => {
        try {
            _client = new WebSocket("ws://" + window.location.host + "/ws/" + _options.path);
            console.log("Client connected");
        } catch (err) {
            console.log(err.message);
        }
    }

    return {
        start: start,
        stop: stop,
        setListener: ((event, value) => {
            _options[event] = value;
        })
    }
}

const url = function(path, query) {
    let url = window.location.protocol + "//" + window.location.host + path;

    let param = [];
    for (let key in query) {
        if (query.hasOwnProperty(key)) {
            param.push(encodeURIComponent(key) + '=' + encodeURIComponent(query[key]));
        }
    }

    if (param.length > 0) {
        return url + "?" + param.join("&");
    }
    return url;
}

String.prototype.ljust = function(length, char = "&nbsp;") {
    var fill = [];
    while (fill.length + this.length < length) {
        fill[fill.length] = char;
    }
    return fill.join('') + this;
}

String.prototype.rjust = function(length, char = "&nbsp;") {
    var fill = [];
    while (fill.length + this.length < length) {
        fill[fill.length] = char;
    }
    return this + fill.join('');
}
