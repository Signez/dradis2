import Ember from "ember";
import DS from "ember-data";

export default DS.Model.extend({
    name: DS.attr('string'),
    slug: DS.attr('string'),
    last_changed_at: DS.attr('date'),
    jukebox: DS.belongsTo('playlist', { async: true, reverse: 'currentStudio' }),

    // bed_liqname
    bed: DS.belongsTo('media', { async: true }),
    bedOnAirSince: DS.attr('date'),
    bedRepeat: DS.attr('boolean'),
    currentShowName: DS.attr('string'),

    bedLength: Ember.computed.alias('bed.length'),

    bedElapsed: function() {
        if (this.get('bedOnAirSince')) {
            return Math.max(0, moment().unix() - this.get('bedOnAirSince.moment').unix());
        } else {
            return 0;
        }
    }.property('bedOnAirSince.moment', 'clock.seconds'),

    // fx_liqname,
    // jukebox_liqname,
    // rec_gold_active,
    // rec_gold_enabled,
    // rec_gold_liqname,
    // rec_show_active,
    // rec_show_enabled,
    // rec_show_liqname,
    // selected

    selected: DS.attr('boolean')
});
