$.extend($.ui.slider.prototype.options, {
    animate: 300
});

$("#flat-slider")
    .slider({
        max: 10,
        min: 0,
        range: true,
        values: [5, 9],
        labels: true
    })
    .slider("pips", {
        first: "label",
        last: "label",
        rest: "label",
        labels: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    });

// document.getElementById("start-value").innerHTML = $("#flat-slider").slider(
//     "values"
// )[0];
// document.getElementById("end-value").innerHTML = $("#flat-slider").slider(
//     "values"
// )[1];

// $("#flat-slider").slider({
//     change: function (event, ui) {
//         document.getElementById("start-value").innerHTML = $(
//             "#flat-slider"
//         ).slider("values")[0];
//         document.getElementById("end-value").innerHTML = $(
//             "#flat-slider"
//         ).slider("values")[1];
//     }
// });