import Ember from "ember";

export default Ember.Service.extend({
    seconds: null,

    tickTack: function() {
        Ember.run.later(this, function() {
            this.notifyPropertyChange('seconds');
            this.tickTack();
        }, 1000 - Math.max(new Date().getMilliseconds(), 100));
    },

    init: function() {
        this.tickTack();
    }
});
