import Ember from "ember";

export default Ember.Route.extend({
    alreadySetup: false,
    previousContent: [],

    renderTemplate() {
        this.render('studio.library', {
            outlet: 'main',
            into: 'application'
        });
    },

    model: () => {
        var controller = this.controllerFor("studio.library"),
            args = { limit: controller.LIMIT_PER_PAGE },
            text = controller.get('text'),
            orderedBy = controller.get('orderedBy'),
            offset = controller.get('offset'),
            desc = controller.get('desc');

        if (!Ember.isEmpty(text)) {
            args.fulltext = text;
        }
        if (!Ember.isEmpty(orderedBy)) {
            args.sort = orderedBy;

            if (desc) {
                args.sort = ["-", args.sort].join("");
            }
        }
        if (!Ember.isEmpty(offset)) {
            args.offset = offset;
        }

        this.alreadySetup = true;

        this.store.query('media', args).then(function(medias) {
            if (!args.offset) {
                this.previousContent = [];
            }
            controller.get("meta").setProperties(medias.get('meta'));

            this.previousContent.push(medias);
            return this.previousContent;
        });
    },

    setupLibrary() {

    },

    setupController(controller, model) {
        if (!this.alreadySetup) {
            this.setupLibrary();
        }
    },

    actions: {
        refreshLibrary() {
            this.setupLibrary();
        }
    }
});
