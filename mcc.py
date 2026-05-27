import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import datetime
import time
import random
import requests
import json

# ==========================================
# [초기 설정] 페이지 세팅
# ==========================================
st.set_page_config(page_title="스마트 마음 상담 센터", page_icon="🌙", layout="wide")

# ==========================================
# [Groq API 키 설정] - 구글 대신 에러 없는 Groq 사용
# ==========================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ 스트림릿 설정(Settings) -> Secrets에 'GROQ_API_KEY'를 먼저 입력해주세요!")
    st.stop()

# ==========================================
# [데이터베이스 설정] SQLite3
# ==========================================
conn = sqlite3.connect('mind_care_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS counseling_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, worry TEXT, answer TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS dday_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, target_date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS game_scores (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, score INTEGER, date TEXT)''')
conn.commit()

# ==========================================
# [감성 아이스브레이킹 멘트 리스트]
# ==========================================
GREETINGS = [
    "편하게 인사부터 해볼까요 우리? 오늘 하루 어땠나요?",
    "이곳에 오신 걸 환영해요. 지금 마음속에 떠오르는 감정은 어떤 색깔인가요?",
    "오늘 하루도 정말 수고 많으셨어요. 어떤 이야기든 편하게 들려주세요.",
    "많이 지치고 힘든 하루였나요? 제가 당신의 이야기를 들어드릴게요.",
    "따뜻한 차 한 잔 마시듯, 편안하게 마주 앉아 이야기 나눠볼까요?"
]

