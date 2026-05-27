import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import datetime
import time
import google.generativeai as genai

# ==========================================
# [초기 설정] 페이지 세팅
# ==========================================
st.set_page_config(page_title="스마트 마음 상담 센터", page_icon="🌙", layout="wide")

# ==========================================
# [Gemini AI 설정] 
# ==========================================
GEMINI_API_KEY = "AIzaSyBOagoX1FvOaIVdyA2xeTqzERYGuunLR_Y"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro') 

# ==========================================
# [데이터베이스 설정] SQLite3
# ==========================================
conn = sqlite3.connect('mind_care_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS counseling_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, worry TEXT, answer TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS dday_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, target_date TEXT)''')
conn.commit()

# ==========================================
# [CSS] 서울남산체 웹 폰트 적용 및 UI/UX 디자인
# ==========================================
st.markdown("""
<style>
    /* 서울남산체 웹 폰트 불러오기 */
    @font-face {
        font-family: 'SeoulNamsan';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/SeoulNamsanM.woff') format('woff');
        font-weight: normal; font-style: normal;
    }

    /* 전체 요소에 서울남산체 강제 적용 */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp table, .stApp th, .stApp td {
        font-family: 'SeoulNamsan', sans-serif !important;
    }

    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    
    .neon-title {
        font-size: 55px; font-weight: 900; color: #ffffff; text-align: center;
        margin-top: 20px; margin-bottom: 10px; letter-spacing: 2px;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #c084fc, 0 0 40px #c084fc, 0 0 80px #c084fc, 0 0 90px #c084fc;
    }
    .sub-title { color: #e2e8f0; font-size: 20px; margin-bottom: 40px; font-weight: 500; text-align: center; }
    
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        background-color: #1e293b !important; border: 2px solid #c084fc !important; border-radius: 10px !important;
    }
    input, textarea { color: #ffffff !important; font-size: 18px !important; font-weight: bold !important; }
    label { color: #fbcfe8 !important; font-size: 18px !important; font-weight: bold !important; }

    /* 라디오 버튼 텍스트 색상을 흰색으로 강제 변경 */
    div[role="radiogroup"] label p { color: #ffffff !important; font-size: 17px !important; }

    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(45deg, #4f46e5, #9333ea) !important; 
        color: #ffffff !important; 
        font-weight: 900 !important; font-size: 18px !important; padding: 10px 20px !important;
        border: none !important; border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.5) !important; transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { 
        transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(147, 51, 234, 0.8) !important; 
    }

    .post-it-container { display: flex; justify-content: center; gap: 25px; margin-bottom: 50px; flex-wrap: wrap; }
    .post-it {
        width: 200px; padding: 25px 20px; color: #1e293b; font-size: 18px; font-weight: 900; text-align: center; 
        border-radius: 2px 15px 15px 2px; box-shadow: 5px 5px 20px rgba(0,0,0,0.4); position: relative;
    }
    .post-it::before {
        content: ""; position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
        width: 50px; height: 20px; background: rgba(255,255,255,0.5); box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .p1 { transform: rotate(-4deg); background: #fef08a; }
    .p2 { transform: rotate(3deg); background: #bbf7d0; }
    .p3 { transform: rotate(-3deg); background: #fbcfe8; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.05); border-radius: 8px 8px 0 0; padding: 10px 20px; color: #cbd5e1; font-size: 18px; }
    .stTabs [aria-selected="true"] { background-color: rgba(192, 132, 252, 0.2); color: #fbcfe8 !important; border-bottom: 3px solid #c084fc; font-weight: bold; }

    .record-card { background: rgba(255,255,255,0.05); border-left: 5px solid #c084fc; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .record-date { color: #fbcfe8; font-size: 14px; font-weight: bold; margin-bottom: 10px; }
    .record-worry { color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 15px; line-height: 1.6; }
    .record-answer { color: #e2e8f0; font-size: 17px; background: rgba(0,0,0,0.4); padding: 20px; border-radius: 10px; line-height: 1.7; }
    
    .chat-user { text-align: right; margin-bottom: 15px; }
    .chat-user span { background-color: #334155; padding: 12px 20px; border-radius: 20px 20px 0 20px; display: inline-block; font-size: 17px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .chat-ai { text-align: left; margin-bottom: 25px; }
    .chat-ai span { background-color: rgba(192, 132, 252, 0.15); border: 1px solid #c084fc; padding: 15px 20px; border-radius: 20px 20px 20px 0; display: inline-block; font-size: 17px; line-height: 1.7; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }

    .counseling-table {
        width: 100%; max-width: 900px; margin: 50px auto; border-collapse: collapse;
        background-color: rgba(255, 255, 255, 0.03); color: #e2e8f0; font-size: 15px;
        text-align: center; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .counseling-table th { background: linear-gradient(45deg, #3b82f6, #8b5cf6); color: #ffffff; padding: 15px; font-weight: 900; border: 1px solid rgba(255, 255, 255, 0.1); font-size: 16px; }
    .counseling-table td { padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1); vertical-align: middle; line-height: 1.5; }
    .counseling-table tr:hover { background-color: rgba(255, 255, 255, 0.08); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리]
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_id' not in st.session_state: st.session_state['user_id'] = ""
if 'id_checked' not in st.session_state: st.session_state['id_checked'] = False
if 'valid_id' not in st.session_state: st.session_state['valid_id'] = ""
if 'chat_session' not in st.session_state: st.session_state['chat_session'] = [] 

# ==========================================
# [화면 구성] 1. 로그인 / 회원가입 화면
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("<div class='neon-title'>스마트 마음 상담소</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>당신의 지친 하루를 따뜻하게 안아드릴게요. 편하게 기대어 보세요.</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="post-it-container">
        <div class="post-it p1">"괜찮아,<br>다 잘 될 거야 💛"</div>
        <div class="post-it p2">"오늘 하루도<br>정말 수고했어 🌿"</div>
        <div class="post-it p3">"넌 충분히<br>빛나고 있어 ✨"</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])
        with auth_tab1:
            login_id = st.text_input("아이디를 입력하세요", key="login_id")
            login_pw = st.text_input("비밀번호를 입력하세요", type="password", key="login_pw")
            st.write("") 
            if st.button("로그인 하기", use_container_width=True):
                c.execute("SELECT * FROM users WHERE user_id=? AND password=?", (login_id, login_pw))
                if c.fetchone():
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = login_id
                    st.session_state['chat_session'] = [] 
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                    
        with auth_tab2:
            reg_id = st.text_input("사용할 아이디", key="reg_id")
            if st.button("아이디 중복 확인"):
                if reg_id.strip() == "": st.warning("아이디를 입력해주세요.")
                else:
                    c.execute("SELECT * FROM users WHERE user_id=?", (reg_id,))
                    if c.fetchone():
                        st.error("이미 사용 중인 아이디입니다.")
                        st.session_state['id_checked'] = False
                    else:
                        st.success("사용 가능한 아이디입니다!")
                        st.session_state['id_checked'] = True
                        st.session_state['valid_id'] = reg_id
            
            reg_pw = st.text_input("사용할 비밀번호", type="password", key="reg_pw")
            reg_pw_confirm = st.text_input("비밀번호 다시 입력", type="password", key="reg_pw_confirm")
            st.write("")
            if st.button("가입 완료하기", use_container_width=True):
                if not st.session_state['id_checked'] or st.session_state['valid_id'] != reg_id:
                    st.error("아이디 중복 확인을 완료해주세요.")
                elif reg_pw == "" or reg_pw != reg_pw_confirm:
                    st.error("비밀번호가 일치하지 않거나 비어있습니다.")
                else:
                    c.execute("INSERT INTO users (user_id, password) VALUES (?, ?)", (reg_id, reg_pw))
                    conn.commit()
                    st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인해주세요.")
                    st.session_state['id_checked'] = False

    st.markdown("""
    <table class="counseling-table">
        <thead>
            <tr><th>지역</th><th>근무지</th><th>장소</th><th>상담사명</th><th>운영시간</th></tr>
        </thead>
        <tbody>
            <tr>
                <td rowspan="4" style="font-weight: bold; color: #fbcfe8;">포항</td>
                <td>포항본사</td><td rowspan="2">늘푸른솔커뮤니티센터<br>1층 회의실</td><td rowspan="2">윤영임</td><td rowspan="2">매주 화, 격주 목<br>09:00~18:00</td>
            </tr>
            <tr><td>포항사업실</td></tr>
            <tr><td>포항양극재</td><td>신사무동 4층 상담실</td><td rowspan="2">김진아</td><td>매주 월<br>09:00~18:00</td></tr>
            <tr><td>포항음극재</td><td>사무동 1층 보건실</td><td>격주 목<br>09:00~18:00</td></tr>
            <tr>
                <td rowspan="2" style="font-weight: bold; color: #fbcfe8;">광양</td>
                <td>광양사업실</td><td>태인동 사무소<br>3층 마음쉼터</td><td>박정숙</td><td>매주 수<br>09:00~18:00</td>
            </tr>
            <tr><td>광양양극재</td><td>창의동 2층<br>건강관리실 內 고충상담실</td><td>이혜주</td><td>매주 화<br>09:00~18:00</td></tr>
            <tr>
                <td style="font-weight: bold; color: #fbcfe8;">세종</td>
                <td>세종음극재</td><td>2공장 복지동<br>2층 혼창통</td><td>김유진</td><td>매주 화<br>10:00~19:00</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

# ==========================================
# [화면 구성] 2. 메인 서비스 화면
# ==========================================
else:
    # 상단 헤더 (홈 화면으로 가기 버튼 추가)
    col_title, col_home, col_logout = st.columns([3, 1, 1])
    with col_title:
        st.markdown(f"<div class='neon-title' style='text-align: left; font-size: 40px;'>{st.session_state['user_id']}님의 마음 상담소</div>", unsafe_allow_html=True)
    with col_home:
        st.write("") 
        st.write("") 
        if st.button("🏠 홈 화면으로", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = ""
            st.session_state['chat_session'] = []
            st.rerun()
    with col_logout:
        st.write("") 
        st.write("") 
        if st.button("🔒 로그아웃", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = ""
            st.session_state['chat_session'] = []
            st.rerun()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💬 AI 마음 상담", "📚 나의 기록", "📊 스트레스 분석", "🌙 수면 사운드", "🎮 스트레스 타파", "📅 D-day 관리"])

    # ------------------------------------------
    # [탭 1] AI 마음 상담
    # ------------------------------------------
    with tab1:
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1: st.markdown("### 💬 마음 상담 채팅")
        with col_t2:
            if st.button("🔄 새 상담 시작 (초기화)", use_container_width=True):
                st.session_state['chat_session'] = []
                st.rerun()

        if not st.session_state['chat_session']:
            st.info("아래 입력창에 고민을 적어주시면 상담이 시작됩니다. 추가 질문도 언제든 가능해요!")
        else:
            for msg in st.session_state['chat_session']:
                st.markdown(f"<div class='chat-user'><span>{msg['worry']}</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-ai'><span>{msg['answer']}</span></div>", unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            worry_input = st.text_area("고민이나 추가 질문을 자유롭게 적어주세요.", height=100)
            submitted = st.form_submit_button("상담사에게 전송", use_container_width=True)
            
            if submitted:
                if worry_input.strip() == "": st.warning("내용을 조금이라도 적어주세요.")
                else:
                    with st.spinner("AI 심리상담사가 답변을 준비하고 있습니다..."):
                        try:
                            context = ""
                            for m in st.session_state['chat_session']:
                                context += f"내담자: {m['worry']}\n상담사: {m['answer']}\n\n"
                            
                            prompt = f"""
                            당신은 직장인들의 마음을 치유해주는 따뜻하고 공감 능력이 뛰어난 전문 심리 상담사입니다.
                            [이전 대화 문맥]
                            {context}
                            
                            [내담자의 새로운 질문/고민]
                            "{worry_input}"
                            
                            위 문맥을 참고하여, 내담자의 새로운 질문에 깊이 공감해주고 마음이 편안해질 수 있는 따뜻한 위로와 조언을 3~4문단으로 작성해주세요. 말투는 '~해요', '~습니다' 등 다정하고 존중하는 어투를 사용하세요.
                            """
                            response = model.generate_content(prompt)
                            answer = response.text
                            
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            c.execute("INSERT INTO counseling_records (user_id, date, worry, answer) VALUES (?, ?, ?, ?)", 
                                      (st.session_state['user_id'], now, worry_input, answer))
                            conn.commit()
                            
                            st.session_state['chat_session'].append({'worry': worry_input, 'answer': answer})
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ AI 응답 중 오류가 발생했습니다. (상세: {e})")

    # ------------------------------------------
    # [탭 2] 나의 마음 기록
    # ------------------------------------------
    with tab2:
        col_r1, col_r2 = st.columns([4, 1])
        with col_r1: st.markdown("### 🕰️ 내가 걸어온 마음의 발자취")
        with col_r2:
            if st.button("🗑️ 전체 삭제", use_container_width=True):
                c.execute("DELETE FROM counseling_records WHERE user_id=?", (st.session_state['user_id'],))
                conn.commit()
                st.session_state['chat_session'] = [] 
                st.success("모든 기록이 삭제되었습니다.")
                time.sleep(1)
                st.rerun()
                
        c.execute("SELECT id, date, worry, answer FROM counseling_records WHERE user_id=? ORDER BY id DESC", (st.session_state['user_id'],))
        records = c.fetchall()
        
        if not records: st.info("아직 상담 기록이 없습니다. 첫 번째 고민을 남겨보세요!")
        else:
            for record in records:
                r_id, date, worry, answer = record
                col_card, col_del = st.columns([6, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="record-card">
                        <div class="record-date">🕒 {date}</div>
                        <div class="record-worry">Q. {worry}</div>
                        <div class="record-answer">A. {answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    st.write("") 
                    if st.button("❌ 삭제", key=f"del_rec_{r_id}", use_container_width=True):
                        c.execute("DELETE FROM counseling_records WHERE id=?", (r_id,))
                        conn.commit()
                        st.rerun()

    # ------------------------------------------
    # [탭 3] 스트레스 지수 분석
    # ------------------------------------------
    with tab3:
        st.markdown("### 📋 직무 스트레스 자가진단 (KOSHA 기반)")
        st.markdown("최근 1개월 동안 직장에서 느낀 감정이나 생각에 대해 가장 잘 맞는 것을 선택해 주세요.")
        
        questions = [
            "1. 업무량이 너무 많아 항상 시간에 쫓긴다.", "2. 내 업무의 책임 한계가 불명확하다.",
            "3. 업무를 수행하기 위해 높은 수준의 집중력이 요구된다.", "4. 상사나 동료와 의견 충돌이 잦다.",
            "5. 내 직무에 대한 권한이나 자율성이 부족하다.", "6. 업무 결과에 대해 정당한 평가를 받지 못한다.",
            "7. 직장 내에서 소외감을 느끼거나 외롭다.", "8. 고용 불안정(구조조정 등)을 느낀다.",
            "9. 업무 환경(소음, 조명, 환기 등)이 불편하다.", "10. 퇴근 후에도 업무에 대한 걱정을 계속 한다.",
            "11. 내 능력에 비해 너무 어려운 업무가 주어진다.", "12. 타 부서와의 협조가 원활하게 이루어지지 않는다.",
            "13. 회사의 장래가 불투명하다고 느낀다.", "14. 업무로 인해 개인 생활(가족, 여가)에 지장을 받는다.",
            "15. 직장에서 감정 노동(감정 숨기기 등)을 강요받는다.", "16. 상사의 지시가 일관성이 없어 혼란스럽다.",
            "17. 직무 수행에 필요한 지원이나 자원이 부족하다.", "18. 승진이나 보상 체계가 불공정하다고 느낀다.",
            "19. 직장 내 괴롭힘이나 부당한 대우를 경험한 적이 있다.", "20. 현재의 직무가 내 적성이나 경력 개발에 도움이 되지 않는다."
        ]
        
        options = ["전혀 그렇지 않다 (1점)", "그렇지 않다 (2점)", "보통이다 (3점)", "그렇다 (4점)", "매우 그렇다 (5점)"]
        
        with st.form("stress_test_form"):
            scores = []
            for q in questions:
                st.markdown(f"**{q}**")
                choice = st.radio("선택", options, horizontal=True, key=q, label_visibility="collapsed")
                scores.append(options.index(choice) + 1)
                st.markdown("<hr style='margin: 10px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            
            submitted_test = st.form_submit_button("📊 진단 결과 확인하기", use_container_width=True)
            
            if submitted_test:
                total_score = sum(scores)
                st.markdown("### 💡 자가진단 결과")
                
                if total_score <= 40:
                    result_text = "🟢 **양호한 상태입니다.** 현재 스트레스를 잘 관리하고 계십니다."
                    color = "#4ade80"
                elif total_score <= 60:
                    result_text = "🟡 **보통 수준입니다.** 가벼운 스트레스가 있으니 충분한 휴식이 필요합니다."
                    color = "#facc15"
                elif total_score <= 80:
                    result_text = "🟠 **심한 스트레스 상태입니다.** 업무 조율과 적극적인 스트레스 관리가 필요합니다."
                    color = "#fb923c"
                else:
                    result_text = "🔴 **위험 수준입니다.** 번아웃이 우려되니 사내 심리상담센터의 도움을 꼭 받아보시길 권장합니다."
                    color = "#f87171"
                    
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border: 2px solid {color}; border-radius: 15px; padding: 30px; text-align: center;">
                    <h2 style="color: {color}; margin-bottom: 10px;">총점: {total_score}점 / 100점</h2>
                    <p style="font-size: 20px; color: #ffffff;">{result_text}</p>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 4] 수면 & 힐링 사운드 (링크 교체 및 추가)
    # ------------------------------------------
    with tab4:
        st.markdown("### 🌙 깊은 수면과 휴식을 위한 사운드")
        sound_choice = st.radio(
            "듣고 싶은 테마를 선택하세요:", 
            ["🔥 장작 타는 소리", "🌧️ 차분해지는 빗소리", "🎵 432Hz 심신 안정 주파수", "🌊 잔잔한 파도 소리", "🌲 숲 속 새소리", "🎹 잔잔한 피아노", "☕ 백색소음 (카페)"], 
            horizontal=True
        )
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        if "장작" in sound_choice: st.video("https://www.youtube.com/watch?v=L_LUpnjgPso") 
        elif "빗소리" in sound_choice: st.video("https://www.youtube.com/watch?v=mPZkdNFkNps")
        elif "주파수" in sound_choice: st.video("https://www.youtube.com/watch?v=77ZozI0rw7w") 
        elif "파도" in sound_choice: st.video("https://www.youtube.com/watch?v=bn9F19Hi1Lk")
        elif "새소리" in sound_choice: st.video("https://www.youtube.com/watch?v=eKFTSSKCzWA")
        elif "피아노" in sound_choice: st.video("https://www.youtube.com/watch?v=81SjIEKOUjE")
        elif "카페" in sound_choice: st.video("https://www.youtube.com/watch?v=gaGrHUekGrc")

    # ------------------------------------------
    # [탭 5] 스트레스 타파 미니게임
    # ------------------------------------------
    with tab5:
        st.markdown("### 🎮 스트레스 타파 미니게임")
        
        # 얼음 속에 넣을 커스텀 텍스트 입력창
        ice_text = st.text_input("🧊 얼음 속에 가두고 싶은 스트레스를 적어주세요 (예: 월요병, 실적 압박)", value="스트레스")
        
        game_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            @font-face {{
                font-family: 'SeoulNamsan';
                src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/SeoulNamsanM.woff') format('woff');
                font-weight: normal; font-style: normal;
            }}
            body {{ font-family: 'SeoulNamsan', sans-serif; color: white; margin: 0; padding: 10px; background: transparent; user-select: none; }}
            h4 {{ color: #c084fc; margin-bottom: 15px; font-size: 20px; font-weight: bold; }}
            
            /* 얼음 깨기 스타일 */
            .ice-container {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 50px; flex-wrap: wrap; }}
            .ice-block {{
                width: 120px; height: 120px;
                background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(165,243,252,0.6) 100%);
                border: 2px solid rgba(255,255,255,0.8); border-radius: 15px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.3), inset 0 0 20px rgba(255,255,255,0.5);
                display: flex; justify-content: center; align-items: center; text-align: center;
                font-size: 18px; font-weight: 900; color: #083344;
                cursor: pointer; transition: all 0.1s; backdrop-filter: blur(5px);
                background-size: cover; background-position: center;
            }}
            .ice-block:active {{ transform: scale(0.95); }}
            .shattered {{ background: transparent !important; border: none !important; box-shadow: none !important; color: transparent !important; pointer-events: none; }}
            .shattered::after {{ content: '💥'; font-size: 60px; color: white; display: block; animation: fadeOut 1s forwards; }}
            
            /* 개미 잡기 스타일 */
            .ant-game-area {{ 
                position: relative; width: 100%; height: 450px; 
                background: radial-gradient(circle, #5c4033 0%, #27160a 100%); 
                border-radius: 20px; overflow: hidden; 
                border: 2px solid #8b5a2b; box-shadow: inset 0 0 50px rgba(0,0,0,0.8);
                cursor: crosshair;
            }}
            #bread {{
                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                font-size: 130px; /* 식빵 크기 1.5배 확대 */
                transition: transform 0.2s; z-index: 10;
            }}
            .ant {{ 
                position: absolute; font-size: 35px; cursor: pointer; 
                transition: transform 0.3s ease-out; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.8)); z-index: 20;
            }}
            .screen-crack {{
                position: absolute; font-size: 80px; z-index: 30;
                animation: fadeOut 0.8s forwards; pointer-events: none; transform: translate(-50%, -50%);
            }}
            @keyframes fadeOut {{ 0% {{ opacity: 1; transform: scale(1) translate(-50%, -50%); }} 100% {{ opacity: 0; transform: scale(1.5) translate(-50%, -50%); }} }}
            
            .btn {{ font-family: 'SeoulNamsan', sans-serif; background: linear-gradient(45deg, #c084fc, #fbcfe8); color: #1e1b4b; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 900; cursor: pointer; margin-bottom: 15px; font-size: 18px; box-shadow: 0 4px 15px rgba(192, 132, 252, 0.4); transition: transform 0.1s; }}
            .btn:active {{ transform: scale(0.95); }}
        </style>
        </head>
        <body>

        <h4>🧊 분노의 얼음 깨기 (3번 클릭해서 박살내세요!)</h4>
        <div class="ice-container">
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice_text}</span></div>
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice_text}</span></div>
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice_text}</span></div>
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice_text}</span></div>
        </div>

        <hr style="border-color: rgba(255,255,255,0.1); margin: 30px 0;">

        <h4>🍞 내 식빵 지키기 (개미를 터치해 식빵을 지키세요!)</h4>
        <button class="btn" onclick="spawnAnts(5)">+ 개미 5마리 소환</button>
        <div class="ant-game-area" id="antContainer">
            <div id="bread">🍞</div>
        </div>

        <script>
            const glassSound = 'https://assets.mixkit.co/active_storage/sfx/2685/2685-preview.mp3'; 
            const squishSound = 'https://assets.mixkit.co/active_storage/sfx/2783/2783-preview.mp3'; 
            const eatSound = 'https://assets.mixkit.co/active_storage/sfx/2902/2902-preview.mp3';

            function playSound(url) {{ let audio = new Audio(url); audio.volume = 0.6; audio.play().catch(e => console.log("Audio blocked")); }}

            // 얼음 깨기 3단 콤보 로직 (SVG로 리얼한 금가기 표현)
            const crack1 = `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M30,0 L45,30 L35,50 L60,80 L50,100" stroke="rgba(255,255,255,0.9)" stroke-width="3" fill="none"/></svg>')`;
            const crack2 = `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M30,0 L45,30 L35,50 L60,80 L50,100 M100,30 L70,45 L80,70 L40,90" stroke="rgba(255,255,255,1)" stroke-width="4" fill="none"/></svg>')`;

            function breakIce(el) {{
                if(el.classList.contains('shattered')) return;
                
                let hits = parseInt(el.getAttribute('data-hits'));
                hits++;
                el.setAttribute('data-hits', hits);
                
                if(hits === 1) {{
                    playSound(glassSound);
                    el.style.backgroundImage = crack1 + ", linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(165,243,252,0.6) 100%)";
                }} else if(hits === 2) {{
                    playSound(glassSound);
                    el.style.backgroundImage = crack2 + ", linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(165,243,252,0.6) 100%)";
                }} else {{
                    playSound(glassSound);
                    el.classList.add('shattered');
                    setTimeout(() => {{ el.style.display = 'none'; }}, 1000);
                }}
            }}

            // 개미 잡기 로직
            const antContainer = document.getElementById('antContainer');
            const bread = document.getElementById('bread');
            let breadScale = 1.0;

            function spawnAnts(count) {{
                for(let i=0; i<count; i++) {{
                    let ant = document.createElement('div'); ant.className = 'ant'; ant.innerHTML = '🐜';
                    
                    let edge = Math.floor(Math.random() * 4);
                    let x, y;
                    if(edge===0) {{ x = Math.random() * antContainer.clientWidth; y = -30; }}
                    else if(edge===1) {{ x = antContainer.clientWidth + 30; y = Math.random() * antContainer.clientHeight; }}
                    else if(edge===2) {{ x = Math.random() * antContainer.clientWidth; y = antContainer.clientHeight + 30; }}
                    else {{ x = -30; y = Math.random() * antContainer.clientHeight; }}
                    
                    ant.style.left = x + 'px'; ant.style.top = y + 'px'; 
                    antContainer.appendChild(ant); 
                    moveAntToBread(ant);

                    ant.addEventListener('pointerdown', function() {{
                        playSound(squishSound);
                        let crack = document.createElement('div'); crack.className = 'screen-crack'; crack.innerHTML = '🕸️'; 
                        crack.style.left = (parseFloat(this.style.left) + 15) + 'px'; 
                        crack.style.top = (parseFloat(this.style.top) + 15) + 'px'; 
                        antContainer.appendChild(crack);
                        this.remove(); 
                        setTimeout(() => {{ crack.remove(); }}, 800);
                    }});
                }}
            }}

            function moveAntToBread(ant) {{
                let moveInterval = setInterval(() => {{
                    if(!document.body.contains(ant)) {{ clearInterval(moveInterval); return; }}
                    
                    let currentX = parseFloat(ant.style.left); let currentY = parseFloat(ant.style.top);
                    let targetX = antContainer.clientWidth / 2 - 15; 
                    let targetY = antContainer.clientHeight / 2 - 15;
                    
                    let dx = targetX - currentX; let dy = targetY - currentY;
                    let distance = Math.sqrt(dx*dx + dy*dy);
                    
                    if(distance < 60) {{ // 식빵이 커졌으므로 충돌 판정 거리도 늘림
                        playSound(eatSound);
                        breadScale -= 0.05;
                        if(breadScale < 0.2) breadScale = 0.2;
                        bread.style.transform = `translate(-50%, -50%) scale(${{breadScale}})`;
                        ant.remove();
                        clearInterval(moveInterval);
                        return;
                    }}
                    
                    let speed = 3;
                    let newX = currentX + (dx / distance) * speed;
                    let newY = currentY + (dy / distance) * speed;
                    
                    let angle = Math.atan2(dy, dx) * 180 / Math.PI;
                    ant.style.transform = `rotate(${{angle + 90}}deg)`; 
                    ant.style.left = newX + 'px'; ant.style.top = newY + 'px';
                }}, 50); 
            }}

            spawnAnts(3); 
        </script>
        </body>
        </html>
        """
        components.html(game_html, height=850, scrolling=False)

    # ------------------------------------------
    # [탭 6] D-day 일정 관리
    # ------------------------------------------
    with tab6:
        st.markdown("### 📅 나만의 소중한 일정 관리")
        st.markdown("기념일, 자격증 시험, 휴가 등 기다려지는 날들을 기록해 보세요. 마음의 여유를 찾는 데 도움이 됩니다.")
        
        st.write("")
        col_title, col_date = st.columns(2)
        with col_title: dday_title = st.text_input("일정 이름 (예: 여름휴가, 승진 시험)", key="dday_title")
        with col_date: dday_date = st.date_input("날짜 선택", key="dday_date")
            
        st.write("")
        if st.button("✨ D-day 추가하기", use_container_width=True):
            if dday_title.strip() == "": st.warning("일정 이름을 입력해주세요.")
            else:
                c.execute("INSERT INTO dday_records (user_id, title, target_date) VALUES (?, ?, ?)", (st.session_state['user_id'], dday_title, str(dday_date)))
                conn.commit()
                st.success("새로운 일정이 추가되었습니다!")
                st.rerun()
                
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)
        
        c.execute("SELECT id, title, target_date FROM dday_records WHERE user_id=? ORDER BY target_date ASC", (st.session_state['user_id'],))
        ddays = c.fetchall()
        
        if not ddays: st.info("등록된 일정이 없습니다. 새로운 D-day를 추가해 보세요!")
        else:
            today = datetime.date.today()
            for dday in ddays:
                d_id, title, t_date_str = dday
                t_date = datetime.datetime.strptime(t_date_str, "%Y-%m-%d").date()
                delta = (t_date - today).days
                
                if delta > 0: d_text, color = f"D - {delta}", "#fbcfe8"
                elif delta == 0: d_text, color = "D - Day 🎉", "#c084fc"
                else: d_text, color = f"D + {-delta}", "#94a3b8"
                
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); border-left: 5px solid {color}; border-radius: 12px; padding: 20px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                        <div><div style="color: #cbd5e1; font-size: 15px; margin-bottom: 5px;">{t_date_str}</div><div style="color: #ffffff; font-size: 22px; font-weight: bold;">{title}</div></div>
                        <div style="color: {color}; font-size: 32px; font-weight: 900; text-shadow: 0 0 10px rgba(255,255,255,0.2);">{d_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    st.write("")
                    st.write("")
                    if st.button("❌ 삭제", key=f"del_dday_{d_id}", use_container_width=True):
                        c.execute("DELETE FROM dday_records WHERE id=?", (d_id,))
                        conn.commit()
                        st.rerun()

# ==========================================
# [푸터] 면책 조항 (로그인 후 화면 하단)
# ==========================================
st.markdown("""
<hr style="border-color: rgba(255,255,255,0.1); margin-top: 50px;">
<div style="text-align: center; color: #94a3b8; font-size: 15px; line-height: 1.8;">
    ⚠️ <b>본 '마음 상담소'의 답변은 AI에 의해 생성된 위로 메시지이며, 전문적인 의학적 진단이나 심리 치료를 대체할 수 없습니다.</b><br>
    심각한 우울감이나 스트레스가 지속될 경우, <b>사내 심리상담센터(심즈업 심리상담 070-4192-7762)</b> 또는 전문 의료기관의 도움을 받으시길 권장합니다.
</div>
<div style="text-align: center; color: #64748b; font-size: 13px; margin-top: 20px;">
    © POSCO FUTURE M Smart Mind Care Center. All rights reserved.
</div>
""", unsafe_allow_html=True)
