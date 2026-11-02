import ipywidgets as widgets


def show_build():
    return widgets.Box(
        [],
        layout=widgets.Layout(
            display='flex',
            flex_flow='row nowrap',
            overflow='auto',
            width='100%',
        ),
    )


def _connectors(motherboard, kind):
    return [
        connector
        for connector in motherboard['connector_layout']['connectors']
        if connector['kind'] == kind
    ]


def check_build(cards):
    parts = {}
    for card in cards:
        parts.setdefault(card.component_type, []).append(card.part)

    issues = []
    cases = parts.get('cases', [])
    coolers = parts.get('coolers', [])
    cpus = parts.get('cpus', [])
    fans = parts.get('fans', [])
    gpus = parts.get('gpus', [])
    lighting = parts.get('lighting', [])
    motherboards = parts.get('motherboards', [])
    psus = parts.get('psus', [])
    ram_parts = parts.get('ram', [])
    storage_parts = parts.get('storage', [])

    for case in cases:
        for motherboard in motherboards:
            if motherboard['form_factor'] not in case['motherboard_form_factors']:
                issues.append(
                    f"{motherboard['brand']} {motherboard['model']} motherboard form factor "
                    f"({motherboard['form_factor']}) is not supported by the {case['name']} case."
                )
        for gpu in gpus:
            if gpu['length_mm'] > case['gpu_max_length_mm']:
                issues.append(
                    f"{gpu['name']} GPU length ({gpu['length_mm']} mm) exceeds the "
                    f"{case['name']} case limit ({case['gpu_max_length_mm']} mm)."
                )
        for cooler in coolers:
            if cooler['type'] == 'air' and cooler['height_mm'] > case['cpu_cooler_max_height_mm']:
                issues.append(
                    f"{cooler['name']} cooler height ({cooler['height_mm']} mm) exceeds the "
                    f"{case['name']} case limit ({case['cpu_cooler_max_height_mm']} mm)."
                )
            if cooler['type'] == 'liquid' and cooler['radiator_mm'] not in case['radiator_sizes_mm']:
                issues.append(
                    f"{cooler['name']} radiator size ({cooler['radiator_mm']} mm) is not "
                    f"supported by the {case['name']} case."
                )
        for psu in psus:
            if psu['form_factor'] not in case['supported_psu_form_factors']:
                issues.append(
                    f"{psu['name']} PSU form factor ({psu['form_factor']}) is not supported "
                    f"by the {case['name']} case."
                )
        for storage in storage_parts:
            if storage['form_factor'] == 'SATA_2.5' and case['sata_bays_2_5'] < 1:
                issues.append(f"{case['name']} case does not support 2.5-inch SATA drives.")
            if storage['form_factor'] == 'SATA_3.5' and case['sata_bays_3_5'] < 1:
                issues.append(f"{case['name']} case does not support 3.5-inch SATA drives.")

    for cooler in coolers:
        for cpu in cpus:
            if cooler['cooling_capacity_w'] < cpu['tdp_w']:
                issues.append(
                    f"{cooler['name']} cooling capacity ({cooler['cooling_capacity_w']} W) is "
                    f"below the {cpu['name']} CPU TDP ({cpu['tdp_w']} W)."
                )

    for motherboard in motherboards:
        motherboard_name = f"{motherboard['brand']} {motherboard['model']}"
        connectors = motherboard['connector_layout']['connectors']
        fan_headers = [c['interface'] for c in connectors if c['kind'] == 'fan_header']
        pcie_slots = [c['interface'] for c in connectors if c['kind'] == 'pcie_slot']

        for cpu in cpus:
            if cpu['socket'] != motherboard['cpu_socket']:
                issues.append(
                    f"{cpu['name']} CPU socket ({cpu['socket']}) is not supported by the "
                    f"{motherboard_name} motherboard ({motherboard['cpu_socket']})."
                )
        for cooler in coolers:
            if motherboard['cooler_mount'] not in cooler['supported_mounts']:
                issues.append(
                    f"{cooler['name']} does not support the {motherboard['cooler_mount']} "
                    f"cooler mount on the {motherboard_name} motherboard."
                )
            if cooler['fan_connector'] not in fan_headers:
                issues.append(
                    f"{cooler['name']} fan connector ({cooler['fan_connector']}) is not "
                    f"supported by the {motherboard_name} motherboard."
                )
        for fan in fans:
            if fan['fan_connector'] not in fan_headers:
                issues.append(
                    f"{fan['name']} fan connector ({fan['fan_connector']}) is not supported "
                    f"by the {motherboard_name} motherboard."
                )
        for gpu in gpus:
            if gpu['pcie_slot'] not in pcie_slots:
                issues.append(
                    f"{gpu['name']} GPU slot ({gpu['pcie_slot']}) is not supported by the "
                    f"{motherboard_name} motherboard."
                )
        for ram in ram_parts:
            memory = motherboard['memory']
            if ram['type'] != memory['type']:
                issues.append(
                    f"{ram['name']} memory type ({ram['type']}) is not supported by the "
                    f"{motherboard_name} motherboard ({memory['type']})."
                )
            if ram['form_factor'] != memory['form_factor']:
                issues.append(
                    f"{ram['name']} memory form factor ({ram['form_factor']}) is not supported "
                    f"by the {motherboard_name} motherboard ({memory['form_factor']})."
                )
            if ram['pins'] != memory['pins']:
                issues.append(
                    f"{ram['name']} memory pin count ({ram['pins']}) does not match the "
                    f"{motherboard_name} motherboard ({memory['pins']})."
                )
            if ram['modules'] > memory['slots']:
                issues.append(
                    f"{ram['name']} requires {ram['modules']} memory slots, but the "
                    f"{motherboard_name} motherboard has {memory['slots']}."
                )
            capacity = ram['modules'] * ram['gb_per_module']
            if capacity > memory['max_capacity_gb']:
                issues.append(
                    f"{ram['name']} capacity ({capacity} GB) exceeds the "
                    f"{motherboard_name} motherboard limit ({memory['max_capacity_gb']} GB)."
                )

        for storage in storage_parts:
            if storage['form_factor'] == 'M2':
                compatible_slots = [
                    connector
                    for connector in connectors
                    if connector['kind'] == 'm2_slot'
                    and connector['key'] in storage['key'].split('+')
                    and storage['size'] in connector['lengths']
                    and storage['protocol'] in connector['protocols']
                ]
                if not compatible_slots:
                    issues.append(
                        f"{storage['name']} is not supported by the {motherboard_name} "
                        "motherboard's M.2 slots."
                    )
            elif storage['form_factor'] in ('SATA_2.5', 'SATA_3.5'):
                if not any(
                    connector['interface'] == 'SATA_6GBPS'
                    for connector in connectors
                    if connector['kind'] == 'sata_port'
                ):
                    issues.append(
                        f"The {motherboard_name} motherboard does not support SATA storage."
                    )

        power_headers = [
            connector['interface']
            for connector in connectors
            if connector['kind'] == 'power_header'
        ]
        for psu in psus:
            for connector in set(power_headers):
                required = power_headers.count(connector)
                available = psu['connectors'].get(connector, 0)
                if required > available:
                    issues.append(
                        f"The {motherboard_name} motherboard requires {required} {connector} "
                        f"power connector(s), but the {psu['name']} PSU has {available}."
                    )

    for psu in psus:
        total_power = (
            sum(cpu['tdp_w'] for cpu in cpus)
            + sum(gpu['tdp_w'] for gpu in gpus)
            + sum(fan['power_w'] for fan in fans)
            + sum(part['power_w'] for part in lighting)
            + sum(storage['power_w'] for storage in storage_parts)
        )
        if total_power > psu['watts']:
            issues.append(
                f"Build power requirements ({total_power} W) exceed the {psu['name']} PSU "
                f"capacity ({psu['watts']} W)."
            )

        required_sata_connectors = sum(
            1
            for storage in storage_parts
            if storage['form_factor'] in ('SATA_2.5', 'SATA_3.5')
        )
        available_sata_connectors = psu['connectors'].get('SATA_POWER', 0)
        if required_sata_connectors > available_sata_connectors:
            issues.append(
                f"Selected SATA storage requires {required_sata_connectors} SATA_POWER "
                f"connector(s), but the {psu['name']} PSU has {available_sata_connectors}."
            )

        for gpu in gpus:
            for connector, required in gpu['power_connectors'].items():
                available = psu['connectors'].get(connector, 0)
                if required > available:
                    issues.append(
                        f"{gpu['name']} requires {required} {connector} power connector(s), "
                        f"but the {psu['name']} PSU has {available}."
                    )

    return issues
