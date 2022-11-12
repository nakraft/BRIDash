'''
When one clicks on the query/export tool, the correct HTML pops  up to support map functionality. 

Inclusive of: 
- query capabilities
- interactive data filtering 
- adding observation 
- exporting data 
'''

from branca.element import Figure, JavascriptLink, MacroElement
from jinja2 import Template

class UserInteractPopup(MacroElement):

    _template = Template(u"""
            {% macro script(this, kwargs) %}

            L.Control.Watermark = L.Control.extend({
                onAdd: function(map) {
                    var img = L.DomUtil.create('img');

                    img.src = '../img/LAS_logo_fullcolor.png';
                    img.style.width = '200px';

                    return img;
                },

                onRemove: function(map) {
                    // Nothing to do here
                }
            });

            L.control.watermark = function(opts) {
                return new L.Control.Watermark(opts);
            }

            # L.control.watermark({ position: 'bottomleft' }).addTo(map);
            {% endmacro %}
            """)

    def __init__(self):
        super(UserInteractPopup, self).__init__()
        self._name = 'UserInteractPopup'

