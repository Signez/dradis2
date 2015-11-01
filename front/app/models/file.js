import Ember from "ember";

export default Ember.Object.extend({
    rawFile: null,

    widthStyle: function() {
        return ["width: ", this.get('percentage'), "%;"].join("");
    }.property('percentage'),

    percentage: function() {
        return Math.round(this.get('uploadedSize') / this.get('rawFile').size * 10000) / 100;
    }.property('uploadedSize'),

    remainingDuration: function() {
        if (this.get('elapsedDuration')) {
            return Math.round(this.get('elapsedDuration') / this.get("uploadedSize") * this.get("rawFile").size);
        } else {
            return false;
        }
    }.property('elapsedDuration', 'uploadedSize'),

    elapsedDuration: function() {
        if (this.get('uploading')) {
            return moment().unix() - this.get('uploadStartedAt'); //Math.max(0, moment().unix() - this.get('uploadStartedAt'));
        } else {
            return false;
        }
    }.property('uploading', 'uploadStartedAt', 'clock.seconds'),

    uploadStartedAt: 0,

    uploadedSize: 0,
    uploading: false,
    uploaded: false,
    success: false,
    uploadErrorMessage: "",

    filename: "",
    url: "",
    size: 0,

    humanFilename: function() {
        var splitted = this.get("filename").split("__");

        if (splitted.length > 2) {
            return splitted.slice(2).join("__");
        } else {
            return this.get("filename");
        }
    }.property("filename"),
    inspected: false,

    analyzed: false,
    waitingForAnalyze: Ember.computed.not("analyzed"),
    title: "",
    album: "",
    artist: "",

    titleCompleted: Ember.computed.notEmpty("title"),
    artistCompleted: Ember.computed.notEmpty("artist"),
    albumCompleted: Ember.computed.notEmpty("album"),

    tags: function() {
        return {
            'title': this.get('title'),
            'album': this.get('album'),
            'artist': this.get('artist')
        };
    }.property('title', 'album', 'artist'),

    completeTags: Ember.computed.and("titleCompleted", "artistCompleted", "albumCompleted")
});
