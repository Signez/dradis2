import Ember from "ember";

export default Ember.Controller.extend({
    actions: {
        refresh: function() {
           this.get('command').post('/api/maintenance/rescan');
        },

        maintenance_bootstrap: function() {
           this.get('command').post('/api/maintenance/bootstrap');
        }
    }
});
