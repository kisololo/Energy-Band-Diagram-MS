import streamlit.components.v1 as components
import os

_component_func = components.declare_component(
    "ga_inject",
    path=os.path.join(os.path.dirname(__file__), "ga_frontend"),
)

def inject():
    return _component_func(default=1)