# ==========================================
# [CSS] 모바일 반응형 및 UI/UX 디자인 (표 디자인 수정 완료)
# ==========================================
st.markdown("""
<style>
    @font-face {
        font-family: 'SeoulNamsan';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/SeoulNamsanM.woff') format('woff');
        font-weight: normal; font-style: normal;
    }

    .stApp, .stApp p, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp table, .stApp th, .stApp td {
        font-family: 'SeoulNamsan', sans-serif !important;
    }

    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    
    .neon-title {
        font-size: 55px; font-weight: 900; color: #ffffff; text-align: center;
        margin-top: 20px; margin-bottom: 10px; letter-spacing: 2px; line-height: 1.2;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #c084fc, 0 0 40px #c084fc, 0 0 80px #c084fc, 0 0 90px #c084fc;
    }
    .sub-title { color: #e2e8f0; font-size: 20px; margin-bottom: 40px; font-weight: 500; text-align: center; word-break: keep-all; }
    
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        background-color: #1e293b !important; border: 2px solid #c084fc !important; border-radius: 10px !important;
    }
    input, textarea { color: #ffffff !important; font-size: 16px !important; font-weight: bold !important; }
    label { color: #fbcfe8 !important; font-size: 16px !important; font-weight: bold !important; }

    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(45deg, #4f46e5, #9333ea) !important; 
        color: #ffffff !important; 
        font-weight: 900 !important; font-size: 16px !important; padding: 10px 20px !important;
        border: none !important; border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.5) !important; transition: all 0.3s ease !important;
    }
    
    .post-it-container { display: flex; justify-content: center; gap: 20px; margin-bottom: 40px; flex-wrap: wrap; }
    .post-it {
        width: 180px; padding: 20px 15px; color: #1e293b; font-size: 16px; font-weight: 900; text-align: center; 
        border-radius: 2px 15px 15px 2px; box-shadow: 5px 5px 20px rgba(0,0,0,0.4); position: relative;
    }
    .post-it::before {
        content: ""; position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
        width: 40px; height: 15px; background: rgba(255,255,255,0.5); box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .p1 { transform: rotate(-4deg); background: #fef08a; }
    .p2 { transform: rotate(3deg); background: #bbf7d0; }
    .p3 { transform: rotate(-3deg); background: #fbcfe8; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 5px; justify-content: center; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.05); border-radius: 8px 8px 0 0; padding: 8px 12px; color: #cbd5e1; font-size: 15px; white-space: nowrap; }
    .stTabs [aria-selected="true"] { background-color: rgba(192, 132, 252, 0.2); color: #fbcfe8 !important; border-bottom: 3px solid #c084fc; font-weight: bold; }

    .record-card { background: rgba(255,255,255,0.05); border-left: 5px solid #c084fc; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .record-date { color: #fbcfe8; font-size: 13px; font-weight: bold; margin-bottom: 8px; }
    .record-worry { color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 12px; line-height: 1.5; }
    .record-answer { color: #e2e8f0; font-size: 15px; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 10px; line-height: 1.6; }
    
    .chat-user { text-align: right; margin-bottom: 15px; }
    .chat-user span { background-color: #334155; padding: 10px 15px; border-radius: 20px 20px 0 20px; display: inline-block; font-size: 15px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3); max-width: 85%; word-break: break-word; }
    .chat-ai { text-align: left; margin-bottom: 25px; }
    .chat-ai span { background-color: rgba(192, 132, 252, 0.15); border: 1px solid #c084fc; padding: 12px 15px; border-radius: 20px 20px 20px 0; display: inline-block; font-size: 15px; line-height: 1.6; box-shadow: 0 4px 10px rgba(0,0,0,0.3); max-width: 90%; word-break: break-word; }

    /* PC 화면에서 표가 예쁘게 가운데로 모이도록 수정된 부분 */
    .table-container { display: flex; justify-content: center; overflow-x: auto; padding: 10px; }
    .counseling-table {
        width: 100%; max-width: 850px; min-width: 500px; margin: 20px auto; border-collapse: collapse;
        background-color: rgba(255, 255, 255, 0.03); color: #e2e8f0; font-size: 15px;
        text-align: center; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .counseling-table th { background: linear-gradient(45deg, #3b82f6, #8b5cf6); color: #ffffff; padding: 12px; font-weight: 900; border: 1px solid rgba(255, 255, 255, 0.1); font-size: 14px; white-space: nowrap; }
    .counseling-table td { padding: 12px; border: 1px solid rgba(255, 255, 255, 0.1); vertical-align: middle; line-height: 1.4; }
    
    .ranking-card { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: bold; }
    .rank-1 { border-left: 5px solid #fbbf24; color: #fbbf24; }
    .rank-2 { border-left: 5px solid #94a3b8; color: #94a3b8; }
    .rank-3 { border-left: 5px solid #b45309; color: #b45309; }
    .rank-other { border-left: 5px solid #c084fc; color: #ffffff; }

    @media (max-width: 768px) {
        .neon-title { font-size: 38px !important; margin-top: 10px; }
        .sub-title { font-size: 16px !important; margin-bottom: 20px; }
        .post-it { width: 45%; padding: 15px 10px; font-size: 14px; }
        .stTabs [data-baseweb="tab"] { font-size: 13px; padding: 6px 10px; }
        .chat-user span, .chat-ai span { font-size: 14px; }
        .record-worry { font-size: 15px; }
        .record-answer { font-size: 14px; }
        div[data-testid="stButton"] > button { font-size: 14px !important; padding: 8px 15px !important; }
        .ranking-card { font-size: 14px; }
    }
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
if 'greeting_msg' not in st.session_state: st.session_state['greeting_msg'] = random.choice(GREETINGS)

# ==========================================
# [화면 구성] 1. 로그인 / 회원가입 화면
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("<div class='neon-title'>스마트<br>마음 상담소</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>당신의 지친 하루를 따뜻하게 안아드릴게요.<br>편하게 기대어 보세요.</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="post-it-container">
        <div class="post-it p1">"괜찮아,<br>다 잘 될 거야 💛"</div>
        <div class="post-it p2">"오늘 하루도<br>정말 수고했어 🌿"</div>
        <div class="post-it p3">"넌 충분히<br>빛나고 있어 ✨"</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 4, 1])
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
                    st.session_state['greeting_msg'] = random.choice(GREETINGS) 
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                    
        with auth_tab2:
            reg_id = st.text_input("사용할 아이디", key="reg_id")
            if st.button("아이디 중복 확인", use_container_width=True):
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
    <div class="table-container">
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
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# [화면 구성] 2. 메인 서비스 화면
# ==========================================
else:
    st.markdown(f"<div class='neon-title' style='font-size: 35px;'>{st.session_state['user_id']}님의<br>마음 상담소</div>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🏠 홈 화면으로", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = ""
            st.session_state['chat_session'] = []
            st.rerun()
    with col_btn2:
        if st.button("🔒 로그아웃", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = ""
            st.session_state['chat_session'] = []
            st.rerun()
            
    st.write("")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💬 AI 상담", "📚 기록", "📊 스트레스", "🌙 사운드", "🎮 게임", "📅 D-day"])

    # ------------------------------------------
    # [탭 1] AI 마음 상담 (Groq API 적용)
    # ------------------------------------------
    with tab1:
        st.markdown("### 💬 마음 상담 채팅")
        if st.button("🔄 새 상담 시작 (초기화)", use_container_width=True):
            st.session_state['chat_session'] = []
            st.session_state['greeting_msg'] = random.choice(GREETINGS) 
            st.rerun()
        st.write("")

        if not st.session_state['chat_session']:
            st.markdown(f"""
            <div class='chat-ai'>
                <span>🌿 <b>상담사:</b><br><br>{st.session_state['greeting_msg']}</span>
            </div>
            """, unsafe_allow_html=True)
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
                            # 대화 기록 구성
                            messages = [
                                {"role": "system", "content": "당신은 직장인들의 마음을 치유해주는 따뜻하고 공감 능력이 뛰어난 전문 심리 상담사입니다. 내담자의 질문에 깊이 공감해주고 마음이 편안해질 수 있는 따뜻한 위로와 조언을 3~4문단으로 작성해주세요. 말투는 '~해요', '~습니다' 등 다정하고 존중하는 어투를 사용하세요. 한국어로만 대답하세요."}
                            ]
                            for m in st.session_state['chat_session']:
                                messages.append({"role": "user", "content": m['worry']})
                                messages.append({"role": "assistant", "content": m['answer']})
                            
                            messages.append({"role": "user", "content": worry_input})
                            
                            # Groq API 호출 (Llama 3 모델)
                            url = "https://api.groq.com/openai/v1/chat/completions"
                            headers = {
                                "Authorization": f"Bearer {GROQ_API_KEY}",
                                "Content-Type": "application/json"
                            }
                            data = {
                                "model": "llama3-70b-8192",
                                "messages": messages,
                                "temperature": 0.7
                            }
                            
                            response = requests.post(url, headers=headers, json=data)
                            
                            if response.status_code == 200:
                                answer = response.json()['choices'][0]['message']['content']
                                
                                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                c.execute("INSERT INTO counseling_records (user_id, date, worry, answer) VALUES (?, ?, ?, ?)", 
                                          (st.session_state['user_id'], now, worry_input, answer))
                                conn.commit()
                                
                                st.session_state['chat_session'].append({'worry': worry_input, 'answer': answer})
                                st.rerun()
                            else:
                                st.error(f"⚠️ AI 서버 응답 오류 (코드: {response.status_code})")
                                st.error(response.text)
                                
                        except Exception as e:
                            st.error("⚠️ 통신 중 오류가 발생했습니다.")
                            st.error(f"상세 오류 메시지: {e}")

    # ------------------------------------------
    # [탭 2] 나의 마음 기록
    # ------------------------------------------
    with tab2:
        st.markdown("### 🕰️ 내가 걸어온 마음의 발자취")
        if st.button("🗑️ 전체 삭제", use_container_width=True):
            c.execute("DELETE FROM counseling_records WHERE user_id=?", (st.session_state['user_id'],))
            conn.commit()
            st.session_state['chat_session'] = [] 
            st.success("모든 기록이 삭제되었습니다.")
            time.sleep(1)
            st.rerun()
        st.write("")
                
        c.execute("SELECT id, date, worry, answer FROM counseling_records WHERE user_id=? ORDER BY id DESC", (st.session_state['user_id'],))
        records = c.fetchall()
        
        if not records: st.info("아직 상담 기록이 없습니다. 첫 번째 고민을 남겨보세요!")
        else:
            for record in records:
                r_id, date, worry, answer = record
                st.markdown(f"""
                <div class="record-card">
                    <div class="record-date">🕒 {date}</div>
                    <div class="record-worry">Q. {worry}</div>
                    <div class="record-answer">A. {answer}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("❌ 이 기록 삭제", key=f"del_rec_{r_id}", use_container_width=True):
                    c.execute("DELETE FROM counseling_records WHERE id=?", (r_id,))
                    conn.commit()
                    st.rerun()
                st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 3] 스트레스 지수 분석
    # ------------------------------------------
    with tab3:
        st.markdown("### 📋 직무 스트레스 자가진단")
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
                <div style="background: rgba(255,255,255,0.05); border: 2px solid {color}; border-radius: 15px; padding: 20px; text-align: center;">
                    <h3 style="color: {color}; margin-bottom: 10px;">총점: {total_score}점 / 100점</h3>
                    <p style="font-size: 16px; color: #ffffff;">{result_text}</p>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 4] 수면 & 힐링 사운드
    # ------------------------------------------
    with tab4:
        st.markdown("### 🌙 깊은 수면과 휴식을 위한 사운드")
        sound_choice = st.selectbox(
            "듣고 싶은 테마를 선택하세요:", 
            ["🔥 장작 타는 소리", "🌧️ 차분해지는 빗소리", "🎵 432Hz 심신 안정 주파수", "🌊 잔잔한 파도 소리", "🌲 숲 속 새소리", "🎹 잔잔한 피아노", "☕ 백색소음 (카페)"]
        )
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        if "장작" in sound_choice: st.video("https://www.youtube.com/watch?v=3_cE2_Mh2L0") 
        elif "빗소리" in sound_choice: st.video("https://www.youtube.com/watch?v=mPZkdNFkNps")
        elif "주파수" in sound_choice: st.video("https://www.youtube.com/watch?v=1ZYbU82GVz4") 
        elif "파도" in sound_choice: st.video("https://www.youtube.com/watch?v=bn9F19Hi1Lk")
        elif "새소리" in sound_choice: st.video("https://www.youtube.com/watch?v=eKFTSSKCzWA")
        elif "피아노" in sound_choice: st.video("https://www.youtube.com/watch?v=WJ3-F02-F_Y") 
        elif "카페" in sound_choice: st.video("https://www.youtube.com/watch?v=gaGrHUekGrc")

    # ------------------------------------------
    # [탭 5] 스트레스 타파 미니게임
    # ------------------------------------------
    with tab5:
        st.markdown("### 🎮 스트레스 타파 미니게임")
        
        st.markdown("#### 🧊 분노의 얼음 깨기")
        st.caption("얼음 속에 가두고 싶은 스트레스를 적어주세요.")
        
        col_i1, col_i2 = st.columns(2)
        with col_i1: 
            ice1 = st.text_input("첫 번째", value="월요병")
            ice3 = st.text_input("세 번째", value="인간관계")
        with col_i2: 
            ice2 = st.text_input("두 번째", value="실적 압박")
            ice4 = st.text_input("네 번째", value="야근")
        
        auto_score = st.text_input("auto_score_input_hidden_123", key="auto_score_input")
        auto_submit = st.button("auto_score_submit_hidden_123", key="auto_submit_btn")
        
        if auto_submit and auto_score.isdigit():
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO game_scores (user_id, score, date) VALUES (?, ?, ?)", (st.session_state['user_id'], int(auto_score), now))
            conn.commit()
            st.success(f"🎉 {auto_score}점이 랭킹에 자동 등록되었습니다!")
            time.sleep(1.5)
            st.rerun()

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
            body {{ font-family: 'SeoulNamsan', sans-serif; color: white; margin: 0; padding: 5px; background: transparent; user-select: none; touch-action: manipulation; }}
            h4 {{ color: #c084fc; margin-bottom: 15px; font-size: 18px; font-weight: bold; text-align: center; }}
            
            .ice-container {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }}
            .ice-block {{
                width: 100px; height: 100px;
                background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(165,243,252,0.6) 100%);
                border: 2px solid rgba(255,255,255,0.8); border-radius: 15px;
                box-shadow: 0 5px 10px rgba(0,0,0,0.3), inset 0 0 10px rgba(255,255,255,0.5);
                display: flex; justify-content: center; align-items: center; text-align: center;
                font-size: 14px; font-weight: 900; color: #083344;
                cursor: pointer; transition: all 0.1s; backdrop-filter: blur(5px);
                background-size: cover; background-position: center; word-break: keep-all; padding: 5px;
            }}
            .ice-block:active {{ transform: scale(0.95); }}
            .shattered {{ background: transparent !important; border: none !important; box-shadow: none !important; color: transparent !important; pointer-events: none; }}
            .shattered::after {{ content: '💥'; font-size: 40px; color: white; display: block; animation: fadeOut 1s forwards; }}
            
            @keyframes shake {{
                0% {{ transform: translate(1px, 1px) rotate(0deg); }}
                20% {{ transform: translate(-2px, 0px) rotate(2deg); }}
                40% {{ transform: translate(2px, -2px) rotate(2deg); }}
                60% {{ transform: translate(-2px, 2px) rotate(0deg); }}
                80% {{ transform: translate(-1px, -1px) rotate(2deg); }}
                100% {{ transform: translate(1px, -2px) rotate(-2deg); }}
            }}
            .shake {{ animation: shake 0.25s; animation-iteration-count: 1; }}
            
            .ant-game-area {{ 
                position: relative; width: 100%; height: 400px; 
                background: radial-gradient(circle, #5c4033 0%, #27160a 100%); 
                border-radius: 15px; overflow: hidden; 
                border: 2px solid #8b5a2b; box-shadow: inset 0 0 30px rgba(0,0,0,0.8);
            }}
            #bread {{
                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                font-size: 80px; transition: transform 0.2s; z-index: 10;
            }}
            .ant {{ 
                position: absolute; font-size: 30px; cursor: pointer; 
                transition: transform 0.1s linear; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.8)); z-index: 20;
            }}
            .screen-crack {{
                position: absolute; font-size: 50px; z-index: 30;
                animation: fadeOut 0.8s forwards; pointer-events: none; transform: translate(-50%, -50%);
            }}
            @keyframes fadeOut {{ 0% {{ opacity: 1; transform: scale(1) translate(-50%, -50%); }} 100% {{ opacity: 0; transform: scale(1.5) translate(-50%, -50%); }} }}
            
            .btn {{ font-family: 'SeoulNamsan', sans-serif; background: linear-gradient(45deg, #c084fc, #fbcfe8); color: #1e1b4b; border: none; padding: 10px 20px; border-radius: 10px; font-weight: 900; cursor: pointer; margin-bottom: 15px; font-size: 16px; box-shadow: 0 4px 10px rgba(192, 132, 252, 0.4); transition: transform 0.1s; display: block; margin: 0 auto 20px auto; width: 80%; }}
            .btn:active {{ transform: scale(0.95); }}
            
            #hud {{ display: flex; justify-content: space-between; padding: 10px 15px; font-size: 16px; font-weight: bold; color: #fbcfe8; background: rgba(0,0,0,0.5); border-radius: 15px 15px 0 0; }}
            #gameOverScreen {{ display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 100; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center; padding: 20px; box-sizing: border-box; }}
            #gameOverScreen h1 {{ color: #f87171; font-size: 35px; margin-bottom: 10px; }}
            #gameOverScreen p {{ font-size: 20px; color: #fbcfe8; margin-bottom: 20px; }}
            #autoSubmitMsg {{ font-size: 14px; color: #4ade80; margin-bottom: 20px; font-weight: bold; word-break: keep-all; }}
        </style>
        </head>
        <body>

        <div class="ice-container">
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice1}</span></div>
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice2}</span></div>
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice3}</span></div>
            <div class="ice-block" onclick="breakIce(this)" data-hits="0"><span>{ice4}</span></div>
        </div>

        <hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">

        <h4>🍞 내 식빵 지키기 (터치!)</h4>
        <button class="btn" id="startBtn" onclick="startGame()">🚀 게임 시작</button>
        
        <div class="ant-game-area" id="antContainer">
            <div id="hud">
                <span id="levelDisplay">Lv: 1</span>
                <span id="scoreDisplay">Score: 0</span>
            </div>
            <div id="bread">🍞</div>
            
            <div id="gameOverScreen">
                <h1>GAME OVER</h1>
                <p id="finalScoreText">최종 점수: 0</p>
                <div id="autoSubmitMsg"></div>
                <button class="btn" onclick="location.reload()" style="margin-top: 10px;">다시 하기</button>
            </div>
        </div>

        <script>
            let hideInterval = setInterval(() => {{
                try {{
                    const parentDoc = window.parent.document;
                    let found = false;
                    parentDoc.querySelectorAll('label').forEach(l => {{
                        if(l.innerText.includes('auto_score_input_hidden_123')) {{
                            l.closest('div[data-testid="stTextInput"]').style.display = 'none';
                            found = true;
                        }}
                    }});
                    parentDoc.querySelectorAll('button').forEach(b => {{
                        if(b.innerText.includes('auto_score_submit_hidden_123')) {{
                            b.style.display = 'none';
                            found = true;
                        }}
                    }});
                    if(found) clearInterval(hideInterval);
                }} catch(e) {{ clearInterval(hideInterval); }}
            }}, 100);

            const crackSound = 'https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3'; 
            const smashSound = 'https://assets.mixkit.co/active_storage/sfx/2684/2684-preview.mp3'; 
            const squishSound = 'https://assets.mixkit.co/active_storage/sfx/2772/2772-preview.mp3'; 
            const eatSound = 'https://assets.mixkit.co/active_storage/sfx/2902/2902-preview.mp3';

            function playSound(url) {{ let audio = new Audio(url); audio.volume = 1.0; audio.play().catch(e => console.log("Audio blocked")); }}

            const crack1 = `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M30,0 L45,30 L35,50 L60,80 L50,100" stroke="rgba(255,255,255,0.9)" stroke-width="3" fill="none"/></svg>')`;
            const crack2 = `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M30,0 L45,30 L35,50 L60,80 L50,100 M100,30 L70,45 L80,70 L40,90" stroke="rgba(255,255,255,1)" stroke-width="4" fill="none"/></svg>')`;

            function breakIce(el) {{
                if(el.classList.contains('shattered')) return;
                
                el.classList.remove('shake');
                void el.offsetWidth; 
                el.classList.add('shake');

                let hits = parseInt(el.getAttribute('data-hits'));
                hits++;
                el.setAttribute('data-hits', hits);
                
                if(hits === 1) {{
                    playSound(crackSound);
                    el.style.backgroundImage = crack1 + ", linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(165,243,252,0.6) 100%)";
                }} else if(hits === 2) {{
                    playSound(crackSound);
                    el.style.backgroundImage = crack2 + ", linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(165,243,252,0.6) 100%)";
                }} else {{
                    playSound(smashSound);
                    el.classList.add('shattered');
                    setTimeout(() => {{ el.style.display = 'none'; }}, 1000);
                }}
            }}

            const antContainer = document.getElementById('antContainer');
            const bread = document.getElementById('bread');
            let score = 0;
            let level = 1;
            let breadScale = 1.0;
            let gameActive = false;
            let spawnInterval;
            let moveIntervals = [];
            let spawnRate = 1500; 

            function startGame() {{
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('gameOverScreen').style.display = 'none';
                score = 0; level = 1; breadScale = 1.0; spawnRate = 1500; gameActive = true;
                updateHUD();
                bread.style.transform = `translate(-50%, -50%) scale(1)`;
                
                document.querySelectorAll('.ant').forEach(a => a.remove());
                moveIntervals.forEach(clearInterval);
                moveIntervals = [];
                
                gameLoop();
            }}

            function gameLoop() {{
                if(!gameActive) return;
                spawnAnt();
                spawnInterval = setTimeout(gameLoop, spawnRate);
            }}

            function updateHUD() {{
                document.getElementById('scoreDisplay').innerText = `Score: ${{score}}`;
                document.getElementById('levelDisplay').innerText = `Lv: ${{level}}`;
            }}

            function spawnAnt() {{
                if(!gameActive) return;
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
                    if(!gameActive) return;
                    playSound(squishSound);
                    
                    score += 10;
                    if(score % 100 === 0) {{ 
                        level++; 
                        spawnRate = Math.max(400, spawnRate - 200); 
                    }}
                    updateHUD();

                    let crack = document.createElement('div'); crack.className = 'screen-crack'; crack.innerHTML = '🕸️'; 
                    crack.style.left = (parseFloat(this.style.left) + 15) + 'px'; 
                    crack.style.top = (parseFloat(this.style.top) + 15) + 'px'; 
                    antContainer.appendChild(crack);
                    this.remove(); 
                    setTimeout(() => {{ crack.remove(); }}, 800);
                }});
            }}

            function moveAntToBread(ant) {{
                let speed = 2 + (level * 0.5); 
                
                let mInterval = setInterval(() => {{
                    if(!gameActive || !document.body.contains(ant)) {{ clearInterval(mInterval); return; }}
                    
                    let currentX = parseFloat(ant.style.left); let currentY = parseFloat(ant.style.top);
                    let targetX = antContainer.clientWidth / 2 - 15; 
                    let targetY = antContainer.clientHeight / 2 - 15;
                    
                    let dx = targetX - currentX; let dy = targetY - currentY;
                    let distance = Math.sqrt(dx*dx + dy*dy);
                    
                    if(distance < 40) {{ 
                        playSound(eatSound);
                        breadScale -= 0.15; 
                        if(breadScale <= 0.2) {{
                            breadScale = 0;
                            gameOver();
                        }}
                        bread.style.transform = `translate(-50%, -50%) scale(${{breadScale}})`;
                        ant.remove();
                        clearInterval(mInterval);
                        return;
                    }}
                    
                    let newX = currentX + (dx / distance) * speed;
                    let newY = currentY + (dy / distance) * speed;
                    
                    let angle = Math.atan2(dy, dx) * 180 / Math.PI;
                    ant.style.transform = `rotate(${{angle + 90}}deg)`; 
                    ant.style.left = newX + 'px'; ant.style.top = newY + 'px';
                }}, 50); 
                moveIntervals.push(mInterval);
            }}

            function gameOver() {{
                gameActive = false;
                clearTimeout(spawnInterval);
                document.getElementById('gameOverScreen').style.display = 'flex';
                document.getElementById('finalScoreText').innerText = `최종 점수: ${{score}}점`;
                
                if(score > 0) {{
                    document.getElementById('autoSubmitMsg').innerText = "점수를 서버에 자동 등록 중입니다... ⏳";
                    
                    try {{
                        const parentDoc = window.parent.document;
                        let scoreInput = null;
                        parentDoc.querySelectorAll('label').forEach(l => {{
                            if(l.innerText.includes('auto_score_input_hidden_123')) {{
                                scoreInput = l.closest('div[data-testid="stTextInput"]').querySelector('input');
                            }}
                        }});
                        
                        if(scoreInput) {{
                            let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeInputValueSetter.call(scoreInput, score);
                            scoreInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            
                            setTimeout(() => {{
                                parentDoc.querySelectorAll('button').forEach(b => {{
                                    if(b.innerText.includes('auto_score_submit_hidden_123')) {{
                                        b.click();
                                        document.getElementById('autoSubmitMsg').innerText = "등록 완료! 랭킹이 갱신됩니다. ✅";
                                    }}
                                }});
                            }}, 500);
                        }} else {{
                            document.getElementById('autoSubmitMsg').innerText = "자동 등록을 지원하지 않는 환경입니다.";
                        }}
                    }} catch(e) {{
                        document.getElementById('autoSubmitMsg').innerText = "자동 등록 실패 (보안 설정).";
                    }}
                }} else {{
                    document.getElementById('autoSubmitMsg').innerText = "0점은 등록되지 않습니다. 다시 도전하세요!";
                }}
            }}
        </script>
        </body>
        </html>
        """
        components.html(game_html, height=700, scrolling=False)

        # ------------------------------------------
        # 🏆 명예의 전당 (랭킹 시스템)
        # ------------------------------------------
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("### 🏆 식빵 수호대 명예의 전당")
        
        c.execute("SELECT user_id, MAX(score) as max_score FROM game_scores GROUP BY user_id ORDER BY max_score DESC LIMIT 5")
        rankings = c.fetchall()
        
        if not rankings:
            st.info("아직 등록된 랭킹이 없습니다. 첫 번째 랭커가 되어보세요!")
        else:
            for i, rank in enumerate(rankings):
                r_user, r_score = rank
                if i == 0: rank_class, icon = "rank-1", "🥇"
                elif i == 1: rank_class, icon = "rank-2", "🥈"
                elif i == 2: rank_class, icon = "rank-3", "🥉"
                else: rank_class, icon = "rank-other", f"{i+1}위"
                
                st.markdown(f"""
                <div class="ranking-card {rank_class}">
                    <div>{icon} {r_user}님</div>
                    <div>{r_score} 점</div>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 6] D-day 일정 관리
    # ------------------------------------------
    with tab6:
        st.markdown("### 📅 나만의 소중한 일정 관리")
        st.markdown("기념일, 자격증 시험, 휴가 등 기다려지는 날들을 기록해 보세요.")
        
        st.write("")
        dday_title = st.text_input("일정 이름 (예: 여름휴가, 승진 시험)", key="dday_title")
        dday_date = st.date_input("날짜 선택", key="dday_date")
            
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
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-left: 5px solid {color}; border-radius: 12px; padding: 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                    <div>
                        <div style="color: #cbd5e1; font-size: 13px; margin-bottom: 5px;">{t_date_str}</div>
                        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">{title}</div>
                    </div>
                    <div style="color: {color}; font-size: 24px; font-weight: 900; text-shadow: 0 0 10px rgba(255,255,255,0.2);">{d_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("❌ 삭제", key=f"del_dday_{d_id}", use_container_width=True):
                    c.execute("DELETE FROM dday_records WHERE id=?", (d_id,))
                    conn.commit()
                    st.rerun()
                st.write("")

# ==========================================
# [푸터] 면책 조항 (로그인 후 화면 하단)
# ==========================================
st.markdown("""
<hr style="border-color: rgba(255,255,255,0.1); margin-top: 40px;">
<div style="text-align: center; color: #94a3b8; font-size: 13px; line-height: 1.6; word-break: keep-all;">
    ⚠️ <b>본 '마음 상담소'의 답변은 AI에 의해 생성된 위로 메시지이며, 전문적인 의학적 진단이나 심리 치료를 대체할 수 없습니다.</b><br><br>
    심각한 우울감이나 스트레스가 지속될 경우, <b>사내 심리상담센터(심즈업 심리상담 070-4192-7762)</b> 또는 전문 의료기관의 도움을 받으시길 권장합니다.
</div>
<div style="text-align: center; color: #64748b; font-size: 11px; margin-top: 20px;">
    © POSCO FUTURE M Smart Mind Care Center. All rights reserved.
</div>
""", unsafe_allow_html=True)
