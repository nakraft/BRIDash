'''
When one clicks on a Map that contains a LatLngPopup,
a popup is shown that displays the latitude and longitude of the pointer.
Reference: https://gis.stackexchange.com/questions/313382/click-event-on-maps-with-folium-and-information-retrieval
'''

from branca.element import Figure, JavascriptLink, MacroElement
from jinja2 import Template

class LatLngPopup(MacroElement):

    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    console.log("Country details requested for (" + e.latlng.lat.toFixed(4) + ", " + e.latlng.lng.toFixed(4) + ").");
                    $.ajax({
                        url: "/find_country",
                        type: 'POST',
                        data: JSON.stringify({
                            "type": "point",
                            "lat": e.latlng.lat.toFixed(4), 
                            "long": e.latlng.lng.toFixed(4)
                        }),
                        contentType: 'application/json', 
                        dataType: 'json',
                        success: function(result) {
                            console.log("Details loading for: " + result['country']);
                            var c = result['country_id'];
                            nextPage(c);
                        },
                        error: function(response) {
                            console.log("ERROR");
                        }
                    });
                }
                function nextPage(country_id) {
                    console.log("Loading next page.");
                    window.location.href = '/data/' + country_id;
                }
                    
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """)  # noqa

    def __init__(self):
        super(LatLngPopup, self).__init__()
        self._name = 'LatLngPopup'