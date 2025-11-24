import streamlit.components.v1 as components
import os

# Declare Streamlit component
_component_func = components.declare_component(
    "ga_inject",
    path=os.path.join(os.path.dirname(__file__), "ga_frontend")
)

def inject():
    # We don't need to send data; just initialize component
    return _component_func()
