import Ember from "ember";

export default Ember.Route.extend({
    model: function() {
        return this.modelFor("studio");
    },

    renderTemplate: function() {
        this.render('studio.recorders', {
            outlet: 'main',
            into: 'application'
        });
    },

    setupController: function(controller, model) {
        this._super(controller, model);
    }
});
