import streamlit as st

# 실제 서비스에서는 보안을 위해 비밀번호를 해싱하거나 secrets에 저장하세요.
USER_ID = "admin"
USER_PW = "1234"

def login_screen():
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px; margin: auto; padding: 40px;
            background-color: white; border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔐 맛집 큐레이터 로그인")
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        input_user = st.text_input("아이디")
        input_pw = st.text_input("비밀번호", type="password")
        
        if st.button("로그인"):
            if input_user == USER_ID and input_pw == USER_PW:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 틀렸습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state['authenticated'] = False
    st.rerun()