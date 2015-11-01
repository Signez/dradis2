import Ember from 'ember';
import config from 'app/config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

export default Router.map(function() {
    this.resource('studio', { path: '/studio/:id' }, function() {
        this.route('dashboard');
        this.route('library');
        this.route('recorders');
        this.route('console');
    });
});
