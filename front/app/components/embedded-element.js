import Ember from "ember";

export default Ember.Component.extend({
    tagName: "div",
    classNames: ["embedded-element"],
    classNameBindings: ["kind"],

    kind: "bed",

    polarToCartesian(centerX, centerY, radius, angleInDegrees) {
      var angleInRadians = (angleInDegrees-90) * Math.PI / 180.0;

      return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
      };
    },

    describeArc(x, y, radius, startAngle, endAngle){
        var start = this.polarToCartesian(x, y, radius, endAngle),
            end = this.polarToCartesian(x, y, radius, startAngle),
            arcSweep = endAngle - startAngle <= 180 ? "0" : "1";

        return [
            "M", x, y,
            "L", start.x, start.y,
            "A", radius, radius, 0, arcSweep, 0, end.x, end.y,
            'M', x, y,
            'Z'
        ].join(" ");
    },

    visualClockArc: function() {
        return this.describeArc(25, 25, 24, 0, Math.min(360, this.get('elapsed') / this.get('length') * 360));
    }.property('elapsed', 'length')
});
