import Ember from "ember";

export default Ember.Route.extend({
    model: function() {
        return this.modelFor("studio");
    },

    renderTemplate: function() {
        this.render('studio.dashboard', {
            outlet: 'main',
            into: 'application'
        });
    }
});
