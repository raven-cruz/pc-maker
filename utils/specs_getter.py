import ipywidgets as widgets

### component-specific specs layouts
# - each function builds a widget containing the specs for one type of component 
# - since each component type has different specs, keeping these functions separate makes my life easier to throw component specs into the main card layout

def get_case_specs(case):
    motherboard_sizes = ', '.join(case['motherboard_form_factors'])
    psu_sizes = ', '.join(case['supported_psu_form_factors'])
    radiator_sizes = ', '.join(f'{size} mm' for size in case['radiator_sizes_mm']) or 'None'
    drive_bays = f"2.5 in: {case['sata_bays_2_5']} | 3.5 in: {case['sata_bays_3_5']}"

    # TODO: might be better to make a normalizer function for this, but not enough data rn to justify 
    usb_header_names = {
        'USB3_19PIN': 'USB 3.0 (19-pin)',
        'USBC_20PIN': 'USB-C (20-pin)',
        'USB2_9PIN': 'USB 2.0 (9-pin)',
    }
    front_usb_headers = ', '.join(usb_header_names[header] for header in case['front_usb_headers']) or 'None'

    spec_rows = [
        ('Motherboards:', motherboard_sizes),
        ('PSU:', psu_sizes),
        ('GPU max length:', f"{case['gpu_max_length_mm']} mm"),
        ('CPU cooler max height:', f"{case['cpu_cooler_max_height_mm']} mm"),
        ('Radiators:', radiator_sizes),
        ('Drive bays:', drive_bays),
        ('Front USB:', front_usb_headers),
    ]

    return spec_rows

def get_cooler_specs(cooler):
    supported_mounts = ', '.join(cooler['supported_mounts'])
    fan_connector = cooler['fan_connector'].replace('_', ' ').replace('PIN', '-pin')
    rgb_connector = cooler['rgb_connector']
    if rgb_connector:
        rgb_connector = rgb_connector.replace('_', ' ').replace('PIN', '-pin')
    else:
        rgb_connector = 'None'

    spec_rows = [
        ('Type:', cooler['type'].capitalize()),
        ('Supported mounts:', supported_mounts),
        ('Cooling capacity:', f"{cooler['cooling_capacity_w']} W"),
    ]

    if 'height_mm' in cooler:
        spec_rows.append(('Height:', f"{cooler['height_mm']} mm"))
    if 'radiator_mm' in cooler:
        spec_rows.append(('Radiator:', f"{cooler['radiator_mm']} mm"))

    spec_rows.extend([
        ('Fan connector:', fan_connector),
        ('RGB connector:', rgb_connector),
    ])

    return spec_rows

def get_cpu_specs(cpu):
    integrated_graphics = 'Yes' if cpu['integrated_graphics'] else 'No'

    spec_rows = [
        ('Socket:', cpu['socket']),
        ('TDP:', f"{cpu['tdp_w']} W"),
        ('Integrated graphics:', integrated_graphics),
    ]

    return spec_rows

def get_fan_specs(fans):
    fan_connector = fans['fan_connector'].replace('_', ' ').replace('PIN', '-pin')
    rgb_connector = fans['rgb_connector']
    if rgb_connector:
        rgb_connector = rgb_connector.replace('_', ' ').replace('PIN', '-pin')
    else:
        rgb_connector = 'None'

    spec_rows = [
        ('Size:', f"{fans['diameter_mm']} mm"),
        ('Fan connector:', fan_connector),
        ('RGB connector:', rgb_connector),
        ('Power draw:', f"{fans['power_w']} W"),
    ]

    return spec_rows

def get_gpu_specs(gpu):
    slot = gpu['pcie_slot'].replace('PCIE_X', 'x')
    power_connectors = [
        f"{count} x {connector.replace('_', ' ').replace('PCIE ', 'PCIe ').replace('PIN', '-pin')}"
        for connector, count in gpu['power_connectors'].items()
    ]
    power_connectors = ', '.join(power_connectors) or 'None'

    spec_rows = [
        ('PCIe slot:', f"{slot} (Gen {gpu['pcie_generation']})"),
        ('Length:', f"{gpu['length_mm']} mm"),
        ('Thickness:', f"{gpu['thickness_slots']} slots"),
        ('TDP:', f"{gpu['tdp_w']} W"),
        ('Power connectors:', power_connectors),
    ]

    return spec_rows

def get_lighting_specs(lighting):
    rgb_connector = lighting['rgb_connector'].replace('_', ' ').replace('PIN', '-pin')

    spec_rows = [
        ('RGB connector:', rgb_connector),
        ('Power draw:', f"{lighting['power_w']} W"),
    ]

    return spec_rows

