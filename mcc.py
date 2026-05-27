import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import datetime
import time
import google.generativeai as genai

# ==========================================
# [초기 설정] 페이지 세팅
# ==========================================
st.set_page_config(page_title="나만의 마음 상담소", page_icon="🌿", layout="wide")

# ==========================================
# [Gemini AI 설정] 제공해주신 API 키 적용
# ==========================================
GEMINI_API_KEY = "AIzaSyBP-dsVMyZCu-IcJ4ezOpvNCoUHQ8wFOKA"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') 

# ==========================================
# [데이터베이스 설정] SQLite3
# ==========================================
conn = sqlite3.connect('mind_care.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS counseling_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        date TEXT,
        worry TEXT,
        answer TEXT
    )
''')
conn.commit()

# ==========================================
# [CSS] 가독성 개선 & 모바일 반응형 테마
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; font-family: 'Pretendard', 'Segoe UI', sans-serif; }
    
    .main-title { 
        font-size: 42px; font-weight: 900; 
        background: -webkit-linear-gradient(45deg, #34d399, #3b82f6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(52, 211, 153, 0.3);
        margin-bottom: 5px; letter-spacing: -1px; text-align: center;
    }
    .sub-title { color: #cbd5e1; font-size: 18px; margin-bottom: 30px; font-weight: 500; text-align: center; }
    
    .login-box {
        background: rgba(15, 23, 42, 0.95); 
        border: 2px solid #3b82f6; 
        border-radius: 16px; padding: 40px 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
        width: 90%; max-width: 400px; margin: 50px auto; text-align: center;
    }
    .login-box h3 { color: #ffffff !important; font-weight: 800; margin-bottom: 20px; }
    
    .record-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-left: 4px solid #3b82f6; border-radius: 12px; padding: 20px;
        margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .record-date { color: #34d399; font-size: 13px; font-weight: bold; margin-bottom: 8px; }
    .record-worry { color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 12px; line-height: 1.5; }
    .record-answer { color: #e2e8f0; font-size: 15px; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 8px; line-height: 1.6; }
    
    @media (max-width: 768px) {
        .main-title { font-size: 32px; }
        .sub-title { font-size: 15px; }
        .login-box { padding: 30px 20px; margin: 30px auto; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리]
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'emp_id' not in st.session_state:
    st.session_state['emp_id'] = ""

# ==========================================
# [화면 구성] 1. 로그인 화면
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("<div class='main-title'>🌿 마음 상담소</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>당신의 지친 하루를 위로해 드립니다. 편하게 털어놓으세요.</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='login-box'>
        <h3>사원 인증</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        emp_input = st.text_input("사번을 입력해주세요", placeholder="예: 123456", label_visibility="collapsed")
        if st.button("입장하기", use_container_width=True):
            if emp_input.strip() == "":
                st.warning("사번을 입력해주세요.")
            else:
                st.session_state['logged_in'] = True
                st.session_state['emp_id'] = emp_input
                st.rerun()

# ==========================================
# [화면 구성] 2. 메인 서비스 화면
# ==========================================
else:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown(f"<div class='main-title' style='text-align: left;'>🌿 {st.session_state['emp_id']}님의 마음 상담소</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title' style='text-align: left;'>어떤 고민이든 괜찮습니다. 당신의 이야기를 들려주세요.</div>", unsafe_allow_html=True)
    with col_logout:
        st.write("") 
        if st.button("🔒 로그아웃", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['emp_id'] = ""
            st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 새로운 상담", "📚 나의 마음 기록", "📊 스트레스 분석", "🌙 수면 사운드", "🎮 스트레스 타파"])

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
                        c.execute("INSERT INTO counseling_records (emp_id, date, worry, answer) VALUES (?, ?, ?, ?)", 
                                  (st.session_state['emp_id'], now, worry_input, answer))
                        conn.commit()
                        
                        st.success("상담이 완료되었습니다.")
                        st.markdown(f"""
                        <div style="background: rgba(52, 211, 153, 0.15); border: 1px solid #34d399; border-radius: 12px; padding: 25px; margin-top: 20px;">
                            <h4 style="color: #34d399; margin-bottom: 15px;">💌 마음 상담소의 답장</h4>
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
        c.execute("SELECT date, worry, answer FROM counseling_records WHERE emp_id=? ORDER BY id DESC", (st.session_state['emp_id'],))
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
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.latex(r"S = \left( \frac{W \times 1.5 + R^2}{B + 1} \right) \times 10")
        st.markdown("<br><br>", unsafe_allow_html=True)

        col_w, col_r, col_b = st.columns(3)
        with col_w: w_val = st.number_input("주간 초과 근무 시간 (W)", min_value=0, max_value=52, value=5)
        with col_r: r_val = st.slider("대인관계 스트레스 (R)", 1, 5, 3)
        with col_b: b_val = st.number_input("하루 평균 휴식 시간 (B)", min_value=0, max_value=10, value=2)
        
        s_score = ((w_val * 1.5 + r_val**2) / (b_val + 1)) * 10
        st.markdown(f"#### 📊 당신의 현재 예상 스트레스 지수: **<span style='color:#f43f5e;'>{s_score:.1f}점</span>**", unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 4] 수면 & 힐링 사운드
    # ------------------------------------------
    with tab4:
        st.markdown("### 🌙 깊은 수면과 휴식을 위한 사운드")
        sound_choice = st.radio(
            "듣고 싶은 테마를 선택하세요:",
            ["🔥 장작 타는 소리", "🌧️ 차분해지는 빗소리", "🎵 432Hz 심신 안정 주파수", "🌊 잔잔한 파도 소리"],
            horizontal=True
        )
        
        st.markdown("<hr style='border-color: #334155;'>", unsafe_allow_html=True)
        
        if "장작" in sound_choice:
            st.video("https://www.youtube.com/watch?v=UGqGMAZhhTo")
        elif "빗소리" in sound_choice:
            st.video("https://www.youtube.com/watch?v=mPZkdNFkNps")
        elif "주파수" in sound_choice:
            st.video("https://www.youtube.com/watch?v=7tNtU5XFwrU")
        elif "파도" in sound_choice:
            st.video("https://www.youtube.com/watch?v=bn9F19Hi1Lk")

    # ------------------------------------------
    # [탭 5] 스트레스 타파 미니게임
    # ------------------------------------------
    with tab5:
        st.markdown("### 🎮 스트레스 타파 미니게임")
        st.markdown("휴대폰 터치나 마우스 클릭으로 스트레스를 날려버리세요! (소리를 켜주세요 🔊)")
        
        game_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body { font-family: sans-serif; color: white; margin: 0; padding: 10px; background: transparent; user-select: none; }
            h4 { color: #34d399; margin-bottom: 10px; }
            
            .bubble-wrap { display: grid; grid-template-columns: repeat(auto-fill, minmax(50px, 1fr)); gap: 10px; margin-bottom: 40px; }
            .bubble { 
                width: 50px; height: 50px; background: rgba(255,255,255,0.2); 
                border-radius: 50%; cursor: pointer; 
                box-shadow: inset -5px -5px 10px rgba(0,0,0,0.5), inset 5px 5px 10px rgba(255,255,255,0.5);
                transition: transform 0.1s;
            }
            .bubble:active { transform: scale(0.9); }
            .bubble.popped { 
                background: rgba(255,255,255,0.05); box-shadow: none; cursor: default; 
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .ant-game-area { 
                position: relative; width: 100%; height: 350px; 
                background: #8b5a2b; border-radius: 12px; overflow: hidden; 
                border: 3px solid #5c3a21; cursor: crosshair;
            }
            .ant { 
                position: absolute; font-size: 30px; cursor: pointer; 
                transition: transform 0.2s linear;
            }
            .btn {
                background: #f43f5e; color: white; border: none; padding: 10px 20px;
                border-radius: 8px; font-weight: bold; cursor: pointer; margin-bottom: 10px;
                font-size: 16px;
            }
            .btn:active { background: #e11d48; }
        </style>
        </head>
        <body>

        <h4>🔵 무한 뽁뽁이 터뜨리기</h4>
        <div class="bubble-wrap" id="bubbleContainer"></div>

        <hr style="border-color: #334155; margin: 30px 0;">

        <h4>🐜 스트레스 개미 잡기</h4>
        <button class="btn" onclick="spawnAnts(5)">+ 개미 5마리 생성</button>
        <div class="ant-game-area" id="antContainer"></div>

        <script>
            const popSoundUrl = 'https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3';
            const squishSoundUrl = 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3';

            function playSound(url) {
                let audio = new Audio(url);
                audio.volume = 0.6;
                audio.play().catch(e => console.log("Audio play blocked by browser"));
            }

            const bubbleContainer = document.getElementById('bubbleContainer');
            for(let i=0; i<24; i++) {
                let b = document.createElement('div');
                b.className = 'bubble';
                b.addEventListener('pointerdown', function() {
                    if(!this.classList.contains('popped')) {
                        this.classList.add('popped');
                        playSound(popSoundUrl);
                    }
                });
                bubbleContainer.appendChild(b);
            }

            const antContainer = document.getElementById('antContainer');
            
            function spawnAnts(count) {
                for(let i=0; i<count; i++) {
                    let ant = document.createElement('div');
                    ant.className = 'ant';
                    ant.innerHTML = '🐜';
                    
                    let x = Math.random() * (antContainer.clientWidth - 30);
                    let y = Math.random() * (antContainer.clientHeight - 30);
                    ant.style.left = x + 'px';
                    ant.style.top = y + 'px';
                    
                    antContainer.appendChild(ant);
                    moveAnt(ant);

                    ant.addEventListener('pointerdown', function() {
                        if(this.innerHTML === '🐜') {
                            this.innerHTML = '💥'; 
                            playSound(squishSoundUrl);
                            this.style.transform = 'scale(1.5)';
                            setTimeout(() => { this.remove(); }, 1000);
                        }
                    });
                }
            }

            function moveAnt(ant) {
                setInterval(() => {
                    if(ant.innerHTML === '💥') return; 
                    
                    let currentX = parseFloat(ant.style.left);
                    let currentY = parseFloat(ant.style.top);
                    
                    let newX = currentX + (Math.random() * 40 - 20);
                    let newY = currentY + (Math.random() * 40 - 20);
                    
                    newX = Math.max(0, Math.min(newX, antContainer.clientWidth - 30));
                    newY = Math.max(0, Math.min(newY, antContainer.clientHeight - 30));
                    
                    let angle = Math.atan2(newY - currentY, newX - currentX) * 180 / Math.PI;
                    ant.style.transform = `rotate(${angle + 90}deg)`;
                    
                    ant.style.left = newX + 'px';
                    ant.style.top = newY + 'px';
                }, 500); 
            }

            spawnAnts(3);
        </script>
        </body>
        </html>
        """
        components.html(game_html, height=800, scrolling=False)

# ==========================================
# [푸터] 면책 조항
# ==========================================
st.markdown("""
<hr style="border-color: #334155; margin-top: 50px;">
<div style="text-align: center; color: #64748b; font-size: 12px; line-height: 1.6;">
    ⚠️ <b>본 '마음 상담소'의 답변은 AI에 의해 생성된 위로 메시지이며, 전문적인 의학적 진단이나 심리 치료를 대체할 수 없습니다.</b><br>
    심각한 우울감이나 스트레스가 지속될 경우, 사내 심리상담센터(EAP) 또는 전문 의료기관의 도움을 받으시길 권장합니다.<br>
    © Mind Care Center. All rights reserved.
</div>
""", unsafe_allow_html=True)
