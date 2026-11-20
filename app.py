import streamlit as st

st.set_page_config(
    page_title = "Panel de Ventanas",
    page_icon = "material/analytics",
    layout = "wide",
    initial_sidebar_state = "expanded",
    menu_items = {
        "Get help": "https://docs.streamlit.io",
        "Report a bug": None,
        "About": "Panel interno de ventas, version beta 0.1",
    },
)

st.title ("Panel de Ventas")
