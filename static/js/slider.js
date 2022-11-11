$.extend($.ui.slider.prototype.options, {
    animate: 300
});

$("#flat-slider")
    .slider({
        max: timeline_details['max'],
        min: timeline_details['min'],
        range: true,
        values: timeline_details['starting_values'],
        labels: true
    })
    .slider("pips", {
        first: "label",
        last: "label",
        rest: "label",
        labels: timeline_details['labels']
    });