import Ember from "ember";

export default Ember.ArrayController.extend({
    needs: ['studio'],
    sortProperties: ['position'],
    playlist: null,
    reloadCanary: null,
    lastSuccesfullyReloadedAt: null,
    model: [],

    canaryDidChange: function() {
        Ember.run.next(this, this.checkReload);
    }.observes('status.canary'),

    checkReload: function() {
        var changedAt = this.get('status.playlistLastChangedAt') || [],
            playlistChangedAt = changedAt["" + this.get('playlist.id')];

        if (playlistChangedAt && !Ember.isEqual(playlistChangedAt, this.get('lastSuccesfullyReloadedAt'))) {
            this.set('lastSuccesfullyReloadedAt', playlistChangedAt);
            this.reload();
        }
    },

    reload: function() {
        if (this.get('playlist')) {
            this.notifyPropertyChange("reloadCanary");
            this.get('playlist').reload();
        }
    },

    actions: {
        addMedia: function(media) {
            this.get('command')
                .addExpectedAnimation("media", "add", media.get('id'))
                .post('/api/playlists/' + this.get('playlist.id') + '/add', {
                    GET: {
                        media_id: media.get('id')
                    }
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        addActionBySlug: function(action_slug) {
            this.get('command')
                .addExpectedAnimation("action", "add", action_slug)
                .post('/api/playlists/' + this.get('playlist.id') + '/add', {
                    GET: {
                        action_slug: action_slug
                    },
                    shakeCanary: true
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        insertMedia: function(media, position) {
            this.get('command')
                .addExpectedAnimation("media", "add", media.get('id'))
                .post('/api/playlists/' + this.get('playlist.id') + '/add', {
                    GET: {
                        media_id: media.get('id'),
                        position: position
                    }
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        endLive: function() {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/end_live', {
                    shakeCanary: true
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        /*moveUp: function(element) {
            this.get('command')
                .post('/api/playlists/' + this.get('playlist.id') + '/move', {
                    GET: {
                        element_id: element.get('id'),
                        position: element.get('position') - 1
                    }
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        moveDown: function(element) {
            this.get('command')
                .post('/api/playlists/' + this.get('playlist.id') + '/move', {
                    GET: {
                        element_id: element.get('id'),
                        position: element.get('position') + 2
                    }
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },*/

        move: function(element, newPosition) {
            this.get('command')
                .addExpectedAnimation("playlist-element", "remove", element.get('id'))
                .addExpectedAnimation("playlist-element", "add", element.get('id'))
                .post('/api/playlists/' + this.get('playlist.id') + '/move', {
                    GET: {
                        element_id: element.get('id'),
                        position: newPosition
                    }
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        removeElement: function(element) {
            this.get('command')
                .addExpectedAnimation("playlist-element", "remove", element.get("id"))
                .post('/api/playlists/' + this.get('playlist.id') + '/remove', {
                    GET: {
                        element_id: element.get('id')
                    }
                }).finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        run: function() {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/run')
                .finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        selectAndRun: function() {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/select_run')
                .finally(function(){ Ember.run.later(this, this.canaryDidChange, 500); }.bind(this));
        },

        skip: function(element) {
            this.get('command')
                .post('/api/studios/' + this.get('controllers.studio.id') + '/skip', {
                    GET: {
                        element_id: element.get('id')
                    }
                });
        }
    },

    willRunOrIsRunning: Ember.computed.or('playlist.hasPendingStudioRunnings', 'controllers.studio.selected'),
    shouldHaveAPendingStudioEnding: Ember.computed.and('playlist.hasNoPendingStudioEndings', 'willRunOrIsRunning')
});
