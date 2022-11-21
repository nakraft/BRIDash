'''
A static gauge per country shows how much expenditure is within that country compared to others 
'''

from branca.element import Figure, JavascriptLink, MacroElement
from jinja2 import Template

class Gauge(MacroElement):

    _template = Template(u"""
            {% macro script(this, kwargs) %}

            L.Control.Watermark = L.Control.extend({
                onAdd: function(map) {
                    var img = L.DomUtil.create('img');

                    img.src = '../static/img/gauge.png';
                    img.style.width = '350px';

                    return img;
                },

                onRemove: function(map) {
                    // Nothing to do here
                }
            });

            L.control.watermark = function(opts) {
                return new L.Control.Watermark(opts);
            }

            L.control.watermark({ position: 'bottomright' }).addTo({{this._parent.get_name()}});
            {% endmacro %}
            """)

    def __init__(self):
        super(Gauge, self).__init__()
        self._name = 'Gauge'