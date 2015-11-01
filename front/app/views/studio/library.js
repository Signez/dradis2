import Ember from "ember";

export default Ember.View.extend({
    _scrolledToTheEnd() {
        var libraryWrapper = this.$(".library-wrapper"),
            scrollTop = libraryWrapper.scrollTop(),
            contentHeight = Array.prototype.reduce.call(libraryWrapper.find("> *"), function(a, b){
                return a + Ember.$(b).outerHeight();
            }, 0);

        if (scrollTop + libraryWrapper.innerHeight() >= contentHeight - 20) {
            this.get('controller').send('loadNextPage');
            libraryWrapper.scrollTop(scrollTop);
        }
    },

    scrollToTop: function() {
        if (this.$(".library-wrapper")) {
            this.$(".library-wrapper").scrollTop(0);
        }
    }.observes('controller.scrollLevel'),

    didScroll() {
        Ember.run.debounce(this, this._scrolledToTheEnd, 300);
    },

    didInsertElement() {
        this.$(".library-wrapper").bind('scroll', this.didScroll.bind(this));
    }
});
