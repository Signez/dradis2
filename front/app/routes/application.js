import Ember from "ember";

export default Ember.Route.extend({
    setupController: function() {
        this.controllerFor('status-bar').set('studios', this.get('store').findAll('studio'));
    },

    actions: {
        openModal: function(modalName) {
            return this.render(modalName, {
                into: 'application',
                outlet: 'modal'
            });
        },

        closeModal: function() {
            return this.disconnectOutlet({
                outlet: 'modal',
                parentView: 'application'
            });
        }
    }
});
