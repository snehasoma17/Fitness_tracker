import streamlit as st
from langchain_ollama import ChatOllama

st.title("💪 AI Workout Planner")

age = st.number_input("Age")
weight = st.number_input("Weight")

goal = st.selectbox(
    "Goal",
    [
        "Weight Loss",
        "Muscle Gain",
        "Strength"
    ]
)

days = st.slider(
    "Workout Days",
    1,
    7,
    4
)

if st.button("Generate Plan"):

    llm = ChatOllama(
        model="llama3.2"
    )

    prompt = f"""
    Create a {days}-day workout plan.

    Age:{age}
    Weight:{weight}
    Goal:{goal}

    Include:
    Exercises
    Reps
    Sets
    Cardio
    Weekly Schedule
    """

    response = llm.invoke(prompt)

    st.write(
        response.content
    )