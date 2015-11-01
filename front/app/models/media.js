import Ember from "ember";
import DS from "ember-data";

export default DS.Model.extend({
    title: DS.attr('string'),
    album: DS.attr('string'),
    artist: DS.attr('string'),
    filename: DS.attr('string'),
    publicUrl: DS.attr('string'),
    length: DS.attr('number'),
    kind: DS.attr('string'),

    addedAt: DS.attr('date'),
    updatedAt: DS.attr('date'),
    path: DS.attr('string'),


    isMusic: Ember.computed.equal('kind', 'music'),
    isJingle: Ember.computed.equal('kind', 'jingle'),
    isOneShot: Ember.computed.equal('kind', 'one_shot'),
    isBed: Ember.computed.equal('kind', 'bed'),
    isFx: Ember.computed.equal('kind', 'fx')
});
