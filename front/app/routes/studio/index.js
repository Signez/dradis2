import Ember from "ember";

export default Ember.Route.extend({
    afterModel: function(studio) {
        this.transitionTo('studio.dashboard', studio.get('id'));
    }
});
