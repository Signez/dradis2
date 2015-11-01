import Ember from "ember";

export default Ember.Component.extend({
    tagName: "p",
    classNames: ["file-drop-zone"],
    classNameBindings: ["dragging:active"],

    dragging: false,

    dragenter: function (event) {
        if (event.dataTransfer.types.contains("Files")) {
            this.set("dragging", true);
        }

        this.$(".drop-overlay").show();
        event.stopPropagation();
        event.preventDefault();
    },

    dragleave: function (event) {
        this.$(".drop-overlay").hide();
        this.set("dragging", false);
        event.stopPropagation();
        event.preventDefault();
    },

    dragover: function (event) {
        event.stopPropagation();
        event.preventDefault();
    },

    drop: function (event) {
        this.$(".drop-overlay").hide();
        this.set("dragging", false);

        var dt = event.dataTransfer;
        this.handleFiles(dt.files);

        event.stopPropagation();
        event.preventDefault();
    },

    fileSelected: function(event) {
        this.handleFiles(event.target.files);
    },

    handleFiles: function(files) {
        if (files && files.length) {
            var filesToSend = Ember.A([]);

            for (var i = 0; i < files.length; i++) {
                var file = files[i];

                //FIXME: Add file type pre-check

                filesToSend.pushObject(this.container.lookupFactory('model:file').create({
                    rawFile: file
                }));
            }

            this.sendAction('upload', filesToSend);
        }
    },

    didInsertElement: function() {
        this.$()
            .append('<div class="drop-overlay"></div>')
            .append('<input class="file-selector" type="file" multiple accept="audio/*" />');

        var overlay = this.$(".drop-overlay")[0],
            fileSelector = this.$(".file-selector")[0],
            dom = this.$()[0];

        dom.addEventListener("dragenter", this.dragenter.bind(this), false);
        dom.addEventListener("dragover", this.dragover.bind(this), false);
        overlay.addEventListener("dragleave", this.dragleave.bind(this), false);
        overlay.addEventListener("drop", this.drop.bind(this), false);
        fileSelector.addEventListener("change", this.fileSelected.bind(this), false);
    },

    // HACK: Necessary to be able to catch events from yielded content
    _yield: function (context, options) {
        var get = Ember.get,
            view = options.data.view,
            parentView = this._parentView,
            template = get(this, 'template');

        if (template) {
            Ember.assert("A Component must have a parent view in order to yield.", parentView);
            view.appendChild(Ember.View, {
                isVirtual: true,
                tagName: '',
                _contextView: parentView,
                template: template,
                context: get(view, 'context'), // the default is get(parentView, 'context'),
                controller: get(view, 'controller'), // the default is get(parentView, 'context'),
                templateData: { keywords: parentView.cloneKeywords() }
            });
        }
    },

    actions: {
        manualSelect: function() {
            this.$(".file-selector").click();
        }
    }
});
