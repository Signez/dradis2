export default function(bytes) {
    var KIO = 1024,
        MIO = KIO * 1024,
        GIO = MIO * 1024,
        round = function(number, decimals) {
            return Math.round(number * (decimals * 10)) / (decimals * 10);
        };

    if (bytes < KIO) {
        return [bytes, "o"].join(" ");
    } else if (bytes < MIO) {
        return [round(bytes / KIO, 1), "kio"].join(" ");
    } else if (bytes < GIO) {
        return [round(bytes / MIO, 1), "Mio"].join(" ");
    } else {
        return [round(bytes / GIO, 2), "Gio"].join(" ");
    }
}
