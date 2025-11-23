import os
import streamlit.components.v1 as components

# Path to the frontend folder
_component_func = components.declare_component(
    "ga_inject",
    path=os.path.join(os.path.dirname(__file__), "ga_frontend")
)

def inject():
    """Inject the GA4 top-level script."""
    return _component_func()
