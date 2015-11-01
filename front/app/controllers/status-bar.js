import Ember from "ember";

export default Ember.Controller.extend({
    needs: ['studio'],

    sortingStudios: ['name'],
    sortedStudios: Ember.computed.sort('studios', 'sortingStudios'),

    plateauRunning: Ember.computed.gt('studioStatus.plateauVolume', 0.01),
    jukeboxRunning: Ember.computed.alias('studioStatus.jukeboxSwitch'),

    secondsBeforeNextAction: function() {
        var nextActionMoment = moment(this.get('studioStatus.nextActionAt'));

        if (nextActionMoment.isValid()) {
            return Math.max(0, nextActionMoment.unix() - moment().unix());
        } else {
            return Infinity;
        }
    }.property('studioStatus.nextActionAt', 'controllers.studio.status.clock.seconds'),

    actionIncoming: Ember.computed.lte('secondsBeforeNextAction', 30),
    nextActionIsPlateau: Ember.computed.equal('studioStatus.nextActionSlug', 'live'),
    plateauIncoming: Ember.computed.and('actionIncoming', 'nextActionIsPlateau'),

    studioStatus: Ember.computed.alias('controllers.studio.studioStatus'),
    currentStudioSelected: Ember.computed.alias('controllers.studio.selected'),
    currentStudioRecording: Ember.computed.or('studioStatus.recorderGoldOn', 'studioStatus.recorderShowOn'),
    currentStudio: Ember.computed.alias('controllers.studio.content'),

    studioEmblem: function() {
        return ["studio-emblem", "little-emblem", this.get('controllers.studio.slug')].join(" ");
    }.property('controllers.studio.slug')
});
