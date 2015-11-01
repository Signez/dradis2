import Ember from "ember";

export default Ember.Controller.extend({
    needs: ['studio'],

    plateauDecibels: function() {
        return 20 * Math.round(Math.log(this.get('studioStatus.plateauVolume')) * 1000) / 1000;
    }.property('studioStatus.plateauVolume'),

    jukeboxDecibels: function() {
        return 20 * Math.round(Math.log(this.get('studioStatus.jukeboxVolume')) * 1000) / 1000;
    }.property('studioStatus.jukeboxVolume'),

    bedDecibels: function() {
        return 20 * Math.round(Math.log(this.get('studioStatus.bedVolume')) * 1000) / 1000;
    }.property('studioStatus.bedVolume'),

    feedbackDecibels: function() {
        return 20 * Math.round(Math.log(this.get('studioStatus.feedbackVolume')) * 1000) / 1000;
    }.property('studioStatus.feedbackVolume'),

    feedbackBedGainDecibels: function() {
        return 20 * Math.round(Math.log(this.get('studioStatus.feedbackBedGainIn')) * 1000) / 1000;
    }.property('studioStatus.feedbackBedGainIn'),

    isEqualizerPowered: Ember.computed.alias('studioStatus.penguinEqOn'),
    isPregainPowered: Ember.computed.alias('studioStatus.penguinPregainOn'),
    isCompressorPowered: Ember.computed.alias('studioStatus.penguinCompOn'),
    isLimiterPowered: Ember.computed.alias('studioStatus.penguinLimitOn'),
    isStudioLimiterPowered: Ember.computed.alias('studioStatus.snakeLimitOn'),

    studioStatus: Ember.computed.alias('controllers.studio.studioStatus')
});
