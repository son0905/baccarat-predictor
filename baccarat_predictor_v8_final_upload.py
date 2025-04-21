import streamlit as st
from collections import Counter

st.set_page_config(page_title="V8 바카라 예측기", page_icon="🎴")
st.title("🎴 V8: 실제 룰 기반 바카라 카드 예측기")
st.markdown("""
플레이어와 뱅커의 카드를 입력하면 실제 바카라 룰에 따라 3번째 카드 여부를 자동 계산하고,
입력된 기록을 바탕으로 다음 결과를 예측합니다.
""")

# 카드 값 계산 함수
def card_value(card):
    card = card.upper()
    if card in ['J', 'Q', 'K', '10']: return 0
    elif card == 'A': return 1
    else: return int(card)

# 점수 계산 함수
def calc_score(cards):
    return sum(card_value(c) for c in cards) % 10

# 세 번째 카드 룰 적용
# 결과: (플레이어 카드, 뱅커 카드)
def apply_third_card_rule(p_cards, b_cards):
    p_score = calc_score(p_cards)
    b_score = calc_score(b_cards)

    p_draws = len(p_cards) == 2 and p_score <= 5
    if p_draws:
        p_third = st.session_state.get('p3')
        if p_third:
            p_cards.append(p_third)
            p_score = calc_score(p_cards)

    # 뱅커 룰 (복잡함)
    b_draws = False
    p_third_val = card_value(p_cards[2]) if len(p_cards) == 3 else None

    if len(b_cards) == 2:
        if len(p_cards) == 2:
            if b_score <= 5:
                b_draws = True
        else:
            if b_score <= 2:
                b_draws = True
            elif b_score == 3 and p_third_val != 8:
                b_draws = True
            elif b_score == 4 and p_third_val in [2, 3, 4, 5, 6, 7]:
                b_draws = True
            elif b_score == 5 and p_third_val in [4, 5, 6, 7]:
                b_draws = True
            elif b_score == 6 and p_third_val in [6, 7]:
                b_draws = True

    if b_draws:
        b_third = st.session_state.get('b3')
        if b_third:
            b_cards.append(b_third)
            b_score = calc_score(b_cards)

    return p_cards, b_cards, p_score, b_score

# 입력 필드
p_input = st.text_input("플레이어 카드 2장 (예: 9,K)", key="p")
b_input = st.text_input("뱅커 카드 2장 (예: 3,4)", key="b")

p_cards = [c.strip() for c in p_input.split(",") if c.strip()]
b_cards = [c.strip() for c in b_input.split(",") if c.strip()]

# 플레이어 3번째 카드 입력 조건부 표시
if len(p_cards) == 2 and calc_score(p_cards) <= 5:
    st.session_state.p3 = st.text_input("플레이어 3번째 카드 (없으면 엔터)", key="p3_input")

# 뱅커 3번째 카드 입력 조건부 표시 (룰이 적용될 수 있는 상황에만)
if len(b_cards) == 2:
    p_temp = p_cards.copy()
    if len(p_temp) == 2 and calc_score(p_temp) <= 5:
        if 'p3' in st.session_state:
            p_temp.append(st.session_state.p3)
    p_third_val = card_value(p_temp[2]) if len(p_temp) == 3 else None
    b_score = calc_score(b_cards)
    cond = (
        b_score <= 2 or
        (b_score == 3 and p_third_val != 8) or
        (b_score == 4 and p_third_val in [2,3,4,5,6,7]) or
        (b_score == 5 and p_third_val in [4,5,6,7]) or
        (b_score == 6 and p_third_val in [6,7])
    )
    if cond:
        st.session_state.b3 = st.text_input("뱅커 3번째 카드 (없으면 엔터)", key="b3_input")

# 결과 기록용 세션
if 'records' not in st.session_state:
    st.session_state.records = []

# 버튼: 기록 추가
if st.button("게임 기록 추가"):
    if len(p_cards) >= 2 and len(b_cards) >= 2:
        p_cards, b_cards, p_score, b_score = apply_third_card_rule(p_cards, b_cards)

        if p_score > b_score:
            result = "Player"
        elif b_score > p_score:
            result = "Banker"
        else:
            result = "Tie"

        st.session_state.records.append({
            "Player": p_cards,
            "Banker": b_cards,
            "P_Score": p_score,
            "B_Score": b_score,
            "Result": result
        })

        st.success(f"결과 기록됨: {result}")
        st.session_state.p = ""
        st.session_state.b = ""
        st.session_state.p3 = ""
        st.session_state.b3 = ""
    else:
        st.error("카드는 반드시 2장씩 입력되어야 합니다.")

# 결과 테이블
if st.session_state.records:
    st.subheader("📋 게임 기록")
    for i, g in enumerate(st.session_state.records):
        st.write(f"Game {i+1}: {g['Player']} ({g['P_Score']}) vs {g['Banker']} ({g['B_Score']}) → {g['Result']}")

    # 예측
    results = [g['Result'] for g in st.session_state.records]
    count = Counter(results)
    total = len(results)

    p_rate = count['Player'] / total if total else 0
    b_rate = count['Banker'] / total if total else 0
    t_rate = count['Tie'] / total if total else 0

    suggestion = max(("Player", p_rate), ("Banker", b_rate), ("Tie", t_rate), key=lambda x: x[1])

    st.subheader("🔮 다음 게임 예측")
    st.write(f"예측: **{suggestion[0]}** (확률: {suggestion[1]*100:.1f}%)")
