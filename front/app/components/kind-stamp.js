import Ember from "ember";

export default Ember.Component.extend({
    tagName: "span",
    classNames: ["kind-stamp"],
    classNameBindings: [
        "isMusic:kind-music",
        "isBed:kind-bed",
        "isOneShot:kind-one_shot",
        "isJingle:kind-jingle",
        "isFx:kind-fx",
        "isLive:kind-live",
        "isRunStudio:kind-run-studio",
        "isEndStudio:kind-end-studio"
    ],

    kind: "",

    isMusic: Ember.computed.equal("kind", "music"),
    isOneShot: Ember.computed.equal("kind", "one_shot"),
    isBed: Ember.computed.equal("kind", "bed"),
    isFx: Ember.computed.equal("kind", "fx"),
    isJingle: Ember.computed.equal("kind", "jingle"),
    isLive: Ember.computed.equal("kind", "live"),
    isRunStudio: Ember.computed.equal("kind", "run_studio"),
    isEndStudio: Ember.computed.equal("kind", "end_studio")
});
