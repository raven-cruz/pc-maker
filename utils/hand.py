import ipywidgets as widgets
import random

from utils.cards import make_random_card

### -------------------- DEAL HANDS -------------------- ###
def deal_hand(hand_size=4):
    return [make_random_card() for _ in range(hand_size)]

def hand_to_widget(hand):
    original_hand_size = len(hand)
    bank_balance = 0
    can_sell = True
    bank_label = widgets.Label(f'Bank: ${bank_balance:,}')
    hand_widget = widgets.Box(
        hand,
        layout=widgets.Layout(
            display='flex',
            flex_flow='row nowrap',
            overflow='auto',
            width='100%',
        ),
    )

    def update_build_buttons():
        nonlocal can_sell
        for card in hand:
            build_button = card.children[-1].children[1]
            can_afford = bank_balance >= card.price_usd
            build_button.style.button_color = 'green' if can_afford else 'gray'
            build_button.disabled = not can_afford

            # only let sell once per hand
            sell_button = card.children[-1].children[0]
            sell_button.style.button_color = 'red' if can_sell else 'gray'
            sell_button.disabled = not can_sell


    def connect_card_buttons(card):
        sell_button, build_button = card.children[-1].children

        # removes card from hand AND widget
        def remove_from_hand(button):
            nonlocal bank_balance
            nonlocal can_sell
            if card in hand:
                if button is sell_button:
                    bank_balance += card.price_usd
                    can_sell = False # one sell per hand
                if button is build_button:
                    if bank_balance < card.price_usd:
                        return
                    bank_balance -= card.price_usd
                bank_label.value = f'Bank: ${bank_balance:,}'
                hand.remove(card)
                hand_widget.children = tuple(hand)
                update_build_buttons()

        sell_button.on_click(remove_from_hand)
        build_button.on_click(remove_from_hand)

    for card in hand: connect_card_buttons(card)
    update_build_buttons()

    # draw replacements for cards removed from hand
    def draw_replacements(button):
        nonlocal can_sell
        while len(hand) < original_hand_size:
            card = make_random_card()
            connect_card_buttons(card)
            hand.append(card)

        hand_widget.children = tuple(hand)
        can_sell = True
        update_build_buttons()

    draw_button = widgets.Button(description='Draw replacements', button_style='primary')
    draw_button.on_click(draw_replacements)

    return widgets.VBox([bank_label, hand_widget, draw_button])