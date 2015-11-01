export default function(seconds) {
    if (seconds === Infinity) {
        return "∞";
    } else if (seconds === undefined || seconds === null) {
        return "-:--";
    }

    var duration = moment.duration(Math.round(seconds), 'seconds');

    if (duration.asSeconds() >= 3600) {
       return duration.format({ template: 'hh:mm:ss' });
    } else {
       return duration.format({ template: 'm:ss', trim: false });
    }
}
