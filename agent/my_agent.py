# -*- coding: utf-8 -*-
from agent import Agent
from card import Card
from card import ALL_CARDS
from game import Game
import card
import numpy as np
import random


class MyAgent(Agent):
    '''
    You have to decide which card to play in this round.
    cards_played: cards that has been played this round
    cards_you_have: list of cards in your hand
    heart_broken: heart is broken or not
    info: score information and cards played in previous rounds
    '''
    def worth_points(self, CARD):
        worth_points = 0
        # 如果沒有剩餘的牌 出了一定吃 視為減項且極大
        if not self.memory[CARD.suit]:
            return -100
        else:
            if ((len(self.mycards[CARD.suit]) + len(self.memory[CARD.suit])) >= 11):
                worth_points += 2
            if len(self.memory[CARD.suit]) <= 2 and any(rnum(c) > rnum(CARD)for c in self.memory[CARD.suit]):
                worth_points += 3
            if all(rnum(c) > rnum(CARD) for c in self.memory[CARD.suit]):
                worth_points += 100

            for c in self.memory[CARD.suit]:
                # 如果此牌大於剩餘的牌 不利 視為減項減1
                if rnum(CARD) > rnum(c):
                    worth_points -= 1
                # 如果此牌小於剩餘的牌 有利 視為加項減1
                else:
                    worth_points += 1
        return worth_points

    def memorize(self, cards):
        self.memory = {suit: [Card(suit, number)
                       for number in card._number
                       if Card(suit, number) not in cards]
                       for suit in card._suit}

    def remove_played_cards(self, cards_lists, cards_played):
        for c in cards_played:
            self.memory[c.suit].remove(c)

        for cards_list in cards_lists[::-1]:
            for idx, c in cards_list:
                if c in self.mycards[c.suit]:
                    return
                elif c in self.memory[c.suit]:
                    self.memory[c.suit].remove(c)

    def play(self, cards_you_have, cards_played, heart_broken, info):

        # remember cards
        if len(cards_you_have) == 13:
            self.memorize(cards_you_have)

        # remove cards from memory if a player has played it
        self.remove_played_cards(info.rounds, cards_played)

        self.mycards = {'♠': [card for card in cards_you_have if card.suit == '♠'],
                        '♥': [card for card in cards_you_have if card.suit == '♥'],
                        '♦': [card for card in cards_you_have if card.suit == '♦'],
                        '♣': [card for card in cards_you_have if card.suit == '♣']}

        self.legal_move = Game.get_legal_moves(cards_you_have, cards_played, heart_broken)

        self.mylegalcards = {'♠': [card for card in self.legal_move if card.suit == '♠'],
                             '♥': [card for card in self.legal_move if card.suit == '♥'],
                             '♦': [card for card in self.legal_move if card.suit == '♦'],
                             '♣': [card for card in self.legal_move if card.suit == '♣']}

        for suit in ['♣', '♦', '♠', '♥']:
            if not self.mylegalcards[suit]:
                del self.mylegalcards[suit]
        # self.cards_left = self.memory
        # 定義在memorize
        '''這裡還有問題 就是後來發現card_played只有那四張'''
        '''self.cards_have_played'''
        # LEGAL MOVE

        # good move
        self.good_move = self.get_good_moves(cards_you_have, cards_played, heart_broken)
        # 出牌次序(0,1,2,3)
        # 各花總價數
        self.mygoodcards = {'♠': [card for card in self.good_move if card.suit == '♠'],
                            '♥': [card for card in self.good_move if card.suit == '♥'],
                            '♦': [card for card in self.good_move if card.suit == '♦'],
                            '♣': [card for card in self.good_move if card.suit == '♣']}

        for suit in ['♣', '♦', '♠', '♥']:
            if not self.mygoodcards[suit]:
                del self.mygoodcards[suit]

        self.mycards_worth_point = {'♠': sum(map(self.worth_points, self.mycards['♠'])),
                                    '♥': sum(map(self.worth_points, self.mycards['♥'])),
                                    '♦': sum(map(self.worth_points, self.mycards['♦'])),
                                    '♣': sum(map(self.worth_points, self.mycards['♣']))
                                    }
        _suit = {'♣': 0, '♦': 1, '♠': 2, '♥': 3}
        # 先按照出牌次序來分類出牌策略
        if len(cards_played) == 0:
            if any(len(cards) <= 2 and len(self.memory[suit]) >= 3 for suit, cards in self.mylegalcards.items()):
                if (Card('♠', 12) in self.memory['♠']) or (Card('♠', 12) in cards_you_have):
                    # 看手上有沒有黑桃QKA
                    if (((Card('♠', 1) or Card('♠', 13)) or Card('♠', 12)) in cards_you_have):
                        cards_not_spade = self.mylegalcards.copy()
                        if '♠' in cards_not_spade.keys():
                            del cards_not_spade['♠']
                        cards_wp = {}
                        ok_suits = []
                        if any(cards_not_spade.values()):
                            for suit in cards_not_spade.keys():
                                if len(cards_not_spade[suit]) == min(map(len, cards_not_spade.values())):
                                    ok_suits.append(_suit[suit])
                            for suit in cards_not_spade.keys():
                                if _suit[suit] == max(ok_suits):
                                    for c in cards_not_spade[suit]:
                                        highestwp_cards = [c for c in cards_not_spade[suit]
                                                           if self.worth_points(c) == max(map(self.worth_points, cards_not_spade[suit]))]
                                    return random.choice([c for c in highestwp_cards if rnum(c) == max(map(rnum, highestwp_cards))])
                        else:
                            cards_lt_Q = [c for c in self.legal_move if rnum(c) < 12]
                            if cards_lt_Q:
                                for c in cards_lt_Q:
                                    cards_wp[c] = self.worth_points(c)
                                highestwp_cards = [c for c in cards_lt_Q if cards_wp[c] == max(cards_wp.values())]
                                return random.choice([c for c in highestwp_cards if rnum(c) == max(map(rnum, highestwp_cards))])
                            else:
                                for c in self.legal_move:
                                    cards_wp[c] = self.worth_points(c)
                                highestwp_cards = [c for c in self.legal_move if cards_wp[c] == max(cards_wp.values())]
                                return random.choice([c for c in highestwp_cards if rnum(c) == max(map(rnum, highestwp_cards))])

                    else:
                        ok_suits = []
                        for suit in self.mylegalcards.keys():
                            if len(self.mylegalcards[suit]) == min(map(len, self.mylegalcards.values())):
                                ok_suits.append(_suit[suit])
                        for suit in self.mylegalcards.keys():
                            if _suit[suit] == max(ok_suits):
                                for c in self.mylegalcards[suit]:
                                    highestwp_cards = [c for c in self.mylegalcards[suit]
                                                       if self.worth_points(c) == max(map(self.worth_points, self.mylegalcards[suit]))]
                                return random.choice([c for c in highestwp_cards if rnum(c) == max(map(rnum, highestwp_cards))])
                else:
                    ok_suits = []
                    for suit in self.mylegalcards.keys():
                        if len(self.mylegalcards[suit]) == min(map(len, self.mylegalcards.values())):
                            ok_suits.append(_suit[suit])
                    for suit in self.mylegalcards.keys():
                        if _suit[suit] == max(ok_suits):
                            for c in self.mylegalcards[suit]:
                                highestwp_cards = [c for c in self.mylegalcards[suit]
                                                   if self.worth_points(c) == max(map(self.worth_points, self.mylegalcards[suit]))]
                            return random.choice([c for c in highestwp_cards if rnum(c) == max(map(rnum, highestwp_cards))])

            # 先判斷黑陶Q出了沒 沒出 有出
            else:
                if (Card('♠', 12) in self.memory['♠']) or (Card('♠', 12) in cards_you_have):
                    # 看手上有沒有黑桃QKA
                    if (((Card('♠', 1) or Card('♠', 13)) or Card('♠', 12)) in cards_you_have):

                        cards_not_spade = [c for c in self.legal_move if c.suit != '♠']
                        cards_wp = {}
                        if cards_not_spade:
                            wahaha = []
                            for c in cards_not_spade:
                                cards_wp[c] = self.worth_points(c)
                            highestwp_cards = [(c, c.suit)for c in cards_not_spade if cards_wp[c] == max(cards_wp.values())]
                            for cards, suit in highestwp_cards:
                                if len(self.mycards[suit]) == min(map(len, [self.mycards[suit] for _, suit in highestwp_cards])):
                                    wahaha.append(cards)
                            return random.choice([c for c in wahaha if rnum(c) == max(map(rnum, wahaha))])
                        else:
                            cards_lt_Q = [c for c in self.legal_move if rnum(c) < 12]
                            if cards_lt_Q:
                                for c in cards_lt_Q:
                                    cards_wp[c] = self.worth_points(c)
                                highestwp_cards = [c for c in cards_lt_Q if cards_wp[c] == max(cards_wp.values())]
                                return random.choice([c for c in highestwp_cards if rnum(c) == max(map(rnum, highestwp_cards))])
                            else:
                                for c in self.legal_move:
                                    cards_wp[c] = self.worth_points(c)
                                highestwp_cards = [c for c in self.legal_move if cards_wp[c] == max(cards_wp.values())]
                                return random.choice([c for c in highestwp_cards if rnum(c) == max(map(rnum, highestwp_cards))])

                    else:
                        cards_wp ={}
                        wahaha = []
                        for c in self.legal_move:
                            cards_wp[c] = self.worth_points(c)
                        highestwp_cards = [(c, c.suit)for c in self.legal_move if cards_wp[c] == max(cards_wp.values())]
                        for cards, suit in highestwp_cards:
                            if len(self.mycards[suit]) == min(map(len, [self.mycards[suit] for _, suit in highestwp_cards])):
                                wahaha.append(cards)
                        return random.choice([c for c in wahaha if rnum(c) == max(map(rnum, wahaha))])
                else:
                    cards_wp = {}
                    wahaha = []
                    for c in self.legal_move:
                        cards_wp[c] = self.worth_points(c)
                    highestwp_cards = [(c, c.suit)for c in self.legal_move if cards_wp[c] == max(cards_wp.values())]
                    for cards, suit in highestwp_cards:
                        if len(self.mycards[suit]) == min(map(len, [self.mycards[suit] for _, suit in highestwp_cards])):
                            wahaha.append(cards)
                    return random.choice([c for c in wahaha if rnum(c) == max(map(rnum, wahaha))])

        elif len(cards_played) == 1 or 2:
            max_num = max([rnum(c) for c in cards_played if c.suit == cards_played[0].suit])
            # 跟花:打比前面數字小的最大牌 不然打大於的最小牌
            if any(c.suit == cards_played[0].suit for c in self.good_move):
                hand_smaller_to_max = [rnum(c) for c in self.good_move if rnum(c) < max_num]
                hand_bigger_to_max = [rnum(c) for c in self.good_move if rnum(c) > max_num]
                if ((len(self.mycards[cards_played[0].suit]) + len(self.memory[cards_played[0].suit])) >= 11) and (cards_played[0].suit != '♠'):
                    max_good_move_num = max([rnum(c) for c in self.good_move])
                    for c in self.good_move:
                        if rnum(c) == max_good_move_num:
                            return c
                elif hand_smaller_to_max:
                    for c in self.good_move:
                        if rnum(c) == max(hand_smaller_to_max):
                            return c
                else:
                    for c in self.good_move:
                        if rnum(c) == min(hand_bigger_to_max):
                            return c
            # 缺門 '♠',12 >'♠',1> '♠',13> '♥',1 13 12 11>最大牌
            else:
                if Card('♠', 12) in self.good_move:
                    return Card('♠', 12)
                elif Card('♠', 12) in self.memory['♠'] and (Card('♠', 1) in self.good_move or Card('♠', 13) in self.good_move):
                    if Card('♠', 1) in self.good_move:
                        return Card('♠', 1)
                    elif Card('♠', 13) in self.good_move:
                        return Card('♠', 13)
                elif Card('♥', 1) in self.good_move:
                    return Card('♥', 1)
                elif Card('♥', 13) in self.good_move:
                    return Card('♥', 13)
                elif Card('♥', 12) in self.good_move:
                    return Card('♥', 12)
                elif Card('♥', 11) in self.good_move:
                    return Card('♥', 11)
                elif any(len(cards) <= 2 for cards in self.mylegalcards.values()):
                    ok_suits = []
                    for suit in self.mygoodcards.keys():
                        if len(self.mygoodcards[suit]) == min(map(len, self.mygoodcards.values())):
                            ok_suits.append(_suit[suit])
                    for suit in self.mygoodcards.keys():
                        if _suit[suit] == max(ok_suits):
                            return random.choice([c for c in self.mygoodcards[suit] if rnum(c) == max(map(rnum, self.mygoodcards[suit]))])
                else:
                    biggest_num_cards = [c for c in self.good_move if rnum(c) == max(map(rnum, self.good_move))]
                    if any(c.suit == '♥' for c in biggest_num_cards):
                        for i in filter(lambda c: c.suit == '♥', biggest_num_cards):
                            return i
                    if any(c.suit == '♠' for c in biggest_num_cards):
                        for i in filter(lambda c: c.suit == '♠', biggest_num_cards):
                            return i
                    if any(c.suit == '♦' for c in biggest_num_cards):
                        for i in filter(lambda c: c.suit == '♦', biggest_num_cards):
                            return i
                    if any(c.suit == '♣' for c in biggest_num_cards):
                        for i in filter(lambda c: c.suit == '♣', biggest_num_cards):
                            return i

        elif len(cards_played) == 3:
            # 如果可以清♠12且不吃點(in good move)就先清
            if Card('♠', 12) in self.good_move:
                return Card('♠', 12)
            # 如果♠12還沒出來就先清♠1,♠13
            elif ((Card('♠', 12) in self.memory) or (Card('♠', 12) in cards_you_have)) and ((Card('♠', 1) or Card('♠', 13)) in self.good_move):
                if Card('♠', 1) in self.good_move:
                    return Card('♠', 1)
                return Card('♠', 13)
            # 如果剩其他牌 清數字大的 有一樣數字就清♣ < ♦  < ♠ < ♥
            elif any(len(cards) <= 2 for cards in self.mylegalcards.values()):
                ok_suits = []
                for suit in self.mygoodcards.keys():
                    if len(self.mygoodcards[suit]) == min(map(len, self.self.mygoodcards.values())):
                        ok_suits.append(_suit[suit])
                for suit in self.self.mygoodcards.keys():
                    if _suit[suit] == max(ok_suits):
                        return random.choice([c for c in self.self.mygoodcards[suit] if rnum(c) == max(map(rnum, self.mygoodcards[suit]))])
            else:
                biggest_num_cards = [c for c in self.good_move if rnum(c) == max(map(rnum, self.good_move))]
                if any(c.suit == '♥' for c in biggest_num_cards):
                    for i in filter(lambda c: c.suit == '♥', biggest_num_cards):
                        return i
                elif any(c.suit == '♠' for c in biggest_num_cards):
                    for i in filter(lambda c: c.suit == '♠', biggest_num_cards):
                        return i
                elif any(c.suit == '♦' for c in biggest_num_cards):
                    for i in filter(lambda c: c.suit == '♦', biggest_num_cards):
                        return i
                elif any(c.suit == '♣' for c in biggest_num_cards):
                    for i in filter(lambda c: c.suit == '♣', biggest_num_cards):
                        return i

    # 計牌程式
    '''def memorize(self, cards):
        self.memory = {suit: [Card(suit, number)
                       for number in card._number
                       if Card(suit, number) not in cards]
                       for suit in card._suit}'''

    def remove_cards(self, card_lists, cards_played, cards_you_have):
        if len(cards_you_have) == 13:
            for c in cards_you_have:
                self.memory[c.suit].remove(c)

        for c in cards_played:
            self.memory[c.suit].remove(c)

        for c_list in card_lists[::-1]:
            for idx, c in c_list[::-1]:
                if c in self.mycards[c.suit]:
                    return
                self.memory[c.suit].remove(c)

    # 新名詞:價數 (簡單計算此牌被吃走的難易程度) 待補:場上剩餘的牌

    def get_good_moves(self, cards_you_have, cards_played, heart_broken):
        if not cards_played:
            return self.legal_move
        else:
            legal_move_results = {}
            cards_same_suit_number = [rnum(c) for c in cards_played if c.suit == cards_played[0].suit]
            max_num = max(cards_same_suit_number)
            # try every legal card
            for c in self.legal_move:
                # see whether it would eat and remember it
                total_points = sum(map(Card.get_point, cards_played+[c]))
                if c.suit == cards_played[0].suit and rnum(c) > max_num:
                    legal_move_results[c] = total_points
                else:
                    legal_move_results[c] = 0
            return [c for c in self.legal_move if legal_move_results[c] == min(legal_move_results.values())]

    def pass_cards(self, cards):
        card_pass = list()

        spades = sorted([card for card in cards if card.suit == '♠'], reverse=True)
        hearts = sorted([card for card in cards if card.suit == '♥'], reverse=True)
        diamonds = sorted([card for card in cards if card.suit == '♦'], reverse=True)
        clubs = sorted([card for card in cards if card.suit == '♣'], reverse=True)

        # 1
        if len(spades) >= 5 and '♠12' in cards:
            pass
        else:
            if len(spades) != 0:
                for c in spades:
                    if c > Card('♠', 11):
                        card_pass.append(c)

        if len(card_pass) >= 3:
            return card_pass[:3]
        # 2
        if len(hearts) >= 7 and '♥1' in cards:
            hearts_num = list(int(card._number[c.number]) for c in hearts[:4])
            if np.mean(hearts_num) >= 9:
                shooting_moon = True
                # the way we pass cards under this situation is still unknown
        else:
            # 3
            hearts_ad = sorted([c for c in hearts if c > Card('♥', 10)])
            diamonds_ad = sorted([c for c in hearts if c > Card('♦', 10)])
            clubs_ad = sorted([c for c in hearts if c > Card('♣', 10)])
            if hearts_ad:
                card_pass.append(hearts.pop(0))
                hearts_ad.remove(hearts_ad[-1])
            if len(card_pass) >= 3:
                return card_pass[:3]
            # 4
            while(len(card_pass) < 3):
                if len(hearts_ad) >= len(diamonds_ad) and len(hearts_ad) >= (len(clubs_ad) - 1) and hearts_ad and hearts:
                    card_pass.append(hearts.pop(0))
                    hearts_ad.remove(hearts_ad[-1])
                elif len(diamonds_ad) >= (len(clubs_ad) - 1) and diamonds_ad and diamonds:
                    card_pass.append(diamonds.pop(0))
                    diamonds_ad.remove(diamonds_ad[-1])
                elif clubs_ad and clubs:
                    card_pass.append(clubs.pop(0))
                    clubs_ad.remove(clubs_ad[-1])
                else:
                    all_max = {'hearts': int(hearts[0].number) if hearts else 0, 'diamonds': int(diamonds[0].number) if diamonds else 0, 'clubs': int(clubs[0].number) if clubs else 0}
                    if all_max['hearts'] == max(all_max.values()):
                        card_pass.append(hearts.pop(0))
                    elif all_max['diamonds'] == max(all_max.values()):
                        card_pass.append(diamonds.pop(0))
                    else:
                        card_pass.append(clubs.pop(0))
            return card_pass[:3]


# real num 把卡片數字轉換成a=100 13=13 12=12....

def rnum(c):
    return card._number[c.number]


# 同理
def rsuit(c):
    return card._suit[c.suit]
