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
model = genai.GenerativeModel('gemini-1.5-flash') 

# ==========================================
# [데이터베이스 설정] SQLite3
# ==========================================
conn = sqlite3.connect('mind_care_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS counseling_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        worry TEXT,
        answer TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        password TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS dday_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        title TEXT,
        target_date TEXT
    )
''')
conn.commit()

# ==========================================
# [CSS] 30년차 전문가의 UI/UX 디자인
# ==========================================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; font-family: 'Pretendard', 'Segoe UI', sans-serif; }
    
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

    div[data-testid="stButton"] > button {
        background: linear-gradient(45deg, #c084fc, #fbcfe8) !important; color: #1e1b4b !important; 
        font-weight: 900 !important; font-size: 18px !important; padding: 10px 20px !important;
        border: none !important; border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(192, 132, 252, 0.5) !important; transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(192, 132, 252, 0.8) !important; }

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

    .record-card {
        background: rgba(255,255,255,0.05); border-left: 5px solid #c084fc; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .record-date { color: #fbcfe8; font-size: 14px; font-weight: bold; margin-bottom: 10px; }
    .record-worry { color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 15px; line-height: 1.6; }
    .record-answer { color: #e2e8f0; font-size: 17px; background: rgba(0,0,0,0.4); padding: 20px; border-radius: 10px; line-height: 1.7; }
    
    .chat-user { text-align: right; margin-bottom: 15px; }
    .chat-user span { background-color: #334155; padding: 12px 20px; border-radius: 20px 20px 0 20px; display: inline-block; font-size: 17px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .chat-ai { text-align: left; margin-bottom: 25px; }
    .chat-ai span { background-color: rgba(192, 132, 252, 0.15); border: 1px solid #c084fc; padding: 15px 20px; border-radius: 20px 20px 20px 0; display: inline-block; font-size: 17px; line-height: 1.7; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }

    /* 사내상담센터 표 스타일 */
    .counseling-table {
        width: 100%; max-width: 900px; margin: 30px auto; border-collapse: collapse;
        background-color: rgba(255, 255, 255, 0.03); color: #e2e8f0; font-size: 15px;
        text-align: center; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .counseling-table th {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6); color: #ffffff;
        padding: 15px; font-weight: 900; border: 1px solid rgba(255, 255, 255, 0.1); font-size: 16px;
    }
    .counseling-table td {
        padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1); vertical-align: middle; line-height: 1.5;
    }
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
        # 불필요한 둥근 원(auth-box) 렌더링 오류 제거 완료
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

# ==========================================
# [화면 구성] 2. 메인 서비스 화면
# ==========================================
else:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown(f"<div class='neon-title' style='text-align: left; font-size: 40px;'>{st.session_state['user_id']}님의 마음 상담소</div>", unsafe_allow_html=True)
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
            submitted = st.form_submit_button("✨ AI 상담사에게 전송 ✨", use_container_width=True)
            
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
        st.markdown("### 🧠 직무 스트레스 자가 진단")
        st.markdown("스트레스 지수($S$)는 업무량($W$), 대인관계 난이도($R$), 그리고 휴식 시간($B$)에 의해 결정됩니다.")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.latex(r"S = \left( \frac{W \times 1.5 + R^2}{B + 1} \right) \times 10")
        st.markdown("<br><br>", unsafe_allow_html=True)

        col_w, col_r, col_b = st.columns(3)
        with col_w: w_val = st.number_input("주간 초과 근무 시간 (W)", min_value=0, max_value=52, value=5)
        with col_r: r_val = st.slider("대인관계 스트레스 (R)", 1, 5, 3)
        with col_b: b_val = st.number_input("하루 평균 휴식 시간 (B)", min_value=0, max_value=10, value=2)
        
        s_score = ((w_val * 1.5 + r_val**2) / (b_val + 1)) * 10
        st.markdown(f"#### 📊 당신의 현재 예상 스트레스 지수: **<span style='color:#fbcfe8; font-size: 28px;'>{s_score:.1f}점</span>**", unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 4] 수면 & 힐링 사운드
    # ------------------------------------------
    with tab4:
        st.markdown("### 🌙 깊은 수면과 휴식을 위한 사운드")
        sound_choice = st.radio("듣고 싶은 테마를 선택하세요:", ["🔥 장작 타는 소리", "🌧️ 차분해지는 빗소리", "🎵 432Hz 심신 안정 주파수", "🌊 잔잔한 파도 소리"], horizontal=True)
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        if "장작" in sound_choice: st.video("https://www.youtube.com/watch?v=peB0qS5A-jY") 
        elif "빗소리" in sound_choice: st.video("https://www.youtube.com/watch?v=mPZkdNFkNps")
        elif "주파수" in sound_choice: st.video("https://www.youtube.com/watch?v=8mAITcNlN7M") 
        elif "파도" in sound_choice: st.video("https://www.youtube.com/watch?v=bn9F19Hi1Lk")

    # ------------------------------------------
    # [탭 5] 스트레스 타파 미니게임
    # ------------------------------------------
    with tab5:
        st.markdown("### 🎮 스트레스 타파 미니게임")
        target_name = st.text_input("⌨️ 미운 사람의 이름이나 스트레스 원인을 적어보세요 (예: 월요병, 부장님)", value="스트레스")
        
        game_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: white; margin: 0; padding: 10px; background: transparent; user-select: none; }}
            h4 {{ color: #c084fc; margin-bottom: 15px; font-size: 20px; font-weight: bold; }}
            .keyboard-container {{ display: flex; justify-content: center; margin-bottom: 50px; padding: 20px; }}
            .keycap {{ width: 150px; height: 150px; background: #1e1e24; border-radius: 16px; box-shadow: 0 12px 0 #0a0a0c, 0 20px 25px rgba(0,0,0,0.6), inset 0 2px 5px rgba(255,255,255,0.1); display: flex; justify-content: center; align-items: center; font-size: 24px; font-weight: 900; color: #00f2fe; cursor: pointer; transition: all 0.05s; text-shadow: 0 0 10px rgba(0, 242, 254, 0.8); border: 1px solid #333; }}
            .keycap:active {{ box-shadow: 0 2px 0 #0a0a0c, 0 5px 10px rgba(0,0,0,0.6), inset 0 2px 5px rgba(255,255,255,0.1); transform: translateY(10px); color: #f43f5e; text-shadow: 0 0 15px rgba(244, 63, 94, 0.9); }}
            .ant-game-area {{ position: relative; width: 100%; height: 400px; background: radial-gradient(circle at center, #1e293b, #020617); border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: inset 0 0 50px rgba(0,0,0,0.8); cursor: crosshair; }}
            .ant {{ position: absolute; font-size: 40px; cursor: pointer; transition: transform 0.3s ease-out; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.5)); }}
            .splat {{ position: absolute; font-size: 45px; animation: fadeOut 1s forwards; pointer-events: none; }}
            @keyframes fadeOut {{ 0% {{ opacity: 1; transform: scale(1); }} 100% {{ opacity: 0; transform: scale(2); }} }}
            .btn {{ background: linear-gradient(45deg, #c084fc, #fbcfe8); color: #1e1b4b; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 900; cursor: pointer; margin-bottom: 15px; font-size: 18px; box-shadow: 0 4px 15px rgba(192, 132, 252, 0.4); transition: transform 0.1s; }}
            .btn:active {{ transform: scale(0.95); }}
        </style>
        </head>
        <body>
        <h4>⌨️ 분노의 기계식 키보드 (마구 눌러보세요!)</h4>
        <div class="keyboard-container"><div class="keycap" id="customKeycap">{target_name}</div></div>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 30px 0;">
        <h4>🐜 모던 스트레스 개미 잡기</h4>
        <button class="btn" onclick="spawnAnts(5)">+ 개미 5마리 소환</button>
        <div class="ant-game-area" id="antContainer"></div>
        <script>
            const mechSoundUrl = 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'; 
            const squishSoundUrl = 'https://assets.mixkit.co/active_storage/sfx/2783/2783-preview.mp3'; 
            function playSound(url) {{ let audio = new Audio(url); audio.volume = 0.7; audio.play().catch(e => console.log("Audio blocked")); }}
            const keycap = document.getElementById('customKeycap');
            keycap.addEventListener('pointerdown', function() {{ playSound(mechSoundUrl); }});
            const antContainer = document.getElementById('antContainer');
            function spawnAnts(count) {{
                for(let i=0; i<count; i++) {{
                    let ant = document.createElement('div'); ant.className = 'ant'; ant.innerHTML = '🐜';
                    let x = Math.random() * (antContainer.clientWidth - 50); let y = Math.random() * (antContainer.clientHeight - 50);
                    ant.style.left = x + 'px'; ant.style.top = y + 'px'; antContainer.appendChild(ant); moveAnt(ant);
                    ant.addEventListener('pointerdown', function() {{
                        playSound(squishSoundUrl);
                        let splat = document.createElement('div'); splat.className = 'splat'; splat.innerHTML = '💥';
                        splat.style.left = this.style.left; splat.style.top = this.style.top; antContainer.appendChild(splat);
                        this.remove(); setTimeout(() => {{ splat.remove(); }}, 1000);
                    }});
                }}
            }}
            function moveAnt(ant) {{
                let moveInterval = setInterval(() => {{
                    if(!document.body.contains(ant)) {{ clearInterval(moveInterval); return; }}
                    let currentX = parseFloat(ant.style.left); let currentY = parseFloat(ant.style.top);
                    let newX = currentX + (Math.random() * 80 - 40); let newY = currentY + (Math.random() * 80 - 40);
                    newX = Math.max(10, Math.min(newX, antContainer.clientWidth - 50)); newY = Math.max(10, Math.min(newY, antContainer.clientHeight - 50));
                    let angle = Math.atan2(newY - currentY, newX - currentX) * 180 / Math.PI;
                    ant.style.transform = `rotate(${{angle + 90}}deg)`; ant.style.left = newX + 'px'; ant.style.top = newY + 'px';
                }}, 600); 
            }}
            spawnAnts(4); 
        </script>
        </body>
        </html>
        """
        components.html(game_html, height=800, scrolling=False)

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
# [푸터] 사내상담센터 안내 및 면책 조항
# ==========================================
st.markdown("""
<hr style="border-color: rgba(255,255,255,0.1); margin-top: 50px;">
<div style="text-align: center; color: #94a3b8; font-size: 15px; line-height: 1.8;">
    ⚠️ <b>본 '마음 상담소'의 답변은 AI에 의해 생성된 위로 메시지이며, 전문적인 의학적 진단이나 심리 치료를 대체할 수 없습니다.</b><br>
    심각한 우울감이나 스트레스가 지속될 경우, <b>사내 심리상담센터(심즈업 심리상담 070-4192-7762)</b> 또는 전문 의료기관의 도움을 받으시길 권장합니다.
</div>

<!-- 사내상담센터 안내 표 -->
<table class="counseling-table">
    <thead>
        <tr>
            <th>지역</th>
            <th>근무지</th>
            <th>장소</th>
            <th>상담사명</th>
            <th>운영시간</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="4" style="font-weight: bold; color: #fbcfe8;">포항</td>
            <td>포항본사</td>
            <td rowspan="2">늘푸른솔커뮤니티센터<br>1층 회의실</td>
            <td rowspan="2">윤영임</td>
            <td rowspan="2">매주 화, 격주 목<br>09:00~18:00</td>
        </tr>
        <tr>
            <td>포항사업실</td>
        </tr>
        <tr>
            <td>포항양극재</td>
            <td>신사무동 4층 상담실</td>
            <td rowspan="2">김진아</td>
            <td>매주 월<br>09:00~18:00</td>
        </tr>
        <tr>
            <td>포항음극재</td>
            <td>사무동 1층 보건실</td>
            <td>격주 목<br>09:00~18:00</td>
        </tr>
        <tr>
            <td rowspan="2" style="font-weight: bold; color: #fbcfe8;">광양</td>
            <td>광양사업실</td>
            <td>태인동 사무소<br>3층 마음쉼터</td>
            <td>박정숙</td>
            <td>매주 수<br>09:00~18:00</td>
        </tr>
        <tr>
            <td>광양양극재</td>
            <td>창의동 2층<br>건강관리실 內 고충상담실</td>
            <td>이혜주</td>
            <td>매주 화<br>09:00~18:00</td>
        </tr>
        <tr>
            <td style="font-weight: bold; color: #fbcfe8;">세종</td>
            <td>세종음극재</td>
            <td>2공장 복지동<br>2층 혼창통</td>
            <td>김유진</td>
            <td>매주 화<br>10:00~19:00</td>
        </tr>
    </tbody>
</table>

<div style="text-align: center; color: #64748b; font-size: 13px; margin-top: 20px;">
    © POSCO FUTURE M Smart Mind Care Center. All rights reserved.
</div>
""", unsafe_allow_html=True)
