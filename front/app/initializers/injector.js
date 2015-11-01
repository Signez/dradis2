import StatusService from "app/services/status";
import CommandService from "app/services/command";
import ClockService from "app/services/clock";

export default {
    name: 'injector',
    initialize: function(container, application) {
        application.register('service:status', StatusService);
        application.register('service:command', CommandService);
        application.register('service:clock', ClockService);

        application.inject('service:status', 'clock', 'service:clock');
        application.inject('service:command', 'status', 'service:status');
        application.inject('model:playlist_element', 'clock', 'service:clock');
        application.inject('model:studio', 'clock', 'service:clock');
        application.inject('model:file', 'clock', 'service:clock');
        application.inject('controller:status-bar', 'status', 'service:status');
        application.inject('controller:playlist', 'status', 'service:status');
        application.inject('controller:studio.console', 'status', 'service:status');
        application.inject('controller:studio.recorders', 'status', 'service:status');
        application.inject('controller:studio', 'status', 'service:status');
        application.inject('controller:upload-dialog', 'status', 'service:status');
        application.inject('controller', 'command', 'service:command');

        application.inject('component:playlist-element', 'command', 'service:command');

    }
};
