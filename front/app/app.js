import Ember from 'ember';
import Resolver from 'ember/resolver';
import loadInitializers from 'ember/load-initializers';
import config from 'app/config/environment';
import durationHelper from './helpers/duration';
import bytesHelper from './helpers/bytes';
import recordHelpers from './helpers/record';

Ember.Inflector.inflector.uncountable('media');

Ember.MODEL_FACTORY_INJECTIONS = true;
Ember.FEATURES['ember-routing-drop-deprecated-action-style'] = true;

var App = Ember.Application.extend({
  modulePrefix: config.modulePrefix,
  podModulePrefix: config.podModulePrefix,
  Resolver: Resolver
});

loadInitializers(App, config.modulePrefix);

Ember.Handlebars.registerBoundHelper('duration', durationHelper);
Ember.Handlebars.registerBoundHelper('bytes', bytesHelper);
Ember.Handlebars.registerBoundHelper('record-datetime', recordHelpers.recordDatetime);
Ember.Handlebars.registerBoundHelper('record-type', recordHelpers.recordType);
Ember.Handlebars.registerBoundHelper('record-slug', recordHelpers.recordSlug);
Ember.Handlebars.registerBoundHelper('record-studio', recordHelpers.recordStudio);

// moment.js locale configuration
// locale : french (fr)
// author : John Fischer : https://github.com/jfroffice

// …this should definitly not be there

moment.defineLocale('fr', {
    months : 'janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split('_'),
    monthsShort : 'janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.'.split('_'),
    weekdays : 'dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi'.split('_'),
    weekdaysShort : 'dim._lun._mar._mer._jeu._ven._sam.'.split('_'),
    weekdaysMin : 'Di_Lu_Ma_Me_Je_Ve_Sa'.split('_'),
    longDateFormat : {
        LT : 'HH:mm',
        L : 'DD/MM/YYYY',
        LL : 'D MMMM YYYY',
        LLL : 'D MMMM YYYY LT',
        LLLL : 'dddd D MMMM YYYY LT'
    },
    calendar : {
        sameDay: '[Aujourd\'hui à] LT',
        nextDay: '[Demain à] LT',
        nextWeek: 'dddd [à] LT',
        lastDay: '[Hier à] LT',
        lastWeek: 'dddd [dernier à] LT',
        sameElse: 'L'
    },
    relativeTime : {
        future : 'dans %s',
        past : 'il y a %s',
        s : 'quelques secondes',
        m : 'une minute',
        mm : '%d minutes',
        h : 'une heure',
        hh : '%d heures',
        d : 'un jour',
        dd : '%d jours',
        M : 'un mois',
        MM : '%d mois',
        y : 'un an',
        yy : '%d ans'
    },
    ordinal : function (number) {
        return number + (number === 1 ? 'er' : '');
    },
    week : {
        dow : 1, // Monday is the first day of the week.
        doy : 4  // The week that contains Jan 4th is the first week of the year.
    }
});

export default App;