def get_mobo_specs(mobo):
    connectors = mobo['connector_layout']['connectors']
    pcie_slots = [c['interface'].replace('PCIE_X', 'x') for c in connectors if c['kind'] == 'pcie_slot']
    usb_headers = [c['interface'] for c in connectors if c['kind'] == 'usb_header']
    rgb_headers = [c['interface'] for c in connectors if c['kind'] == 'rgb_header']
    m2_slots = [c for c in connectors if c['kind'] == 'm2_slot']
    sata_ports = [c for c in connectors if c['kind'] == 'sata_port']
    fan_headers = [c for c in connectors if c['kind'] == 'fan_header']
    power_connectors = [
        c['interface'].replace('_', ' ').replace('PIN', '-pin') 
        for c in connectors if c['kind'] == 'power_header'
    ]

    spec_rows = [
        ('Chipset:', mobo['chipset']),
        ('Socket:', mobo['cpu_socket']),
        ('Size:', mobo['form_factor']),
        ('Board:', f"{mobo['dimensions_mm']['width']} x {mobo['dimensions_mm']['height']} mm"),
        ('Memory:', f"{mobo['memory']['type']} {mobo['memory']['form_factor']}"),
        ('Slots:', str(mobo['memory']['slots'])),
        ('Max memory:', f"{mobo['memory']['max_capacity_gb']} GB"),
        ('PCIe:', ', '.join(pcie_slots)),
        ('M.2 slots:', str(len(m2_slots))),
        ('SATA ports:', str(len(sata_ports))),
        ('Headers:', f"fan {len(fan_headers)} | USB {len(usb_headers)} | RGB {len(rgb_headers)}"),
        ('Power:', ' + '.join(power_connectors)),
    ]

    return spec_rows

def get_psu_specs(psu):
    connector_names = {
        'ATX_24PIN': 'ATX 24-pin',
        'EPS_8PIN': 'EPS 8-pin',
        'PCIE_8PIN': 'PCIe 8-pin',
        'PCIE_16PIN': 'PCIe 16-pin',
        'SATA_POWER': 'SATA power',
    }

    spec_rows = [
        ('Form factor:', psu['form_factor']),
        ('Power output:', f"{psu['watts']} W"),
    ]
    spec_rows.extend(
        (f"{connector_names[connector]}:", str(count)) for connector, count in psu['connectors'].items()
    )

    return spec_rows

def get_ram_specs(ram):
    total_capacity = ram['modules'] * ram['gb_per_module']

    spec_rows = [
        ('Memory type:', ram['type']),
        ('Form factor:', ram['form_factor']),
        ('Capacity:', f"{total_capacity} GB ({ram['modules']} x {ram['gb_per_module']} GB)"),
        ('Modules:', str(ram['modules'])),
        ('Pins:', str(ram['pins'])),
    ]

    return spec_rows

def get_storage_specs(storage):
    form_factor = storage['form_factor']
    if form_factor == 'M2': form_factor = 'M.2'
    elif form_factor.startswith('SATA_'):
        form_factor = form_factor.replace('SATA_', 'SATA ')

    spec_rows = [
        ('Form factor:', form_factor),
        ('Protocol:', storage['protocol']),
    ]

    if 'key' in storage:
        spec_rows.append(('Key:', storage['key']))
    if 'size' in storage:
        spec_rows.append(('M.2 size:', f"{storage['size']} mm"))
    if 'pcie_generation' in storage:
        spec_rows.append(('PCIe generation:', str(storage['pcie_generation'])))

    spec_rows.append(('Power draw:', f"{storage['power_w']} W"))

    return spec_rows

### grab specs by compoonent type
SPEC_GETTERS = {
    'cases': get_case_specs,
    'coolers': get_cooler_specs,
    'cpus': get_cpu_specs,
    'fans': get_fan_specs,
    'gpus': get_gpu_specs,
    'lighting': get_lighting_specs,
    'motherboards': get_mobo_specs,
    'psus': get_psu_specs,
    'ram': get_ram_specs,
    'storage': get_storage_specs,
}

### make the specs widget with the given rows (list of tuples)
def specs_widget(part_type, part):
    spec_rows = SPEC_GETTERS[part_type](part)

    specs_content = widgets.VBox([
        # label: value
        widgets.HBox([
            widgets.Label(label, style={'font_weight': 'bold'},layout=widgets.Layout(flex='0 0 auto')),
            widgets.Label(value, layout=widgets.Layout(flex='0 0 auto', margin='0 0 0 2%')),
        ], layout=widgets.Layout(width='max-content', min_width='100%', flex='0 0 auto', margin='0 0 0 0'))
        for label, value in spec_rows
    ], layout=widgets.Layout(width='max-content', min_width='100%', flex='0 0 auto'))

    return widgets.Box(
        [specs_content],
        layout=widgets.Layout(width='99%', height='50%', display='block'),
    )
