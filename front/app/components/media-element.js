import Ember from "ember";

export default Ember.Component.extend({
    tagName: 'li',
    classNames: ['media-element', 'list-group-item'],
    visible: false,

    click(event) {
        var $target = Ember.$(event.target);

        if ($target.not(".media-element-pane").not(".media-element-pane *").length) {
            return this.send('open');
        }
    },

    didInsertElement: function() {
        var audio = this.$("audio")[0];

        audio.addEventListener("playing", function() {
            this.set("isPrelistening", true);
        }.bind(this));

        audio.addEventListener("pause", function() {
            this.set("isPrelistening", false);
        }.bind(this));

        audio.addEventListener("timeupdate", function() {
            this.set("prelisteningElapsed", audio.currentTime);
        }.bind(this));

        audio.addEventListener("durationchange", function() {
            this.set("prelisteningDuration", audio.duration);
        }.bind(this));

        this.set("prelisteningDuration", this.get('content.length'));

        this.$(".media-line")[0].addEventListener('dragstart', function(event) {
            event.dataTransfer.setData('text/plain', JSON.stringify({
                "objectName": "media",
                "relevantId": this.get('content.id'),
                "originalHtmlId": this.$().attr("id")
            }));
        }.bind(this), false);
    },

    isPrelistening: false,
    prelisteningElapsed: 0,
    prelisteningDuration: 0,

    media: Ember.computed.alias('content'),

    actions: {
        open() {
            this.toggleProperty('visible');
        },

        addMedia() {
            console.log('Adding media', this.get('content.id'));
            this.sendAction('addMedia', this.get('content'));
        },

        prelisteningPlay() {
            var audio = this.$("audio")[0];
            audio.preload = "auto";
            audio.play();
        },

        prelisteningBackward() {
            this.$("audio")[0].currentTime -= 20;
        },

        prelisteningForward() {
            this.$("audio")[0].currentTime += 20;
        },

        prelisteningStop() {
            var audio = this.$("audio")[0];
            audio.pause();
            audio.currentTime = 0;
        }
    }
});
