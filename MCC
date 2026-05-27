import streamlit as st
import sqlite3
import datetime
import time
import random

# ==========================================
# [초기 설정] 페이지 세팅
# ==========================================
st.set_page_config(page_title="나만의 마음 상담소", page_icon="🌿", layout="wide")

# ==========================================
# [데이터베이스 설정] SQLite3를 이용한 데이터 축적
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
# [CSS] 마음을 편안하게 해주는 다크 & 네온 테마
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #e2e8f0; font-family: 'Pretendard', 'Segoe UI', sans-serif; }
    
    .main-title { 
        font-size: 42px; font-weight: 900; 
        background: -webkit-linear-gradient(45deg, #34d399, #3b82f6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(52, 211, 153, 0.3);
        margin-bottom: 5px; letter-spacing: -1px; text-align: center;
    }
    .sub-title { color: #94a3b8; font-size: 18px; margin-bottom: 30px; font-weight: 500; text-align: center; }
    
    .login-box {
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px);
        border: 1px solid #334155; border-radius: 16px; padding: 40px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        max-width: 400px; margin: 50px auto; text-align: center;
    }
    
    .record-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-left: 4px solid #3b82f6; border-radius: 12px; padding: 20px;
        margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .record-card:hover { transform: translateY(-3px); border-left: 4px solid #34d399; }
    .record-date { color: #34d399; font-size: 13px; font-weight: bold; margin-bottom: 8px; }
    .record-worry { color: #f8fafc; font-size: 16px; font-weight: 600; margin-bottom: 12px; line-height: 1.5; }
    .record-answer { color: #cbd5e1; font-size: 15px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; line-height: 1.6; }
    
    div.stButton > button {
        background: linear-gradient(45deg, #3b82f6, #2dd4bf); color: white; 
        border: none; border-radius: 8px; font-weight: bold; width: 100%; height: 45px;
        transition: all 0.3s;
    }
    div.stButton > button:hover { box-shadow: 0 0 15px rgba(45, 212, 191, 0.5); transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리] 로그인 유지
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'emp_id' not in st.session_state:
    st.session_state['emp_id'] = ""

# ==========================================
# [함수] AI 모의 답변 생성기
# ==========================================
def generate_comfort_message(worry_text):
    worry_text = worry_text.lower()
    if any(word in worry_text for word in ["사람", "인간관계", "상사", "동료", "팀장"]):
        return "직장 생활에서 가장 힘든 게 사람 문제라고 하죠. 당신의 잘못이 아닙니다. 오늘은 스스로를 위해 맛있는 저녁을 선물하는 건 어떨까요?"
    elif any(word in worry_text for word in ["일", "업무", "야근", "실수", "프로젝트"]):
        return "업무에 대한 책임감이 강하신 분이군요. 하지만 완벽하지 않아도 괜찮습니다. 잠시 숨을 고르고, 우선순위를 다시 정리해 보세요."
    elif any(word in worry_text for word in ["퇴사", "이직", "진로", "미래"]):
        return "새로운 길을 고민하는 것 자체가 당신이 성장하고 싶다는 증거입니다. 조급해하지 말고, 당신의 마음이 진정으로 향하는 곳을 천천히 탐색해 보세요."
    else:
        return "많이 지치고 힘드셨군요. 이곳에 털어놓는 것만으로도 마음의 짐이 조금은 가벼워지길 바랍니다. 제가 항상 당신의 편이 되어 드릴게요."

# ==========================================
# [화면 구성] 1. 로그인 화면
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("<div class='main-title'>🌿 마음 상담소</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>당신의 지친 하루를 위로해 드립니다. 편하게 털어놓으세요.</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: white; margin-bottom: 20px;'>사원 인증</h3>", unsafe_allow_html=True)
        
        emp_input = st.text_input("사번을 입력해주세요 (예: 123456)", placeholder="사번 입력")
        
        if st.button("입장하기"):
            if emp_input.strip() == "":
                st.warning("사번을 입력해주세요.")
            else:
                st.session_state['logged_in'] = True
                st.session_state['emp_id'] = emp_input
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# [화면 구성] 2. 메인 서비스 화면 (로그인 후)
# ==========================================
else:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown(f"<div class='main-title' style='text-align: left;'>🌿 {st.session_state['emp_id']}님의 마음 상담소</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title' style='text-align: left;'>어떤 고민이든 괜찮습니다. 당신의 이야기를 들려주세요.</div>", unsafe_allow_html=True)
    with col_logout:
        st.write("") 
        if st.button("🔒 로그아웃"):
            st.session_state['logged_in'] = False
            st.session_state['emp_id'] = ""
            st.rerun()

    # 탭 구성에 '수면 & 힐링 사운드' 추가
    tab1, tab2, tab3, tab4 = st.tabs(["💬 새로운 상담", "📚 나의 마음 기록", "📊 스트레스 지수 분석", "🌙 수면 & 힐링 사운드"])

    # ------------------------------------------
    # [탭 1] 새로운 상담
    # ------------------------------------------
    with tab1:
        st.markdown("### 📝 오늘의 고민을 적어주세요")
        worry_input = st.text_area("누구에게도 말하지 못한 고민, 스트레스 받는 일들을 자유롭게 적어주세요.", height=150)
        
        if st.button("상담 받기 ✨"):
            if worry_input.strip() == "":
                st.warning("고민 내용을 조금이라도 적어주세요.")
            else:
                with st.spinner("당신의 마음을 읽고 위로의 말을 준비하고 있습니다..."):
                    time.sleep(1.5)
                    answer = generate_comfort_message(worry_input)
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    c.execute("INSERT INTO counseling_records (emp_id, date, worry, answer) VALUES (?, ?, ?, ?)", 
                              (st.session_state['emp_id'], now, worry_input, answer))
                    conn.commit()
                    
                    st.success("상담이 완료되었습니다. 아래 답변을 확인해주세요.")
                    st.markdown(f"""
                    <div style="background: rgba(52, 211, 153, 0.1); border: 1px solid #34d399; border-radius: 12px; padding: 25px; margin-top: 20px;">
                        <h4 style="color: #34d399; margin-bottom: 15px;">💌 마음 상담소의 답장</h4>
                        <p style="font-size: 16px; line-height: 1.8; color: #f8fafc;">{answer}</p>
                    </div>
                    """, unsafe_allow_html=True)

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
        st.markdown("간단한 수식을 통해 현재 나의 스트레스 상태를 점검해 볼 수 있습니다.")
        st.info("※ 아래 수식은 예시를 위한 가상의 스트레스 산출 공식입니다.")
        
        st.markdown("스트레스 지수($S$)는 업무량($W$), 대인관계 난이도($R$), 그리고 휴식 시간($B$)에 의해 결정됩니다.")
        

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.latex(r"S = \left( \frac{W \times 1.5 + R^2}{B + 1} \right) \times 10")
        
        st.markdown("<br><br>", unsafe_allow_html=True)


        st.markdown("""
        - **$W$ (Workload)**: 주간 초과 근무 시간
        - **$R$ (Relationship)**: 대인관계 스트레스 척도 (1~5점)
        - **$B$ (Break)**: 하루 평균 온전한 휴식 시간 (시간)
        """)
        
        col_w, col_r, col_b = st.columns(3)
        with col_w: w_val = st.number_input("주간 초과 근무 시간 (W)", min_value=0, max_value=52, value=5)
        with col_r: r_val = st.slider("대인관계 스트레스 (R)", 1, 5, 3)
        with col_b: b_val = st.number_input("하루 평균 휴식 시간 (B)", min_value=0, max_value=10, value=2)
        
        s_score = ((w_val * 1.5 + r_val**2) / (b_val + 1)) * 10
        
        st.markdown(f"#### 📊 당신의 현재 예상 스트레스 지수: **<span style='color:#f43f5e;'>{s_score:.1f}점</span>**", unsafe_allow_html=True)

    # ------------------------------------------
    # [탭 4] 수면 & 힐링 사운드 (신규 추가)
    # ------------------------------------------
    with tab4:
        st.markdown("### 🌙 깊은 수면과 휴식을 위한 사운드")
        st.markdown("<p style='color: #94a3b8; font-size: 15px;'>스트레스 해소의 1위는 <b>충분한 수면</b>입니다. 마음을 편안하게 해주는 소리를 들으며 지친 뇌를 쉬게 해주세요.</p>", unsafe_allow_html=True)
        
        # 사운드 선택 라디오 버튼
        sound_choice = st.radio(
            "듣고 싶은 테마를 선택하세요 (재생 버튼을 누르면 연속 재생됩니다):",
            ["🔥 장작 타는 소리 (모닥불 ASMR)", "🌧️ 차분해지는 빗소리", "🎵 432Hz 심신 안정 주파수", "🌊 잔잔한 파도 소리"],
            horizontal=True
        )
        
        st.markdown("<hr style='border-color: #334155;'>", unsafe_allow_html=True)
        
        # 선택된 테마에 맞는 유튜브 영상(ASMR) 임베드
        if "장작" in sound_choice:
            st.markdown("#### 🔥 따뜻한 모닥불 소리 (8시간 연속)")
            st.video("https://www.youtube.com/watch?v=L_LUpnjgPso")
            st.caption("장작이 타들어가는 백색소음은 심장 박동을 안정시키고 불안감을 낮춰줍니다.")
            
        elif "빗소리" in sound_choice:
            st.markdown("#### 🌧️ 텐트 위로 떨어지는 빗소리 (10시간 연속)")
            st.video("https://www.youtube.com/watch?v=mPZkdNFkNps")
            st.caption("일정한 패턴의 빗소리는 뇌파를 알파파로 유도하여 깊은 수면을 돕습니다.")
            
        elif "주파수" in sound_choice:
            st.markdown("#### 🎵 432Hz 힐링 주파수 (수면 유도)")
            st.video("https://www.youtube.com/watch?v=tNkZsRW7hXc")
            st.caption("우주의 자연 주파수라 불리는 432Hz는 긴장된 근육을 이완시키고 스트레스를 해소합니다.")
            
        elif "파도" in sound_choice:
            st.markdown("#### 🌊 잔잔한 밤바다 파도 소리 (8시간 연속)")
            st.video("https://www.youtube.com/watch?v=nepNTqwI0mM")
            st.caption("밀려오고 나가는 파도 소리에 맞춰 천천히 심호흡을 해보세요.")

# ==========================================
# [푸터] 면책 조항
# ==========================================
st.markdown("""
<hr style="border-color: #334155; margin-top: 50px;">
<div style="text-align: center; color: #64748b; font-size: 12px; line-height: 1.6;">
    ⚠️ <b>본 '마음 상담소'의 답변은 AI 알고리즘에 의해 생성된 위로 메시지이며, 전문적인 의학적 진단이나 심리 치료를 대체할 수 없습니다.</b><br>
    심각한 우울감이나 스트레스가 지속될 경우, 사내 심리상담센터(EAP) 또는 전문 의료기관의 도움을 받으시길 권장합니다.<br>
    © Mind Care Center. All rights reserved.
</div>
""", unsafe_allow_html=True)
