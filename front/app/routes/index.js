import Ember from "ember";

export default Ember.Route.extend({
    model: function(_params) {
        return this.store.findAll('studio');
    },

    afterModel: function(studios) {
        this.transitionTo('studio', studios.sortBy("slug").get('firstObject').get('id'));
    }
});
