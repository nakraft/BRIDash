'''
When one clicks on the home button, the map is recentered for the current country. 
'''

from branca.element import Figure, JavascriptLink, MacroElement
from jinja2 import Template

class HomeButton(MacroElement):

    _template = Template(u"""
            {% macro script(this, kwargs) %}

            L.easyButton('fa-home fa-lg', function(btn, map){
                var point = {{this._bounds}};
                map.fitBounds(point);
            }).addTo({{this._parent.get_name()}});

            {% endmacro %}
            """)

    def __init__(self, bounds):
        super(HomeButton, self).__init__()
        self._name = 'HomeButton'
        self._bounds = bounds