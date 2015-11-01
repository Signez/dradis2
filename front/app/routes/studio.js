import Ember from "ember";

export default Ember.Route.extend({
    model: function(params) {
        return this.store.findRecord('studio', params.id);
    },

    renderTemplate: function() {
        this.render('playlist', {
            outlet: 'left'
        });
    },

    afterModel: function(studio) {
        var jukebox = studio.get('jukebox');

        jukebox.then(function(jukebox) {
            this.controllerFor("playlist").setProperties({
                playlist: jukebox,
                model: jukebox.get('elements')
            });
            this.controllerFor("playlist").reload();
        }.bind(this));
    }
});
