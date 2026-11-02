import ipywidgets as widgets
import random

from utils.catalog import CATALOG, CATEGORIES
from utils.specs_getter import specs_widget

data_loc = "../data/synthetic/components"

### -------------------- HELPERS -------------------- ###

# PLACEHOLDER IMAGE
# will eventually have cute lil pics for components
# for now, this:
image_placeholder = widgets.Box(
    [widgets.Label('IMAGE PLACEHOLDER')],
    layout=widgets.Layout(
        width='98%',
        height='40%',
        justify_content='center',
        align_items='center',
        border='1px solid #ccc',
    ),
)

# grab card images
def get_card_image(part_id):
    # in the future, will have to make a lookup by part id
    return image_placeholder # TODO: add imaged for parts

### -------------------- CARD MAKER -------------------- ###
def make_card(type, index):
    part = CATALOG[type][index]

    type_label = str(type).upper()
    if type_label == "MOTHERBOARDS": type_label = "MOBO"    # ia m being lazy
    if type_label[-1] == 'S': type_label = type_label[:-1]  # lazy way to get rid of plurals

    name = f"{type_label} - {part['name']}"
    price = part['price_usd']
    specs_layout = specs_widget(type, part)
    image = get_card_image(part['id'])
    
    # CARD HEADER = |name  price|
    header = widgets.HBox(
        [
            widgets.Label(name, style={'font_weight': 'bold'}), 
            widgets.Label(f'${price:,}', style={'text_color': 'green'})
        ], 
        layout=widgets.Layout(width='100%', justify_content='space-between', overflow='hidden')
    )

    add_button = widgets.Button(description='[ build ]', tooltip='Add to build', style={'button_color': 'green'})
    sell_button = widgets.Button(description='[ sell ]', tooltip='Sell this card', style={'button_color': 'red'})
    buttons = widgets.HBox(
        [sell_button, add_button],
        layout=widgets.Layout(width='100%', justify_content='space-between', overflow='hidden'),
    )

    card = widgets.VBox(
        [header, image, specs_layout, buttons],
        layout=widgets.Layout(
            width='350px',
            height='460px',
            padding='6px',
            border='1px solid #777',
            flex='0 0 350px',
            min_width='350px',
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