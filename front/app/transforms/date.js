import Ember from "ember";
import DS from "ember-data";

var MomentDateObject = Ember.Object.extend({
    moment: function() {
        if (arguments.length > 1) {
            this.set('_moment', arguments[0].clone());
        }

        return this.get('_moment').clone();
    }.property('_moment'),

    toString: function() {
        return this.get('_moment').toString();
    }
});

export default DS.Transform.extend({
    serialize: function(value) {
        return value.format();
    },
    deserialize: function(value) {
        if (value === undefined || value === null) {
            return value;
        } else {
            return MomentDateObject.create({
                _moment: moment(value)
            });
        }
    }
});
