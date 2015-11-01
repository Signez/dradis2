import Ember from "ember";

export default Ember.Controller.extend({
    studios: function() {
        return this.store.findAll('studio');
    },

    selectedStudioDidChange: function() {
        var newSelectedStatus = this.get('status.' + this.get('slug') + '.selected');
        if (newSelectedStatus !== undefined && this.get('selected') !== newSelectedStatus) {
            this.set('selected', newSelectedStatus);
        }
    }.observes('status.studio_a.selected', 'status.studio_b.selected'),

    canaryDidSquack: function() {
        console.log("SQUACK");
        this.get('model').reload();
    }.observes('status.canary'),

    studioStatus: function() {
        if (this.get('slug') === 'studio_a') {
            return this.get('status.studio_a');
        } else {
            return this.get('status.studio_b');
        }
    }.property('slug', 'status.studio_a', 'status.studio_b'),

    actions: {
        startBed: function (media) {
            this.get('command')
                .post('/api/studios/' + this.get('model.id') + '/start_bed', {
                    GET: {
                        media_id: media.get('id')
                    }
                });
        },

        stopBed: function () {
            this.get('command')
                .post('/api/studios/' + this.get('model.id') + '/stop_bed');
        },

        setBedRepeat: function (repetition) {
            this.get('command')
                .post('/api/studios/' + this.get('model.id') + '/bed_options', {
                    GET: {
                        repetition: repetition ? "true" : "false"
                    }
                });
        }
    }
});
