import streamlit as st
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-pro")

# Set page configuration for responsiveness
st.set_page_config(page_title="AI Quiz Generator", page_icon="🎓", layout="wide")

# Welcome Message & Branding
st.markdown("""
    <div style="text-align: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/1903/1903162.png" width="100">
        <h1 style="color: #2E86C1;">✨ AI-Powered Quiz Generator 🎓</h1>
        <h3>📢 Welcome to the Future of Learning! 🚀</h3>
        <p style="font-size:18px;">
            Convert any text into **interactive multiple-choice quizzes** instantly. 
            Whether you're a **student, teacher, or self-learner**, this tool will help 
            you **enhance engagement, save time, and make learning more effective!**
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1903/1903162.png", width=80)
st.sidebar.title("📌 App Navigation")
st.sidebar.markdown("""
- **About This App**: AI-powered quiz generator creates **multiple-choice quizzes** from any text.
- **Settings Menu**: Choose difficulty level, number of questions & customize your quiz experience.
- **Quiz Features**: Get instant feedback, track progress & improve your knowledge!
""")

# Function to generate questions
@st.cache_data
def fetch_questions(text_content, quiz_level, num_questions):
    RESPONSE_JSON = {
        "mcqs": [
            {
                "mcq": "Sample question",
                "options": {
                    "a": "Option 1",
                    "b": "Option 2",
                    "c": "Option 3",
                    "d": "Option 4",
                },
                "correct": "a"
            }
        ]
    }

    PROMPT_TEMPLATE = f"""
    You are an expert in generating MCQ quizzes based on provided content.
    Given the text below, generate a quiz with {num_questions} multiple-choice questions at the '{quiz_level}' difficulty level.

    Text: {text_content}

    The format should strictly match this JSON:
    {json.dumps(RESPONSE_JSON, indent=2)}
    """

    response = model.generate_content(PROMPT_TEMPLATE)

    try:
        extracted_response = json.loads(response.text)
        return extracted_response.get("mcqs", [])
    except json.JSONDecodeError:
        return []  # Return an empty list if JSON fails

def main():
    # Educational Importance Section
    with st.expander("📚 **Why is this App Important in Education?**"):
        st.write("""
        - **Enhances Learning**: Practice and reinforce knowledge through AI-generated quizzes.
        - **Saves Time**: Instantly generate quizzes instead of manually creating them.
        - **Personalized Learning**: Adjust quiz difficulty & customize based on learners' needs.
        - **Improves Engagement**: Interactive quizzes make learning **fun & effective!**
        """)

    # User input section (better layout for mobile devices)
    text_content = st.text_area("📄 Paste your text here:", height=150, help="Enter content to generate questions from.")

    # Select options in a single row for better mobile support
    col1, col2 = st.columns(2)
    with col1:
        quiz_level = st.selectbox("🎚 Select difficulty:", ["Easy", "Medium", "Hard"], help="Choose difficulty level.")

    with col2:
        num_questions = st.number_input("🔢 Number of questions:", min_value=1, max_value=20, value=5, step=1, help="Set the number of MCQs to generate.")

    # Session state
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = {}

    # Generate Quiz Button
    if st.button("🚀 Generate Quiz", use_container_width=True):
        st.session_state.questions = fetch_questions(text_content, quiz_level, num_questions)
        st.session_state.quiz_generated = True
        st.session_state.selected_options = {}  # Reset answers
        st.rerun()

    # Display Quiz (Ensuring Mobile Compatibility)
    if st.session_state.quiz_generated:
        st.divider()
        st.write("## 🎯 Your Quiz")

        # Using container ensures questions display correctly on all screen sizes
        with st.container():
            with st.form(key="quiz_form"):
                for i, question in enumerate(st.session_state.questions):
                    st.markdown(f"### ❓ {i+1}. {question['mcq']}")
                    formatted_options = [f"{key}: {value}" for key, value in question["options"].items()]
                    option_key = f"question_{i}"

                    selected_option = st.radio(
                        "Select an answer:", 
                        formatted_options, 
                        key=option_key, 
                        index=None,
                        help=f"Select the correct answer for question {i+1}"
                    )

                    if selected_option:
                        st.session_state.selected_options[i] = selected_option.split(":")[0]

                # Submit Button
                submitted = st.form_submit_button("✅ Submit Answers")
        
        if submitted:
            marks = 0
            st.success("✅ Quiz Submitted Successfully!")
            st.write("### 📊 Quiz Results")

            for i, question in enumerate(st.session_state.questions):
                st.markdown(f"**Q{i+1}. {question['mcq']}**")

                selected_letter = st.session_state.selected_options.get(i)
                correct_letter = question["correct"]

                if selected_letter:
                    st.write(f"🟢 You selected: **{selected_letter.upper()} - {question['options'][selected_letter]}**")
                else:
                    st.write("❌ You didn't select an answer.")

                st.write(f"✅ Correct answer: **{correct_letter.upper()} - {question['options'][correct_letter]}**")

                if selected_letter == correct_letter:
                    marks += 1

            # Score Display
            score_percentage = (marks / len(st.session_state.questions)) * 100
            st.markdown(f"### 🎉 You scored **{marks} / {len(st.session_state.questions)}** ({score_percentage:.2f}%)")

            # Progress bar
            st.progress(score_percentage / 100)

            # 🎯 Personalized Feedback
            st.subheader("📢 Performance Feedback")
            if score_percentage == 100:
                st.success("🎯 Perfect Score! You're a genius! 🚀")
            elif score_percentage >= 80:
                st.info("🌟 Great job! Keep up the good work! 💪")
            elif score_percentage >= 50:
                st.warning("📚 Good effort! Try again to improve your score! 🔄")
            else:
                st.error("❌ Don't worry! Practice makes perfect! 😊")

        # Reset Button
        if st.button("🔄 Reset Quiz", use_container_width=True):
            st.session_state.quiz_generated = False
            st.session_state.selected_options = {}
            st.rerun()

# Run the application
if __name__ == "__main__":
    main()
