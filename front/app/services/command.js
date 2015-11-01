import Ember from "ember";

export default Ember.Service.extend({
    expectedAnimation: Ember.A([]),

    addExpectedAnimation: function(objectName, operation, relevantId) {
        var expectedAnimation = Ember.Object.create({
            objectName: objectName,
            operation: operation,
            relevantId: relevantId
        });
        this.get('expectedAnimation').addObject(expectedAnimation);
        return this;
    },

    removeExpectedAnimation: function(objectName, operation, relevantId) {
        this.get('expectedAnimation').removeObjects(
            this.get('expectedAnimation').filter(function(animation, index, self) {
                return animation.get('objectName') === objectName &&
                    animation.get('operation') === operation &&
                    animation.get('relevantId') === relevantId;
            })
        );
        return this;
    },

    post: function(url, post_options) {
        var options = post_options || {},
            get_parameters = options.GET;

        if (get_parameters) {
            url = url + '?' + Ember.$.param(get_parameters);
        }

        return new Ember.RSVP.Promise(function(resolve, reject){
            Ember.$.post(url, options.POST, function(data) {
                Ember.Logger.debug("Command sent", data);
                if (options.shakeCanary) {
                    this.get('status').shakeCanary();
                }
                return resolve(data);
            }.bind(this))
            .fail(function(error) {
                return reject(error);
            });
        }.bind(this));
    }
});
