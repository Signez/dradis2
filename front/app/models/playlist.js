import Ember from "ember";
import DS from "ember-data";

export default DS.Model.extend({
    name: DS.attr('string'),
    curpos: DS.attr('number'),
    lastChangedAt: DS.attr('string'),
    studios: DS.hasMany('studio'),
    elements: DS.hasMany('playlist_element', { inverse: 'playlist' }),

    state: DS.attr('string'),

    currentElement: function() {
        return this.get('elements').findBy('position', this.get('curpos'));
    }.property('elements.@each.position', 'curpos'),

    pendingElements: function() {
        return this.get('elements').filter(function(el) {
            return el.get('position') >= this.get('curpos');
        }.bind(this));
    }.property('elements.@each.position', 'curpos'),

    pendingStudioEndings: Ember.computed.filterBy('pendingElements', 'action.isEndStudio'),
    pendingStudioRunnings: Ember.computed.filterBy('pendingElements', 'action.isRunStudio'),
    pendingLive: Ember.computed.filterBy('pendingElements', 'action.isLive'),

    hasNoPendingElements: Ember.computed.equal('pendingElements.length', 0),
    hasNoPendingStudioEndings: Ember.computed.equal('pendingStudioEndings.length', 0),
    hasPendingStudioRunnings:  Ember.computed.gt('pendingStudioRunnings.length', 0)
});
