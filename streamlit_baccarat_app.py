import streamlit as st
from collections import Counter

def card_value(card):
    if card in ['10', 'J', 'Q', 'K']:
        return 0
    elif card == 'A':
        return 1
    else:
        return int(card)

def hand_score(hand):
    return sum([card_value(c) for c in hand]) % 10

def draw_third_card(player_hand, banker_hand):
    p_score = hand_score(player_hand)
    b_score = hand_score(banker_hand)

    # 내추럴
    if p_score >= 8 or b_score >= 8:
        return player_hand, banker_hand

    third_player = None
    if p_score <= 5:
        third_player = st.text_input("플레이어 3번째 카드 입력 (없으면 엔터)", key="player_3rd").upper()
        if third_player:
            player_hand.append(third_player)

    # 뱅커의 행동은 복잡함
    b_score = hand_score(banker_hand)
    p_third_val = card_value(third_player) if third_player else None

    if third_player is None:
        if b_score <= 5:
            third_banker = st.text_input("뱅커 3번째 카드 입력 (없으면 엔터)", key="banker_3rd").upper()
            if third_banker:
                banker_hand.append(third_banker)
    else:
        # 복잡한 룰 적용
        if b_score <= 2:
            banker_hand.append(st.text_input("뱅커 3번째 카드 입력", key="banker_3rd_force").upper())
        elif b_score == 3 and p_third_val != 8:
            banker_hand.append(st.text_input("뱅커 3번째 카드 입력", key="banker_3rd_3").upper())
        elif b_score == 4 and p_third_val in range(2, 8):
            banker_hand.append(st.text_input("뱅커 3번째 카드 입력", key="banker_3rd_4").upper())
        elif b_score == 5 and p_third_val in range(4, 8):
            banker_hand.append(st.text_input("뱅커 3번째 카드 입력", key="banker_3rd_5").upper())
        elif b_score == 6 and p_third_val in range(6, 8):
            banker_hand.append(st.text_input("뱅커 3번째 카드 입력", key="banker_3rd_6").upper())

    return player_hand, banker_hand

if 'games' not in st.session_state:
    st.session_state.games = []

st.title("진짜 룰 기반 바카라 예측기")
st.write("플레이어/뱅커 카드 입력 후 실제 룰에 따라 3번째 카드 입력창이 자동 등장합니다.")

player_input = st.text_input("플레이어 카드 2장 (예: 9,K)", key="p_input")
banker_input = st.text_input("뱅커 카드 2장 (예: 3,4)", key="b_input")

if st.button("게임 기록 추가"):
    player_cards = player_input.upper().split(',')
    banker_cards = banker_input.upper().split(',')

    if len(player_cards) == 2 and len(banker_cards) == 2:
        player_cards, banker_cards = draw_third_card(player_cards, banker_cards)
        p_score = hand_score(player_cards)
        b_score = hand_score(banker_cards)

        if p_score > b_score:
            result = 'Player'
        elif b_score > p_score:
            result = 'Banker'
        else:
            result = 'Tie'

        st.session_state.games.append({
            'Player': player_cards,
            'Banker': banker_cards,
            'P_Score': p_score,
            'B_Score': b_score,
            'Result': result
        })
        st.success(f"결과 기록됨: {result}")
    else:
        st.error("카드는 반드시 2장씩 입력해주세요.")

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
