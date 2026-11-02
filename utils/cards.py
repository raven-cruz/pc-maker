import ipywidgets as widgets
import random

from utils.catalog import CATALOG, CATEGORIES
from utils.specs_getter import specs_widget
from utils.image import part_id_to_widget

data_loc = "../data/synthetic/components"

### -------------------- CARD MAKER -------------------- ###
def make_card(type, index, c_width=350, c_height=460):
    part = CATALOG[type][index]

    type_label = str(type).upper()
    if type_label == "MOTHERBOARDS": type_label = "MOBO"    # ia m being lazy
    if type_label[-1] == 'S': type_label = type_label[:-1]  # lazy way to get rid of plurals

    name = f"{type_label} - {part['name']}"
    price = part['price_usd']
    specs_layout = specs_widget(type, part)
    image = part_id_to_widget(part['id'], c_width, c_height*0.4)
    
    # CARD HEADER = |name  price|
    header = widgets.HBox(
        [
            widgets.Label(name, style={'font_weight': 'bold'}), 
            widgets.Label(f'${price:,}', style={'text_color': 'green'})
        ], 
        layout=widgets.Layout(width='100%', justify_content='space-between', overflow='hidden')
    )

    add_button = widgets.Button(description='[ build ]', tooltip='Add to build', style={'button_color': 'green'})
    scrap_button = widgets.Button(description='[ scrap ]', tooltip='Scrap this card', style={'button_color': 'orange'})
    sell_button = widgets.Button(description='[ sell ]', tooltip='Sell this card', style={'button_color': 'red'})
    buttons = widgets.HBox(
        [sell_button, scrap_button, add_button],
        layout=widgets.Layout(width='100%', justify_content='space-between', overflow='hidden'),
    )

    card = widgets.VBox(
        [header, image, specs_layout, buttons],
        layout=widgets.Layout(
            width=f'{c_width}px',
            height=f'{c_height}px',
            padding='6px',
            border='1px solid #777',
            flex=f'0 0 {c_width}px',
            min_width=f'{c_width}px',
        ),
    )

    card.price_usd = price
    card.component_type = type
    card.part = part

    return card

### randomization
def make_random_card(category=None):
    if not category: category = random.choice(CATEGORIES)
    index = random.randrange(0, len(CATALOG[category])) # maybe a more sophisticated way to do but this'll work
    return make_card(category, index)