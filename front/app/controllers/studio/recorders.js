import Ember from "ember";

export default Ember.Controller.extend({
    needs: ['studio'],

    actions: {
        startRecorderShow: function() {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/record_show');
        },
        startRecorderGold: function() {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/record_gold');
        },
        stopRecorderShow: function() {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/stop_record_show');
        },
        stopRecorderGold: function() {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/stop_record_gold');
        }
    },

    isRecorderGoldPowered: Ember.computed.alias('studioStatus.recorderGoldOn'),
    isRecorderShowPowered: Ember.computed.alias('studioStatus.recorderShowOn'),
    isPigeRecorderPowered: Ember.computed.alias('status.pigeRecorderOn'),

    studioStatus: Ember.computed.alias('controllers.studio.studioStatus')
});
