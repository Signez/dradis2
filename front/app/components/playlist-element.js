import Ember from "ember";

export default Ember.Component.extend({
    tagName: 'li',
    attributeBindings: [
        'contentPosition:data-position',
        'isDraggable:draggable'
    ],
    classNames: ['playlist-element', 'list-group-item'],
    classNameBindings: [
        'content.isCurrent:current-element',
        'content.isDone:status-done',
        'content.isReady:sortable',
        'fadedInAndAnimated::out',
        'isDragged:dragging'
    ],
    visible: false,
    fadedIn: false,

    editedComment: "",

    commentDidChange: function() {
        this.set('editedComment', this.get('content.comment'));
    }.observes('content.comment'),

    editedLiveContent: "",

    liveContentDidChange: function() {
        this.set('editedLiveContent', this.get('content.live_content'));
    }.observes('content.live_content'),

    hasComment: Ember.computed.bool("content.comment"),

    isUpdating: Ember.computed.or('isUpdatingComment', 'isUpdatingLiveContent'),
    isUpdatingComment: false,
    isUpdatingLiveContent: false,
    isNotUpdating: Ember.computed.not('isUpdating'),

    isReady: Ember.computed.alias('content.isReady'),
    contentPosition: Ember.computed.alias('content.position'),

    isDraggable: Ember.computed.and('isReady', 'isNotUpdating'),

    fadedInAndAnimated: Ember.computed.or('shouldNotAnimate', 'fadedIn'),

    progressBarStyle: function() {
        var percentage = Math.min(Math.max(0, Math.round(this.get('content.elapsed') / this.get('content.length') * 1000) / 10), 100);
        return ["width: ", percentage,  "%"].join('');
    }.property('content.elapsed', 'content.length'),

    classesAssociations: {
        'live': 'fa-microphone',
        'run_studio': 'fa-sign-in',
        'end_studio': 'fa-sign-out'
    },

    actionIconClass: function() {
        var specificClass = this.classesAssociations[this.get('content.action.slug')];

        return ["fa", "fa-fw", specificClass ? specificClass : "fa-exclamation"].join(" ");
    }.property('content.action.slug'),

    shouldAnimate: function() {
        var expectedAnimation = this.get('command').get('expectedAnimation');

        return expectedAnimation.some(function(animation, index, self) {
            if (animation.get('objectName') === "media") {
                return animation.get('relevantId') === this.get('content.media.id');
            } else if (animation.get('objectName') === "playlist-element") {
                return animation.get('relevantId') === this.get('content.id');
            } else if (animation.get('objectName') === "action") {
                return animation.get('relevantId') === this.get('content.action.slug');
            }
        }.bind(this));
    }.property('command.expectedAnimation.[]'),
    shouldNotAnimate: Ember.computed.not('shouldAnimate'),

    didInsertElement: function() {
        if (this.get('shouldAnimate')) {
            this.set('fadedIn', false);

            Ember.run.next(this, function () {
                if (!this.isDestroyed) {
                    this.set('fadedIn', true);
                }
            });

            Ember.run.later(this, function() {
                this.removeExpectedAnimation("add");
            }, 500);
        } else {
            this.set('fadedIn', true);
        }

        this.$()[0].addEventListener('dragstart', function(event) {
            var $parentPlaylist = this.$().parents(".playlist");

            this.set("isDragged", true);

            if ($parentPlaylist.find(".drop-placeholder").size() === 0) {
                $parentPlaylist.prepend('<div class="drop-placeholder" style="display: none"></div>');
            }

            event.dataTransfer.setData('text/plain', JSON.stringify({
                "objectName": "playlist-element",
                "relevantId": this.get('content.id'),
                "originalHtmlId": this.$().attr("id"),
                "originalPosition": this.get('content.position')
            }));
        }.bind(this), false);

        this.$()[0].addEventListener('dragend', function(event) {
            if (!this.isDestroyed) {
                this.set("isDragged", false);
            }
        }.bind(this), false);
    },

    willDestroyElement: function() {
        if (this.get('shouldAnimate')) {
            var clone = this.$().clone(),
                prevElement = this.$().prev(),
                parentElement = this.$().parent();

            if (prevElement.size() > 0) {
                prevElement.after(clone);
            } else {
                parentElement.prepend(clone);
            }

            clone.addClass("will-be-destroyed");
            clone.css("height", clone.css("height"));
            Ember.run.later(clone, function() { this.addClass("destroyed"); }, 30);
            Ember.run.later(clone, function() { this.addClass("collapsed"); }, 500);
            Ember.run.later(clone, function() { this.remove();              }, 700);

            this.removeExpectedAnimation("remove");
        }
    },

    removeExpectedAnimation: function(operation) {
        if (this.get('command')) {
            this.get('command').removeExpectedAnimation("playlist-element", operation, this.get('content.id'));
            if (this.get('content.media.id')) {
                this.get('command').removeExpectedAnimation("media", operation, this.get('content.media.id'));
            } else if (this.get('content.action.id')) {
                this.get('command').removeExpectedAnimation("action", operation, this.get('content.action.slug'));
            }
        }
    },

    actions: {
        removeElement: function() {
            console.log('Removing element', this.get('content.id'));
            this.sendAction('removeElement', this.get('content'));
        },
        moveUp: function() {
            console.log('Moving up', this.get('content.id'));
            this.sendAction('moveUp', this.get('content'));
        },
        moveDown: function() {
            console.log('Moving down', this.get('content.id'));
            this.sendAction('moveDown', this.get('content'));
        },
        move: function() {
            var previousElement = Ember.View.views[this.$().prev().attr('id')],
                newPosition = this.get('content.playlist.curpos');

            if (previousElement) {
                newPosition = previousElement.get('content.position') + 1;
            }

            console.log('Moving', this.get('content.id'), newPosition);
            this.sendAction('move', this.get('content'), newPosition);
        },
        endLive: function() {
            this.sendAction('endLive');
        },
        skip: function() {
            console.log('Skipping', this.get('content.id'));
            this.sendAction('skip', this.get('content'));
        },
        run: function() {
            this.sendAction('run', this.get('content'));
        },
        openModal: function(modalName) {
            this.sendAction('openModal', modalName);
        },

        showUpdateComment: function() {
            this.commentDidChange();
            this.set('isUpdatingComment', true);
            Ember.run.next(this, function() {
                this.$(".js-autofocus").focus().select();
            });
        },

        showUpdateLiveContent: function() {
            this.liveContentDidChange();
            this.set('isUpdatingLiveContent', true);
            Ember.run.next(this, function() {
                this.$(".js-autofocus").focus().select();
            });
        },

        updateComment: function() {
            this.set('isUpdatingComment', false);
            this.get('command')
                .post('/api/elements/' + this.get('content.id') + '/update', {
                    POST: {
                        comment: this.get('editedComment')
                    }
                }).then(function(){ this.get('content').reload(); }.bind(this));
        },

        updateLiveContent: function() {
            this.set('isUpdatingLiveContent', false);
            this.get('command')
                .post('/api/elements/' + this.get('content.id') + '/update', {
                    POST: {
                        live_content: this.get('editedLiveContent')
                    }
                }).then(function(){ this.get('content').reload(); }.bind(this));
        }
    }
});
