import Ember from "ember";

export default Ember.View.extend({
    studioEmblem: function() {
        return ["studio-emblem", "header-emblem", this.get('controller.model.slug')].join(" ");
    }.property('controller.model.slug')
});

