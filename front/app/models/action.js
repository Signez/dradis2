import Ember from "ember";
import DS from "ember-data";

export default DS.Model.extend({
    title: DS.attr('string'),
    slug: DS.attr('string'),
    task: DS.attr('string'),

    isRunStudio: Ember.computed.equal('slug', 'run_studio'),
    isEndStudio: Ember.computed.equal('slug', 'end_studio'),
    isLive: Ember.computed.equal('slug', 'live')
});
