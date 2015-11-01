/* global require, module */
var EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function (defaults) {
    var app = new EmberApp(defaults, {
        tests: false,
        storeConfigInMeta: false,
        wrapInEval: false,
        trees: {
            files: []
        }
    });

    app.import('bower_components/moment/moment.js', {});
    app.import('bower_components/moment-duration-format/lib/moment-duration-format.js', {});
    app.import('bower_components/jquery.animate-enhanced/jquery.animate-enhanced.min.js', {});
    app.import('bower_components/underscore/underscore-min.js', {});
    app.import('vendor/bootstrap.min.js', {});

    return app.toTree();
};
