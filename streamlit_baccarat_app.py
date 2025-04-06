import streamlit as st
from collections import Counter

def card_value(card):
    if card in ['10', 'J', 'Q', 'K']:
        return 0
    elif card == 'A':
        return 1
    else:
        return int(card)

def hand_score(cards):
    return sum([card_value(c) for c in cards]) % 10

games = []

st.title("바카라 게임 예측기")
st.write("카드를 입력해 게임 결과를 기록하고 다음 판 결과를 예측합니다.")

player_cards = st.text_input("플레이어 카드 (예: 9,K)").upper().split(',')
banker_cards = st.text_input("뱅커 카드 (예: 3,4)").upper().split(',')

if st.button("게임 기록 추가"):
    if len(player_cards) == 2 and len(banker_cards) == 2:
        p_score = hand_score(player_cards)
        b_score = hand_score(banker_cards)

        if p_score > b_score:
            result = 'Player'
        elif b_score > p_score:
            result = 'Banker'
        else:
            result = 'Tie'

        games.append({
            'Player': player_cards,
            'Banker': banker_cards,
            'P_Score': p_score,
            'B_Score': b_score,
            'Result': result
        })
        st.success(f"결과 기록됨: {result}")
    else:
        st.error("카드는 반드시 2장씩 입력해주세요.")

if games:
    st.subheader("게임 기록")
    for i, g in enumerate(games):
        st.write(f"Game {i+1}: {g['Player']} ({g['P_Score']}) vs {g['Banker']} ({g['B_Score']}) → {g['Result']}")

    results = [g['Result'] for g in games]
    count = Counter(results)
    total = len(results)

    p_rate = count['Player'] / total if 'Player' in count else 0
    b_rate = count['Banker'] / total if 'Banker' in count else 0
    t_rate = count['Tie'] / total if 'Tie' in count else 0

    suggestion = max(("Player", p_rate), ("Banker", b_rate), ("Tie", t_rate), key=lambda x: x[1])

    st.subheader("다음 게임 예측")
    st.write(f"예측: **{suggestion[0]}** (확률: {suggestion[1]*100:.1f}%)")
