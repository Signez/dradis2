import Ember from "ember";

export default Ember.Controller.extend({
    kind: "",

    unknownKind: Ember.computed.empty("kind"),

    musicKind: Ember.computed.equal("kind", "music"),
    oneShotKind: Ember.computed.equal("kind", "one_shot"),
    utilityKind: Ember.computed.equal("kind", "utility"),

    modalTitle: function() {
        if (this.get('tagging')) {
            return "Ajouter des fichiers à la bibliothèque";
        } else if (this.get('musicKind')) {
            return "Téléverser de la musique";
        } else if (this.get('oneShotKind')) {
            return "Téléverser des reportages";
        } else if (this.get('utilityKind')) {
            return "Téléverser des sons utilitaires";
        } else {
            return "Téléverser des fichiers";
        }
    }.property('musicKind', 'oneShotKind', 'utilityKind', 'tagging'),

    knownKind: Ember.computed.not("unknownKind"),

    waitingDrop: Ember.computed.and("knownKind", "filesNeeded", "uploadNeeded"),

    cancelleable: Ember.computed.not("uploading"),

    canCancel: Ember.computed.and("cancelleable", "cantBack"),

    uploadFinished: false,
    uploadNeeded: Ember.computed.not("uploadFinished"),

    uploadProgressNeeded: Ember.computed.or("uploadNeeded", "needReview"),
    uploading: Ember.computed.and("knownKind", "filesSelected", "uploadProgressNeeded"),

    tagged: false,
    needTagging: Ember.computed.not("tagged"),

    reviewed: true,
    needReview: Ember.computed.not("reviewed"),

    canReview: false,
    canTerminate: false,

    tagging: Ember.computed.and("reviewed", "uploadFinished", "needTagging"),
    inspecting: Ember.computed.notEmpty('inspectedFile'),

    filesToUpload: [],
    filesNeeded: Ember.computed.empty("filesToUpload"),
    filesSelected: Ember.computed.not("filesNeeded"),

    canBack: Ember.computed.notEmpty('inspectedFile'),
    cantBack: Ember.computed.not("canBack"),
    canContinue: Ember.computed.and('inspecting', 'inspectedFile.analyzed', 'inspectedFile.completeTags'),

    waitingUploadedFiles: Ember.computed.alias("status.waitingUploadedFiles"),
    hasWaitingUploadedFiles: Ember.computed.notEmpty("waitingUploadedFiles"),

    inspectedFile: function() {
        return this.get('taggingFiles').findBy('inspected', true);
    }.property('taggingFiles.@each.inspected'),

    taggingFiles: Ember.A([]),

    didWaitingUploadedFilesChange: function() {
        if (this.get('taggingFiles').length) {
            this.set('taggingFiles', this.get('taggingFiles').filterBy('inspected'));
        }

        this.get('taggingFiles').pushObjects(
            this.get('waitingUploadedFiles')
                .rejectBy('filename', this.get('taggingFiles.firstObject.filename'))
                .map(function(file) {
                    return this.container.lookupFactory('model:file').create({
                        filename: file.filename,
                        size: file.size,
                        url: file.url
                    });
                }.bind(this))
        );

        this.set('taggingFiles', this.get('taggingFiles').sortBy('humanFilename'));
    }.observes('waitingUploadedFiles'),

    didProgress: function(event, file) {
        file.set('uploading', true);
        file.set('uploadedSize', event.loaded);
    },

    didUpload: function(file) {
        file.set('uploadedSize', file.get('rawFile').size);
        file.set('uploading', false);
        file.set('uploaded', true);
        file.set('success', true);
    },

    didUploadFailed: function(file, errorMessage) {
        file.set('uploading', false);
        file.set('uploaded', true);
        file.set('success', false);
        file.set('uploadErrorMessage', errorMessage);
        this.set('reviewed', false);
    },

    analyzeFile: function(file) {
        this.get('command')
            .post('/api/analyze', {
                GET: {
                    filename: file.get("filename")
                }
            })
            .then(function(data) {
                if (data.status !== "done") {
                    // FIXME: Better error handling
                    console.log("Error while analyzing file", data);
                } else {
                    delete data.status;
                    file.set("analyzedTags", data);
                    file.set("analyzed", true);
                    file.setProperties(data);
                }
            });
    },

    _addFileToLibrary: function(file) {
        this.get('command')
            .post('/api/library/add', {
                GET: {
                    filename: file.get("filename")
                },
                POST: {
                    tags: JSON.stringify(file.get('tags'))
                }
            })
            .then(function(data) {
                if (data.status !== "done") {
                    console.log("Error while adding file to library", data);
                } else {
                    file.set('inspected', false);
                    file.set('addedToLibrary', true);

                    if (this.get('waitingUploadedFiles')
                            .rejectBy('filename', file.get('filename'))
                            .length === 0) {
                        this.resetContent();
                        this.target.send('closeModal');
                    }
                }
            }.bind(this));
    },

    _uploadNext: function() {
        var nextFile = this.get('filesToUpload').findBy('uploaded', false);

        if (!nextFile) {
            var hasFailure = this.get('filesToUpload').findBy('success', false),
                hasSuccess = this.get('filesToUpload').findBy('success', true);

            if (hasSuccess) {
                if (hasFailure) {
                    this.set('canReview', true);
                }
                this.set('uploadFinished', true);
                this.didWaitingUploadedFilesChange();
            } else {
                this.set('canTerminate', true);
            }
        } else {
            var formData = new FormData();
            formData.append("file", nextFile.rawFile);

            nextFile.set('uploading', true);
            nextFile.set('uploadStartedAt', moment().unix());

            Ember.$.ajax({
                url: ["/api/upload?kind=", this.get('kind')].join(''),
                method: "POST",
                contentType: false,
                processData: false,
                data: formData,

                xhr: function() {
                    var xhr = Ember.$.ajaxSettings.xhr();
                    xhr.upload.onprogress = function (event) {
                        this.didProgress(event, nextFile);
                    }.bind(this);
                    return xhr;
                }.bind(this),

                success: function(response) {
                    if (response.status === "done") {
                        this.didUpload(nextFile);
                    } else {
                        this.didUploadFailed(nextFile, response.error_message);
                    }
                }.bind(this),

                error: function(jqueryXhr, status) {
                    this.didUploadFailed(nextFile, status);
                }.bind(this),

                complete: function() {
                    Ember.run.next(this, this._uploadNext);
                }.bind(this)
            });
        }
    },

    _startUpload: function() {
        this._uploadNext();
    },

    _jumpToTagging: function() {
        this.setProperties({
            kind: "indifferent",
            tagged: false,
            reviewed: true,
            uploadFinished: true
        });
        this.didWaitingUploadedFilesChange();
    },

    resetContent: function() {
        this.setProperties({
            kind: "",
            tagged: false,
            reviewed: true,
            canReview: false,
            canTerminate: false,
            uploadFinished: false,
            filesToUpload: []
        });
    },

    actions: {
        setKind: function(kind) {
            this.set("kind", kind);
        },

        upload: function(files) {
            this.set("filesToUpload", files);
            this._startUpload();
        },

        inspectFile: function(file) {
            file.set('inspected', true);
            this.analyzeFile(file);
        },

        addCurrentFileToLibrary: function() {
            this._addFileToLibrary(this.get('inspectedFile'));
        },

        back: function() {
            this.set('inspectedFile.inspected', false);
        },

        jumpToTagging: function() {
            this._jumpToTagging();
        },

        markAsReviewed: function() {
            this.set("reviewed", true);
        },

        closeModal: function() {
            this.resetContent();
            this.target.send("closeModal");
        }
    }
});
