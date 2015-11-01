var FILENAME_REGEX = /(.*)_(show|gold)_([0-9A-Za-z_]+)_(\d+)-(\d+)-(\d+)_(\d+)-(\d+)-(\d+)\.(...?.?.?)/;

function parseFilename(filename) {
    var matches = filename.match(FILENAME_REGEX);

    if (matches !== null) {
        console.log(matches);
        return {
            slug: matches[1],
            type: matches[2],
            studio: matches[3],
            datetime: moment({
                years: +matches[4],
                months: +matches[5] - 1,
                days: +matches[6],
                hours: +matches[7],
                minutes: +matches[8],
                seconds: +matches[9]
            })
        };
    }
}

export default {
    recordDatetime: function(filename) {
        var parsed = parseFilename(filename);

        if (parsed) {
            return parsed.datetime.format("ddd Do MMM YYYY, HH:mm:ss");
        }
    },
    recordType: function(filename) {
        var parsed = parseFilename(filename);

        if (parsed) {
            return parsed.type;
        }
    },
    recordSlug: function(filename) {
        var parsed = parseFilename(filename);

        if (parsed) {
            return parsed.slug;
        }
    },
    recordStudio: function(filename) {
        var parsed = parseFilename(filename);

        if (parsed) {
            return parsed.studio;
        }
    }
};
