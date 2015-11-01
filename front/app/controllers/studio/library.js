import Ember from "ember";

export default Ember.Controller.extend({
    needs: ['playlist'],
    text: "",
    orderedBy: "title",
    desc: false,
    offset: null,
    meta: Ember.Object.create({}),
    scrollLevel: 0,

    LIMIT_PER_PAGE: 25,

    _addMediaToPlaylist(media) {
        this.get('controllers.playlist').send('addMedia', media);
    },

    haveNextPage: function() {
        return this.get('elementsLeft') > this.LIMIT_PER_PAGE;
    }.property('elementsLeft'),

    elementsLeft: function() {
        return this.get('meta.count') - (this.get('meta.offset') + this.LIMIT_PER_PAGE);
    }.property('meta.offset', 'meta.count'),

    scrollToTop() {
       this.notifyPropertyChange('scrollLevel');
    },

    queryFieldDidChange: function() {
        Ember.run.debounce(this, this.debouncedSearch, 300);
    }.observes('queryField'),

    debouncedSearch() {
        this.send('search');
    },

    sortedByArtist: Ember.computed.equal('orderedBy', 'artist'),
    sortedByTitle: Ember.computed.equal('orderedBy', 'title'),
    sortedByAlbum: Ember.computed.equal('orderedBy', 'album'),
    sortedByLength: Ember.computed.equal('orderedBy', 'length'),

    clearDisabled: Ember.computed.empty('queryField'),
    sortField: Ember.computed.alias('orderedBy'),
    
    actions: {
        addMediaToPlaylist(media) {
            this._addMediaToPlaylist(media);
        },
        search() {
            this.set('text', this.get('queryField'));
            this.set('offset', null);
            this.scrollToTop();
            this.send('refreshLibrary');
        },
        resetAndRefreshLibrary() {
            this.set('offset', null);
            this.scrollToTop();
            this.send('refreshLibrary');
        },
        loadNextPage() {
            if (this.get('elementsLeft') > 0) {
                this.set('offset', (this.get('meta.offset') || 0) + this.LIMIT_PER_PAGE);
                this.send('refreshLibrary');
            }
        },

        sortBy(field) {
            this.set('sortField', field);

            Ember.run.next(this, function() {
                this.send('resetAndRefreshLibrary');
            });
        },

        clearSearch() {
            this.set('queryField', '');
        },

        toggleOrder() {
            if (this.get('desc')) {
                this.set('desc', false);
            } else {
                this.set('desc', true);
            }

            Ember.run.next(this, function() {
                this.send('resetAndRefreshLibrary');
            });
        }
    }
});
