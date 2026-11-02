from PIL import Image
import io
import requests
from IPython.display import display
import json
import ipywidgets as widgets
from pathlib import Path

def part_id_to_widget(part_id, widget_width=None, widget_height=None):
    # making sure width and height are both defined
    if widget_width and not widget_height: widget_height = widget_width     # treat as radius
    elif widget_height and not widget_width: widget_width = widget_height
    elif not widget_width and not widget_height:
        widget_width = widget_height = 100  # default

    mappings_path = Path(__file__).parent.parent / 'data/synthetic/image_lookups/image_mappings.json'
    with open(mappings_path, 'r') as file:
        image_mappings = json.load(file)

    storage_ffs = {
        'M2': 'strorage_M2.png',
        'SATA': 'storage_SATA.png',
    }
    component_type = None
    quadrant = None
    image_filename = None
    for part_type, parts in image_mappings.items(): # TODO: could be simpler as a df, just doing this quick n lazy for now
        # since there are two different storage files, gotta make sure we're finding the right image url
        if part_type == 'storage':
            for storage_type, storage_parts in parts.items():
                if part_id in storage_parts:
                    component_type = part_type
                    quadrant = storage_parts[part_id]
                    image_filename = storage_ffs[storage_type]
                    break
        elif part_id in parts:
            component_type = part_type
            quadrant = parts[part_id]
            image_filename = f'{component_type}.png'
            break
        if component_type:
            break

    if image_filename is None:
        raise KeyError(f'No image mapping found for part ID: {part_id}')
    if quadrant not in ('TL', 'TR', 'BL', 'BR'):
        raise ValueError(f'Invalid image quadrant for {part_id}: {quadrant}')

    image_url = f'https://raw.githubusercontent.com/raven-cruz/component_icons/refs/heads/main/{image_filename}'
    response = requests.get(image_url)
    response.raise_for_status()
    image = Image.open(io.BytesIO(response.content))

    # crop image so it just shows the correct quadrant (using image_mappings.json)
    middle_x = image.width // 2
    middle_y = image.height // 2
    quadrants = {
        'TL': (0, 0, middle_x, middle_y),
        'TR': (middle_x, 0, image.width, middle_y),
        'BL': (0, middle_y, middle_x, image.height),
        'BR': (middle_x, middle_y, image.width, image.height),
    }

    # make fit in dimensions
    cropped = image.crop(quadrants[quadrant])
    cropped.thumbnail((widget_width, widget_height), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    cropped.save(buffer, format="PNG")

    image_widget = widgets.Image(
        value=buffer.getvalue(),
        format="png",
        width=cropped.width,
        height=cropped.height,
    )
    return image_widget