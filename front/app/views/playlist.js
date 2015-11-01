import Ember from "ember";

export default Ember.View.extend({
    P_KEY: 80,
    D_KEY: 68,
    F_KEY: 70,

    cancellingSort: false,

    dragging: false,

    counter: 0,

    dragenter: function (event) {
        event.stopPropagation();
        event.preventDefault();

        if (this.$().find(".drop-placeholder").size() === 0) {
            this.$(".playlist").prepend('<div class="drop-placeholder" style="display: none"></div>');
        }

        this.set("dragging", true);

        this.counter++;
    },

    dragleave: function (event) {
        event.stopPropagation();
        event.preventDefault();

        this.counter--;

        if (this.counter === 0) {
            this.$().find(".drop-placeholder").hide();
            this.set("dragging", false);
        }
    },

    dragover: function (event) {
        var $placeholder = this.$(".drop-placeholder"),
            $target = this.$(event.target);

        if ($target.is(".playlist")) {
            $target.find(".playlist-element:last").after($placeholder);
            $placeholder.show();
        } else if ($target.is(".playlist-hint") || $target.parents(".playlist-hint").size()) {
            $target.parents(".playlist").find(".playlist-element:last").after($placeholder);
            $placeholder.show();
        } else if ($target.is(".drop-placeholder")) {
            // Duh, do nothing
            $placeholder.show();
        } else {
            if (!$target.is(".sortable")) {
                $target = this.$(event.target).parents(".sortable");
            }

            if ($target.size() > 0) {
                var offset = $target.offset();

                if (event.clientY - offset.top > $target.outerHeight() / 2) {
                    $target.after($placeholder);
                } else {
                    $target.before($placeholder);
                }
                $placeholder.show();
            } else {
                event.dropEffect = "none";
                $placeholder.hide();
            }
        }

        event.stopPropagation();
        event.preventDefault();
    },

    drop: function (event) {
        event.preventDefault();
        event.stopPropagation();

        this.set("dragging", false);

        var dt = null;

        try { dt = JSON.parse(event.dataTransfer.getData('text/plain')); } catch (e) { }

        console.log("Dropped", dt);

        if (dt && this.$(".drop-placeholder").is(":visible")) {
            var previousElement = this.$(".drop-placeholder").prevAll(".playlist-element"),
                previousPosition = previousElement.size() > 0 ? Ember.$(previousElement[0]).attr('data-position') : null,
                newPosition = parseInt(previousPosition) + 1;

            if (previousPosition) {
                if (dt.objectName === "playlist-element" &&
                    newPosition !== parseInt(dt.originalPosition) &&
                    newPosition !== parseInt(dt.originalPosition) + 1) {
                    var oldView = Ember.View.views[dt.originalHtmlId];

                    console.log('Moving', dt.relevantId, newPosition);
                    this.get('controller').send('move', Ember.Object.create({ id: dt.relevantId }), newPosition);

                    if (oldView) {
                        oldView.destroy();
                    }

                    this.$(".drop-placeholder").remove();
                    Ember.run.debounce(this, this.forceRerender, 5000);
                    event.dragEffect = "move";
                } else if (dt.objectName === "media") {
                    this.get('controller').send("insertMedia", Ember.Object.create({ id: dt.relevantId }), newPosition);
                    event.dragEffect = "copy";
                } else {
                    event.dragEffect = "none";
                }
            } else {
                event.dragEffect = "none";
            }
        } else {
            event.dragEffect = "none";
        }

        this.$(".drop-placeholder").hide();
    },

    didInsertElement: function() {
        Ember.$(document).unbind("keyup.playlist");

        Ember.$(document).bind("keyup.playlist", function(e){
            if (Ember.$("input:focus").length === 0 && Ember.$(".left-container:hover").length > 0) {
                if (e.which === this.P_KEY) {
                    this.get('controller').send('addActionBySlug', 'live');
                } else if (e.which === this.D_KEY) {
                    this.get('controller').send('addActionBySlug', 'run_studio');
                } else if (e.which === this.F_KEY) {
                    this.get('controller').send('addActionBySlug', 'end_studio');
                }
            }
        }.bind(this));


        this.$(".playlist").prepend('<div class="drop-placeholder" style="display: none"></div>');

        var dom = this.$()[0];

        dom.addEventListener("dragenter", this.dragenter.bind(this), false);
        dom.addEventListener("dragover", this.dragover.bind(this), false);
        dom.addEventListener("dragleave", this.dragleave.bind(this), false);
        dom.addEventListener("drop", this.drop.bind(this), false);
    },

    forceRerender: function() {
        this.rerender();
    }
});

