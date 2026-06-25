import sqlite3

import streamlit as st

st.title("👤 User Profile")

username = st.text_input("Enter Username")

if username:
    conn = sqlite3.connect("fitness.db")

    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT *
    FROM users
    WHERE username=?
    """,
        (username,),
    )

    user = cursor.fetchone()

    if user:
        st.metric("Age", user[3])

        st.metric("Height", user[5])

        st.metric("Weight", user[6])

        st.metric("Goal", user[7])

        bmi = user[6] / ((user[5] / 100) ** 2)

        st.metric("BMI", f"{bmi:.2f}")
