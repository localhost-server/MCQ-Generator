import streamlit as st
from streamlit import session_state as ss

st.header("Session Counter")
if "counter" not in ss:
    ss.counter = 0

increment,decrement = st.columns(2)
with increment:
    increment = st.button("Increment")

with decrement:
    decrement = st.button("Decrement")
if increment:
    ss.counter += 1

if decrement:
    ss.counter -= 1

st.write(f"Counter: { ss.counter} ")