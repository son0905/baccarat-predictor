import streamlit as st
import random
from collections import Counter

# 초기 슈 카드 구성 (6덱 기준, 312장)
def create_shoe():
    deck = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    shoe = deck * 24  # 24 = 6덱 * 4무늬 = 312장 / 13종류
    random.shuffle(shoe)
    return shoe

def card_value(card):
    if card in ['10', 'J', 'Q', 'K']:
        return 0
    elif card == 'A':
        return 1
    else:
        return int(card)

def hand_score(hand):
    return sum([card_value(c) for c in hand]) % 10

if 'shoe' not in st.session_state:
    st.session_state.shoe = create_shoe()

if 'games' not in st.session_state:
    st.session_state.games = []

st.title("V7: 슈 기반 카드 추적 시스템")
st.write("실제 슈(6덱) 구성으로 카드 소모를 추적하며 게임 진행!")

# 카드 뽑기 함수
def draw_cards(num):
    drawn = []
    for _ in range(num):
        if st.session_state.shoe:
            drawn.append(st.session_state.shoe.pop(0))
    return drawn

# 한 게임 실행
if st.button("게임 진행 (카드 자동 소모)"):
    if len(st.session_state.shoe) < 6:
        st.warning("슈에 카드가 부족합니다. 새 슈를 생성합니다.")
        st.session_state.shoe = create_shoe()

    player = draw_cards(2)
    banker = draw_cards(2)

    p_score = hand_score(player)
    b_score = hand_score(banker)

    # 내추럴
    if p_score < 8 and b_score < 8:
        if p_score <= 5:
            player += draw_cards(1)

        # 복잡한 뱅커 규칙 생략: 간단 룰로 처리
        if b_score <= 5:
            banker += draw_cards(1)

    p_score = hand_score(player)
    b_score = hand_score(banker)

    if p_score > b_score:
        result = 'Player'
    elif b_score > p_score:
        result = 'Banker'
    else:
        result = 'Tie'

    st.session_state.games.append({
        'Player': player,
        'Banker': banker,
        'P_Score': p_score,
        'B_Score': b_score,
        'Result': result
    })

    st.success(f"게임 결과: {result}")

# 기록 출력
if st.session_state.games:
    st.subheader("게임 기록")
    for i, g in enumerate(st.session_state.games):
        st.write(f"Game {i+1}: {g['Player']} ({g['P_Score']}) vs {g['Banker']} ({g['B_Score']}) → {g['Result']}")

    results = [g['Result'] for g in st.session_state.games]
    count = Counter(results)
    total = len(results)

    p_rate = count['Player'] / total if 'Player' in count else 0
    b_rate = count['Banker'] / total if 'Banker' in count else 0
    t_rate = count['Tie'] / total if 'Tie' in count else 0

    suggestion = max(("Player", p_rate), ("Banker", b_rate), ("Tie", t_rate), key=lambda x: x[1])

    st.subheader("다음 게임 예측")
    st.write(f"예측: **{suggestion[0]}** (확률: {suggestion[1]*100:.1f}%)")

    st.info(f"남은 카드 수: {len(st.session_state.shoe)}장")
