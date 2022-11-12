$.extend($.ui.slider.prototype.options, {
    animate: 300
});

$("#flat-slider")
    .slider({
        max: timeline_details.max,
        min: timeline_details.min,
        range: true,
        values: timeline_details.starting_values,
        labels: true
    })
    .slider("pips", {
        first: "label",
        last: "label",
        rest: "label",
        labels: timeline_details.labels
    });

$("#flat-slider").slider({
    change: function (event, ui) {
        var start_value = $("#flat-slider").slider("values")[0]; // use start/end value to filter stuff
        var end_value = $("#flat-slider").slider("values")[1];
        
        newtimerange(start_value, end_value);
    }
    });