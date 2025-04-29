import streamlit as st
import os

# Folder jisme images stored hain
image_folder = "coin_images"

# Streamlit UI
st.title("Crypto Coin Image Search")

# User se coin ID input lena
coin_id = st.text_input("Enter Coin ID (e.g., bitcoin, ethereum):")

# Image dikhana agar available ho
if coin_id:
    image_path = os.path.join(popular_coin_images, f"{coin_id.lower()}.png")
    if os.path.exists(image_path):
        st.image(image_path, width=200)
    else:
        st.error("⚠ Coin image not found!")
        