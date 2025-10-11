import streamlit as st
from streamlit_option_menu import option_menu # pip install streamlit-option-menu

# --- 1. Убираем стандартные элементы Streamlit и внедряем CSS ---
def load_css():
    st.markdown("""
        <style>
            /* Убираем стандартный header и footer от Streamlit */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Стили для карточек */
            .card {
                background-color: white;
                border-radius: 10px;
                padding: 25px;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
                margin: 10px auto;
                max-width: 800px; /* Ограничиваем ширину контента */
            }

            /* Стили для кнопок (переопределяем стандартный класс Streamlit) */
            div[data-testid="stButton"] > button {
                background-color: #1ed760; /* Ваш бирюзовый цвет */
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
            }
            div[data-testid="stButton"] > button:hover {
                background-color: #1ac859;
            }
        </style>
    """, unsafe_allow_html=True)

# Загружаем CSS в самом начале
load_css()

# --- 2. Создаем кастомную навигационную панель ---
selected_page = option_menu(
    menu_title=None, # нет заголовка
    options=["Теория", "Тесты", "Калькулятор", "Регистрация"],
    icons=['book', 'patch-check', 'calculator', 'person-plus'], # иконки из bootstrap
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1ed760"},
        "icon": {"color": "white", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#1ac859", "color": "white"},
        "nav-link-selected": {"background-color": "#15a448"},
    }
)

# --- 3. Отображаем контент в зависимости от выбранной страницы ---
if selected_page == "Теория":
    st.markdown("""
        <div class="card">
            <h1>Neyman-Pearson Criterion</h1>
            <h3>Introduction</h3>
            <p>The Neyman-Pearson criterion is a fundamental concept in statistical hypothesis testing...</p>
        </div>
    """, unsafe_allow_html=True)

elif selected_page == "Тесты":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Multiple Choice Questions")
    answer = st.radio(
        "Choose the correct statement regarding the Neyman-Pearson criterion.",
        ('A', 'B', 'C', 'D'),
        label_visibility="collapsed" # Скрываем заголовок
    )
    if st.button("Submit Answer", key="q1"):
        # Логика проверки ответа
        pass
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Регистрация":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Регистрация")
    name = st.text_input("Имя")
    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")
    if st.button("Зарегистрироваться"):
        # Логика регистрации
        st.success("Вы успешно зарегистрированы!")
    st.markdown('</div>', unsafe_allow_html=True)