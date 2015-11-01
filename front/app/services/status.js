import Ember from "ember";

export default Ember.Service.extend({
    serverTime: 0,
    listeners: '?',

    _uri: 'ws://localhost:5000/ws/broadcast',
    _ws: null,

    connect: function() {
        this._ws = new WebSocket(this._uri);

        this._ws.onopen = function() {
            var login = "LOGIN=" + Ember.$("body").data("dradis-api-key");
            this.send(login);
        };

        this._ws.onclose = function() {
            Ember.Logger.warn('Disconnected, will try to reconnect in 5 seconds.');

            Ember.run.later(this, function() { this.connect(); }, 5000);
        }.bind(this);

        this._ws.onmessage = function(e) {
            var data = e.data,
                values = null;

            try {
                values = JSON.parse(String(data));
            } catch (exception) {
                Ember.Logger.debug("Could not parse or save", data);
            }

            if (values) {
                var type = values["type"];

                if (type === "ping") {
                    this.set("serverTime", values["serverTime"]);
                } else if (type === "status" || type === "diff_status") {
                    delete values["type"];

                    Object.keys(values).forEach(function(key) {
                        if (key !== undefined) {
                            var value = values[key],
                                isHashObject = Ember.typeOf(value) === "object";

                            if (isHashObject) {
                                /* Transforming hash-objects into ember observable objects */
                                value = Ember.Object.create(null).setProperties(value);
                            }

                            if (!this.hasOwnProperty(key) && isHashObject) {
                                this.set(key, Ember.Object.create(null));
                            }

                            if (!_.isEqual(this.get(key), value)) {
                                if (Ember.typeOf(this.get(key)) === "instance") {
                                    this.get(key).setProperties(value);
                                } else {
                                    this.set(key, value);
                                }
                            }
                        }
                    }.bind(this));
                }
            }
        }.bind(this);
    },

    humanTime: function(){
        if(this.get('serverTime') > 0) {
            var serverTime = moment.unix(this.get('serverTime'));

            return serverTime.format("HH:mm:ss");
        } else {
            return "??:??:??";
        }
    }.property('serverTime'),

    humanizedSelected: function() {
        var selected = this.get('selected');
        if (selected === "permanent") {
            return "Permanent";
        } else if (selected === "studio_a") {
            return "Studio A";
        } else if (selected === "studio_b") {
            return "Studio B";
        }
    }.property("selected"),

    permanentSelected: Ember.computed.equal("selected", "permanent"),
    studioASelected: Ember.computed.equal("selected", "studio_a"),
    studioBSelected: Ember.computed.equal("selected", "studio_b"),
    studioSelected: Ember.computed.or("studioASelected", "studioBSelected"),

    _lastChangedAt: 0,

    lastChangedAtDidChange: function() {
        if (this.get('lastChangedAt') !== this._lastChangedAt) {
            console.log("lastChangedAtDidChange.");
            this._lastChangedAt = this.get('lastChangedAt');
            this.notifyPropertyChange('canary');
        }
    }.observes('lastChangedAt'),

    canary: null,

    shakeCanary: function() {
        this.notifyPropertyChange('canary');
    },

    connected: Ember.computed.bool('selected'),

    init: function() {
        this.connect();
    }
});
