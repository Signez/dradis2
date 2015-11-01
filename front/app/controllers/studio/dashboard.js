import Ember from "ember";

export default Ember.Controller.extend({
    needs: ['studio'],

    actions: {
        startBed: function() {
            this.get('store').findRecord('media', 478).then(function(media) {
                this.get('controllers.studio').send('startBed', media);
            }.bind(this));
        },

        stopBed: function() {
            this.get('controllers.studio').send('stopBed');
        },

        setBedRepeat: function(repetition) {
            this.get('controllers.studio').send('setBedRepeat', repetition);
        }
    }
});
