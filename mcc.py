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
GEMINI_API_KEY = "AIzaSyBP-dsVMyZCu-IcJ4ezOpvNCoUHQ8wFOKA"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') 

# ==========================================
# [데이터베이스 설정] SQLite3 (유저 테이블 추가)
# ==========================================
conn = sqlite3.connect('mind_care.db', check_same_thread=False)
c = conn.cursor()
# 상담 기록 테이블
c.execute('''
    CREATE TABLE IF NOT EXISTS counseling_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        worry TEXT,
        answer TEXT
    )
''')
# 유저 정보 테이블 (아이디, 비밀번호)
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

# ==========================================
# [CSS] 감성 디자인 & 가독성 & 모바일 반응형
# ==========================================
st.markdown("""
<style>
    /* 전체 배경: 차분하고 몽환적인 밤하늘 느낌 */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
        color: #f8fafc; font-family: 'Pretendard', 'Segoe UI', sans-serif; 
    }
    
    /* 메인 타이틀 */
    .main-title { 
        font-size: 46px; font-weight: 900; 
        background: -webkit-linear-gradient(45deg, #fbcfe8, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 25px rgba(192, 132, 252, 0.4);
        margin-bottom: 10px; letter-spacing: -1px; text-align: center;
    }
    .sub-title { color: #e2e8f0; font-size: 18px; margin-bottom: 40px; font-weight: 400; text-align: center; }
    
    /* 감성 포스트잇 디자인 */
    .post-it-container {
        display: flex; justify-content: center; gap: 20px; margin-bottom: 40px; flex-wrap: wrap;
    }
    .post-it {
        width: 180px; padding: 20px; background: #fef08a; color: #334155;
        font-size: 16px; font-weight: bold; text-align: center; border-radius: 2px 15px 15px 2px;
        box-shadow: 3px 5px 15px rgba(0,0,0,0.3); position: relative;
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
    }
    .post-it::before {
        content: ""; position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
        width: 40px; height: 15px; background: rgba(255,255,255,0.4); box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .p1 { transform: rotate(-3deg); background: #fef08a; }
    .p2 { transform: rotate(4deg); background: #bbf7d0; }
    .p3 { transform: rotate(-2deg); background: #fbcfe8; }

    /* 로그인/회원가입 박스 */
    .auth-box {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 20px; padding: 40px 30px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        width: 100%; max-width: 450px; margin: 0 auto;
    }
    
    /* 탭 스타일 커스텀 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255,255,255,0.05); border-radius: 8px 8px 0 0; 
        padding: 10px 20px; color: #cbd5e1; 
    }
    .stTabs [aria-selected="true"] { background-color: rgba(192, 132, 252, 0.2); color: #fbcfe8 !important; border-bottom: 2px solid #c084fc; }

    /* 기록 카드 */
    .record-card {
        background: rgba(255,255,255,0.03); border-left: 4px solid #c084fc; 
        border-radius: 12px; padding: 20px; margin-bottom: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); backdrop-filter: blur(5px);
    }
    .record-date { color: #fbcfe8; font-size: 13px; font-weight: bold; margin-bottom: 8px; }
    .record-worry { color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 12px; line-height: 1.5; }
    .record-answer { color: #e2e8f0; font-size: 15px; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; line-height: 1.6; }
    
    @media (max-width: 768px) {
        .main-title { font-size: 32px; }
        .post-it { width: 140px; font-size: 14px; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리]
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = ""
if 'id_checked' not in st.session_state:
    st.session_state['id_checked'] = False
if 'valid_id' not in st.session_state:
    st.session_state['valid_id'] = ""

# ==========================================
# [화면 구성] 1. 로그인 / 회원가입 화면
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("<div class='main-title'>🌙 스마트 마음 상담 센터</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>당신의 지친 하루를 따뜻하게 안아드릴게요. 편하게 기대어 보세요.</div>", unsafe_allow_html=True)
    
    # 감성 포스트잇
    st.markdown("""
    <div class="post-it-container">
        <div class="post-it p1">"괜찮아,<br>다 잘 될 거야 💛"</div>
        <div class="post-it p2">"오늘 하루도<br>정말 수고했어 🌿"</div>
        <div class="post-it p3">"넌 충분히<br>빛나고 있어 ✨"</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        auth_tab1, auth_tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])
        
        # --- 로그인 탭 ---
        with auth_tab1:
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw")
            if st.button("로그인", use_container_width=True):
                c.execute("SELECT * FROM users WHERE user_id=? AND password=?", (login_id, login_pw))
                if c.fetchone():
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = login_id
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                    
        # --- 회원가입 탭 ---
        with auth_tab2:
            reg_id = st.text_input("새 아이디", key="reg_id")
            if st.button("중복 확인"):
                if reg_id.strip() == "":
                    st.warning("아이디를 입력해주세요.")
                else:
                    c.execute("SELECT * FROM users WHERE user_id=?", (reg_id,))
                    if c.fetchone():
                        st.error("이미 사용 중인 아이디입니다.")
                        st.session_state['id_checked'] = False
                    else:
                        st.success("사용 가능한 아이디입니다!")
                        st.session_state['id_checked'] = True
                        st.session_state['valid_id'] = reg_id
            
            reg_pw = st.text_input("새 비밀번호", type="password", key="reg_pw")
            reg_pw_confirm = st.text_input("비밀번호 확인", type="password", key="reg_pw_confirm")
            
            if st.button("가입하기", use_container_width=True):
                if not st.session_state['id_checked'] or st.session_state['valid_id'] != reg_id:
                    st.error("아이디 중복 확인을 완료해주세요.")
                elif reg_pw == "" or reg_pw != reg_pw_confirm:
                    st.error("비밀번호가 일치하지 않거나 비어있습니다.")
                else:
                    c.execute("INSERT INTO users (user_id, password) VALUES (?, ?)", (reg_id, reg_pw))
                    conn.commit()
                    st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인해주세요.")
                    st.session_state['id_checked'] = False
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# [화면 구성] 2. 메인 서비스 화면
# ==========================================
else:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown(f"<div class='main-title' style='text-align: left; font-size: 36px;'>🌙 {st.session_state['user_id']}님의 마음 상담소</div>", unsafe_allow_html=True)
    with col_logout:
        st.write("") 
        if st.button("🔒 로그아웃", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = ""
            st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 AI 마음 상담", "📚 나의 기록", "📊 스트레스 분석", "🌙 수면 사운드", "🎮 스트레스 타파"])

    # ------------------------------------------
    # [탭 1] 새로운 상담 (Gemini AI 연동)
    # ------------------------------------------
    with tab1:
        st.markdown("### 📝 오늘의 고민을 적어주세요")
        worry_input = st.text_area("누구에게도 말하지 못한 고민, 스트레스 받는 일들을 자유롭게 적어주세요.", height=150)
        
        if st.button("상담 받기 ✨", use_container_width=True):
            if worry_input.strip() == "":
                st.warning("고민 내용을 조금이라도 적어주세요.")
            else:
                with st.spinner("AI 심리상담사가 당신의 마음을 읽고 위로의 말을 준비하고 있습니다..."):
                    try:
                        prompt = f"""
                        당신은 직장인들의 마음을 치유해주는 따뜻하고 공감 능력이 뛰어난 전문 심리 상담사입니다.
                        내담자가 다음과 같은 고민을 털어놓았습니다: "{worry_input}"
                        이 고민에 대해 깊이 공감해주고, 마음이 편안해질 수 있는 따뜻한 위로와 현실적이고 부드러운 조언을 3~4문단으로 작성해주세요.
                        말투는 '~해요', '~습니다' 등 다정하고 존중하는 어투를 사용하세요.
                        """
                        response = model.generate_content(prompt)
                        answer = response.text
                        
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        c.execute("INSERT INTO counseling_records (user_id, date, worry, answer) VALUES (?, ?, ?, ?)", 
                                  (st.session_state['user_id'], now, worry_input, answer))
                        conn.commit()
                        
                        st.success("상담이 완료되었습니다.")
                        st.markdown(f"""
                        <div style="background: rgba(192, 132, 252, 0.15); border: 1px solid #c084fc; border-radius: 12px; padding: 25px; margin-top: 20px;">
                            <h4 style="color: #fbcfe8; margin-bottom: 15px;">💌 마음 상담소의 답장</h4>
                            <p style="font-size: 16px; line-height: 1.8; color: #ffffff; white-space: pre-wrap;">{answer}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"AI 응답 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. (에러: {e})")

    # ------------------------------------------
    # [탭 2] 나의 마음 기록
    # ------------------------------------------
    with tab2:
        st.markdown("### 🕰️ 내가 걸어온 마음의 발자취")
        c.execute("SELECT date, worry, answer FROM counseling_records WHERE user_id=? ORDER BY id DESC", (st.session_state['user_id'],))
        records = c.fetchall()
        
        if not records:
            st.info("아직 상담 기록이 없습니다. 첫 번째 고민을 남겨보세요!")
        else:
            for record in records:
                date, worry, answer = record
                st.markdown(f"""
                <div class="record-card">
                    <div class="record-date">🕒 {date}</div>
                    <div class="record-worry">Q. {worry}</div>
                    <div class="record-answer">A. {answer}</div>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 3] 스트레스 지수 분석
    # ------------------------------------------
    with tab3:
        st.markdown("### 🧠 직무 스트레스 자가 진단")
        st.markdown("스트레스 지수($S$)는 업무량($W$), 대인관계 난이도($R$), 그리고 휴식 시간($B$)에 의해 결정됩니다.")
        
        # 수식 전후 개행 2번 유지
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.latex(r"S = \left( \frac{W \times 1.5 + R^2}{B + 1} \right) \times 10")
        st.markdown("<br><br>", unsafe_allow_html=True)

        col_w, col_r, col_b = st.columns(3)
        with col_w: w_val = st.number_input("주간 초과 근무 시간 (W)", min_value=0, max_value=52, value=5)
        with col_r: r_val = st.slider("대인관계 스트레스 (R)", 1, 5, 3)
        with col_b: b_val = st.number_input("하루 평균 휴식 시간 (B)", min_value=0, max_value=10, value=2)
        
        s_score = ((w_val * 1.5 + r_val**2) / (b_val + 1)) * 10
        st.markdown(f"#### 📊 당신의 현재 예상 스트레스 지수: **<span style='color:#fbcfe8;'>{s_score:.1f}점</span>**", unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 4] 수면 & 힐링 사운드 (재생 가능한 링크로 완벽 교체)
    # ------------------------------------------
    with tab4:
        st.markdown("### 🌙 깊은 수면과 휴식을 위한 사운드")
        sound_choice = st.radio(
            "듣고 싶은 테마를 선택하세요:",
            ["🔥 장작 타는 소리", "🌧️ 차분해지는 빗소리", "🎵 432Hz 심신 안정 주파수", "🌊 잔잔한 파도 소리"],
            horizontal=True
        )
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        # 임베드(외부 재생)가 확실히 허용된 범용 ASMR 영상들로 교체
        if "장작" in sound_choice:
            st.video("https://www.youtube.com/watch?v=peB0qS5A-jY") # Relaxing White Noise 채널
        elif "빗소리" in sound_choice:
            st.video("https://www.youtube.com/watch?v=mPZkdNFkNps")
        elif "주파수" in sound_choice:
            st.video("https://www.youtube.com/watch?v=8mAITcNlN7M") # Meditative Mind 채널 (432Hz)
        elif "파도" in sound_choice:
            st.video("https://www.youtube.com/watch?v=bn9F19Hi1Lk")

    # ------------------------------------------
    # [탭 5] 스트레스 타파 미니게임 (2026년형 모던 디자인)
    # ------------------------------------------
    with tab5:
        st.markdown("### 🎮 스트레스 타파 미니게임")
        
        # 키캡에 적을 이름 입력받기
        target_name = st.text_input("⌨️ 미운 사람의 이름이나 스트레스 원인을 적어보세요 (예: 월요병, 부장님)", value="스트레스")
        
        # HTML/JS 게임 엔진 (모던 UI 적용)
        game_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: white; margin: 0; padding: 10px; background: transparent; user-select: none; }}
            h4 {{ color: #c084fc; margin-bottom: 15px; font-size: 18px; }}
            
            /* 2026년형 RGB 기계식 키캡 디자인 */
            .keyboard-container {{ display: flex; justify-content: center; margin-bottom: 50px; padding: 20px; }}
            .keycap {{
                width: 140px; height: 140px;
                background: #1e1e24;
                border-radius: 16px;
                box-shadow: 0 12px 0 #0a0a0c, 0 20px 25px rgba(0,0,0,0.6), inset 0 2px 5px rgba(255,255,255,0.1);
                display: flex; justify-content: center; align-items: center;
                font-size: 22px; font-weight: 900; color: #00f2fe;
                cursor: pointer; transition: all 0.05s;
                text-shadow: 0 0 10px rgba(0, 242, 254, 0.8);
                border: 1px solid #333;
                position: relative;
            }}
            .keycap:active {{
                box-shadow: 0 2px 0 #0a0a0c, 0 5px 10px rgba(0,0,0,0.6), inset 0 2px 5px rgba(255,255,255,0.1);
                transform: translateY(10px);
                color: #f43f5e; text-shadow: 0 0 15px rgba(244, 63, 94, 0.9);
            }}
            
            /* 2026년형 모던 개미잡기 (Glassmorphism) */
            .ant-game-area {{ 
                position: relative; width: 100%; height: 400px; 
                background: radial-gradient(circle at center, #1e293b, #020617);
                border-radius: 20px; overflow: hidden; 
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: inset 0 0 50px rgba(0,0,0,0.8);
                cursor: crosshair;
            }}
            .ant {{ 
                position: absolute; font-size: 35px; cursor: pointer; 
                transition: transform 0.3s ease-out; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.5));
            }}
            .splat {{
                position: absolute; font-size: 40px;
                animation: fadeOut 1s forwards; pointer-events: none;
            }}
            @keyframes fadeOut {{
                0% {{ opacity: 1; transform: scale(1); }}
                100% {{ opacity: 0; transform: scale(2); }}
            }}
            .btn {{
                background: linear-gradient(45deg, #c084fc, #fbcfe8); color: #1e1b4b; 
                border: none; padding: 12px 24px; border-radius: 12px; 
                font-weight: 900; cursor: pointer; margin-bottom: 15px; font-size: 16px;
                box-shadow: 0 4px 15px rgba(192, 132, 252, 0.4); transition: transform 0.1s;
            }}
            .btn:active {{ transform: scale(0.95); }}
        </style>
        </head>
        <body>

        <h4>⌨️ 분노의 기계식 키보드 (마구 눌러보세요!)</h4>
        <div class="keyboard-container">
            <div class="keycap" id="customKeycap">{target_name}</div>
        </div>

        <hr style="border-color: rgba(255,255,255,0.1); margin: 30px 0;">

        <h4>🐜 모던 스트레스 개미 잡기</h4>
        <button class="btn" onclick="spawnAnts(5)">+ 개미 5마리 소환</button>
        <div class="ant-game-area" id="antContainer"></div>

        <script>
            // 고품질 효과음 (기계식 청축 소리 & 타격음)
            const mechSoundUrl = 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'; // 대체 타격음
            const squishSoundUrl = 'https://assets.mixkit.co/active_storage/sfx/2783/2783-preview.mp3'; // 찌직 소리

            function playSound(url) {{
                let audio = new Audio(url);
                audio.volume = 0.7;
                audio.play().catch(e => console.log("Audio blocked"));
            }}

            // 키캡 로직
            const keycap = document.getElementById('customKeycap');
            keycap.addEventListener('pointerdown', function() {{
                playSound(mechSoundUrl);
            }});

            // 개미 잡기 로직
            const antContainer = document.getElementById('antContainer');
            
            function spawnAnts(count) {{
                for(let i=0; i<count; i++) {{
                    let ant = document.createElement('div');
                    ant.className = 'ant';
                    ant.innerHTML = '🐜';
                    
                    let x = Math.random() * (antContainer.clientWidth - 40);
                    let y = Math.random() * (antContainer.clientHeight - 40);
                    ant.style.left = x + 'px';
                    ant.style.top = y + 'px';
                    
                    antContainer.appendChild(ant);
                    moveAnt(ant);

                    ant.addEventListener('pointerdown', function() {{
                        playSound(squishSoundUrl);
                        
                        // 모던 타격 이펙트 생성
                        let splat = document.createElement('div');
                        splat.className = 'splat';
                        splat.innerHTML = '💥';
                        splat.style.left = this.style.left;
                        splat.style.top = this.style.top;
                        antContainer.appendChild(splat);
                        
                        this.remove(); // 개미 즉시 삭제
                        setTimeout(() => {{ splat.remove(); }}, 1000);
                    }});
                }}
            }}

            function moveAnt(ant) {{
                let moveInterval = setInterval(() => {{
                    if(!document.body.contains(ant)) {{ clearInterval(moveInterval); return; }}
                    
                    let currentX = parseFloat(ant.style.left);
                    let currentY = parseFloat(ant.style.top);
                    
                    let newX = currentX + (Math.random() * 60 - 30);
                    let newY = currentY + (Math.random() * 60 - 30);
                    
                    newX = Math.max(10, Math.min(newX, antContainer.clientWidth - 40));
                    newY = Math.max(10, Math.min(newY, antContainer.clientHeight - 40));
                    
                    let angle = Math.atan2(newY - currentY, newX - currentX) * 180 / Math.PI;
                    ant.style.transform = `rotate(${{angle + 90}}deg)`;
                    
                    ant.style.left = newX + 'px';
                    ant.style.top = newY + 'px';
                }}, 600); 
            }}

            spawnAnts(4); // 시작 시 4마리
        </script>
        </body>
        </html>
        """
        components.html(game_html, height=800, scrolling=False)

# ==========================================
# [푸터] 면책 조항
# ==========================================
st.markdown("""
<hr style="border-color: rgba(255,255,255,0.1); margin-top: 50px;">
<div style="text-align: center; color: #94a3b8; font-size: 12px; line-height: 1.6;">
    ⚠️ <b>본 '마음 상담소'의 답변은 AI에 의해 생성된 위로 메시지이며, 전문적인 의학적 진단이나 심리 치료를 대체할 수 없습니다.</b><br>
    심각한 우울감이나 스트레스가 지속될 경우, 사내 심리상담센터(EAP) 또는 전문 의료기관의 도움을 받으시길 권장합니다.<br>
    © Smart Mind Care Center. All rights reserved.
</div>
""", unsafe_allow_html=True)
