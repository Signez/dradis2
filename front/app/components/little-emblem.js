import Ember from "ember";

export default Ember.Component.extend({
    tagName: "span",
    classNames: ["little-emblem"],
    classNameBindings: ["type", "slug"]
});
