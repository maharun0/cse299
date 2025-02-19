import streamlit as st

# Title of the app
st.title('Simple Streamlit Frontend')

# Add a text input for user to input their name
name = st.text_input('Enter your name')

# Display a message when the user inputs their name
if name:
    st.write(f'Hello, {name}!')
else:
    st.write('Please enter your name.')

# Add a slider to select a number
number = st.slider('Select a number', 1, 10)

# Display the selected number
st.write(f'You selected: {number}')

# Add a button that when clicked, shows a message
if st.button('Click me'):
    st.write('Button clicked!')
