import Ember from "ember";
import DS from "ember-data";

export default DS.Model.extend({
    status: DS.attr('string'),
    position: DS.attr('number'),
    media: DS.belongsTo('media', { async: true }),
    action: DS.belongsTo('action', { async: true }),
    playlist: DS.belongsTo('playlist'),
    added_at: DS.attr('date'),
    on_air_since: DS.attr('date'),
    live_content: DS.attr('string'),
    comment: DS.attr('string'),

    done_since: DS.attr('date'),
    edited_at: DS.attr('date'),
    length_hint: DS.attr('number'),
    skipped: DS.attr('boolean'),

    length: function() {
        if (this.get('media')) {
            return this.get('media.length');
        } else {
            return Infinity;
        }
    }.property('media', 'media.length'),

    beforeEnd: function() {
        if (this.get('elapsed') && this.get('length') !== Infinity) {
            return Math.max(0, this.get('length') - this.get('elapsed'));
        } else {
            return this.get('length');
        }
    }.property('elapsed', 'length'),

    elapsed: function() {
        if (this.get('on_air_since')) {
            return Math.max(0, moment().unix() - this.get('on_air_since.moment').unix());
        } else {
            return 0;
        }
    }.property('on_air_since.moment', 'clock.seconds'),

    isCurrent: function() {
        return this.get('position') === this.get('playlist.curpos');
    }.property('position', 'playlist.curpos'),

    scheduled: false,

    isDone: Ember.computed.equal('status', 'done'),
    isReady: Ember.computed.equal('status', 'ready'),
    isPlaying: Ember.computed.equal('status', 'playing'),

    kind: function() {
        if (this.get('media.kind')) {
            return this.get('media.kind');
        } else {
            return this.get('action.slug');
        }
    }.property('media', 'media.kind', 'action', 'action.slug')
});
