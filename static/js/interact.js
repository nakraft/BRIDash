// implements functionality for custom queries, export and filtering

// function clickForInteractPopup(e) {
//     console.log("Query Interactivity Menu Open");
//     window.open("interact.html","Rating","width=550,height=170,left=150,top=200,toolbar=0,status=0,");
// }

// function clicking() {
//     const targetDiv = document.getElementById("query_menu_options");
//     if (targetDiv.style.display !== "none") {
//         targetDiv.style.display = "none";
//     } else {
//         targetDiv.style.display = "block";
//     }
// };

// var map = L.map('official_map');

L.control.custom({
    position: 'bottomleft',
    content : '<div class="panel-body">'+
              '    <div class="progress" style="margin-bottom:0px;">'+
              '        <div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="41" '+
              '             aria-valuemin="0" aria-valuemax="100" style="min-width: 2em; width: 41%">'+
              '            41% Completed'+
              '        </div>'+
              '    </div>'+
              '</div>',
    classes : 'panel panel-default',
    style   :
    {
        width: '200px',
        margin: '20px',
        padding: '0px',
    },
})
.addTo(map);