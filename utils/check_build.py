"""Minimal compatibility checker for this deliberately fictional demo dataset.
Usage: python check_build.py valid_am4
       python check_build.py invalid_rgb_header
       python check_build.py --all
"""
import json
import sys
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
NAMES = ['motherboards','cpus','coolers','ram','gpus','storage','cases','psus','fans','lighting']
TABLES = {name: {p['id']: p for p in json.loads((HERE/f'{name}.json').read_text())} for name in NAMES}
EXAMPLES = {b['id']:b for b in json.loads((HERE/'example_builds.json').read_text())}

def verify(build):
    """Return list of incompatibility explanations. Empty means demo-compatible."""
    b=build['components'] if 'components' in build else build
    issues=[]
    def part(cat, key):
        try: return TABLES[cat][key]
        except KeyError:
            issues.append(f'Unknown {cat} item: {key}')
            return {}
    mb=part('motherboards',b['motherboard']); cpu=part('cpus',b['cpu']); cooler=part('coolers',b['cooler']); ram=part('ram',b['ram']); case=part('cases',b['case']); psu=part('psus',b['psu'])
    if not all((mb,cpu,cooler,ram,case,psu)): return issues
    connectors={c['id']:c for c in mb['connector_layout']['connectors']}
    used={}
    def occupy(connector_id, kind, allowed=None):
        c=connectors.get(connector_id)
        if not c:
            issues.append(f'No connector called {connector_id} exists on this motherboard')
            return None
        if c['kind']!=kind:
            issues.append(f'{connector_id} is {c["kind"]}, not {kind}')
            return None
        if c['id'] in used: issues.append(f'Connector {connector_id} is used twice: {used[c["id"]]}')
        used[c['id']]=kind
        if allowed and c['interface'] not in allowed:
            issues.append(f'{connector_id} uses {c["interface"]}, expected {sorted(allowed)}')
        return c

    if cpu['socket'] != mb['cpu_socket']:
        issues.append(f'CPU socket mismatch: {cpu["socket"]} vs board {mb["cpu_socket"]}')
    if mb['cooler_mount'] not in cooler['supported_mounts']:
        issues.append(f'CPU cooler does not have a {mb["cooler_mount"]} mount')
    if cooler['cooling_capacity_w'] < cpu['tdp_w']:
        issues.append(f'Cooler capacity {cooler["cooling_capacity_w"]}W below CPU {cpu["tdp_w"]}W TDP')
    if ram['type']!=mb['memory']['type'] or ram['pins']!=mb['memory']['pins'] or ram['form_factor']!=mb['memory']['form_factor']:
        issues.append(f'RAM {ram["type"]} {ram["pins"]}-pin incompatible with board {mb["memory"]["type"]}')
    if ram['modules'] > mb['memory']['slots']:
        issues.append('RAM kit has more modules than DIMM slots')
    if ram['modules']*ram['gb_per_module'] > mb['memory']['max_capacity_gb']:
        issues.append('RAM kit exceeds motherboard maximum capacity')
    if mb['form_factor'] not in case['motherboard_form_factors']:
        issues.append(f'Motherboard form factor {mb["form_factor"]} will not fit case')
    if psu['form_factor'] not in case['supported_psu_form_factors']:
        issues.append(f'PSU form factor {psu["form_factor"]} will not fit case')
    if cooler['type']=='air' and cooler['height_mm']>case['cpu_cooler_max_height_mm']:
        issues.append('CPU cooler too tall for case')
    if cooler['type']=='liquid' and cooler['radiator_mm'] not in case['radiator_sizes_mm']:
        issues.append(f'{cooler["radiator_mm"]}mm radiator not supported in case')

    # A connected case front I/O requires one suitable internal motherboard header each.
    available=Counter(c['interface'] for c in connectors.values() if c['kind']=='usb_header')
    for header in case['front_usb_headers']:
        available[header]-=1
        if available[header]<0: issues.append(f'Case front I/O requires unavailable motherboard header: {header}')

    gpu=None
    if b.get('gpu'):
        g=b['gpu']; gpu=part('gpus',g['part_id'])
        c=occupy(g['connector_id'],'pcie_slot',{'PCIE_X16'})
        if gpu and c and c['physical_lanes']<16:
            issues.append(f'GPU needs full-length PCIe slot: {g["connector_id"]}')
        if gpu and gpu['length_mm']>case['gpu_max_length_mm']:
            issues.append(f'GPU is {gpu["length_mm"]}mm; case allows {case["gpu_max_length_mm"]}mm')
        if gpu:
            for kind,number in gpu['power_connectors'].items():
                if psu['connectors'].get(kind,0)<number: issues.append(f'PSU is missing {kind} GPU connectors ({number} required)')
    elif not cpu['integrated_graphics']:
        issues.append('No graphics card selected and CPU has no integrated graphics')

    sata_devices=0
    m2_use={}
    power_draw=cpu['tdp_w']+(gpu['tdp_w'] if gpu else 0)+60
    drive_bays=Counter()
    for s in b.get('storage',[]):
        d=part('storage',s['part_id'])
        if not d: continue
        target=s['connector_id']
        if d['form_factor']=='M2':
            c=occupy(target,'m2_slot')
            if c:
                if d['key'] not in ({'M','B+M'} if c['key']=='M' else {c['key']}):
                    issues.append(f'M.2 key {d["key"]} will not fit socket key {c["key"]}')
                if d['size'] not in c['lengths']:
                    issues.append(f'M.2 drive length {d["size"]} not supported in {target}')
                if d['protocol'] not in c['protocols']:
                    issues.append(f'M.2 drive protocol {d["protocol"]} not supported by {target}')
                m2_use[target]=d['protocol']
        else:
            occupy(target,'sata_port',{'SATA_6GBPS'})
            sata_devices+=1
            drive_bays['2_5' if d['form_factor']=='SATA_2.5' else '3_5']+=1
        power_draw+=d['power_w']
    for k in ('2_5','3_5'):
        if drive_bays[k]>case[f'sata_bays_{k}']:
            issues.append(f'Not enough {k}-inch drive bays in case')
    if sata_devices>psu['connectors'].get('SATA_POWER',0):
        issues.append('Not enough SATA power plugs')
    for rule in mb['rules']:
        cond=rule['when']
        if m2_use.get(cond['connector_id'])==cond['storage_protocol']:
            for unavailable in rule['disables']:
                if unavailable in used: issues.append(f'Using {cond["connector_id"]} as {cond["storage_protocol"]} disables occupied {unavailable}')

    for f in b.get('fans',[]):
        fan=part('fans',f['part_id'])
        c=occupy(f['connector_id'],'fan_header',{'PWM_4PIN'})
        if not fan: continue
        power_draw+=fan['power_w']
        if f.get('rgb_connector_id'):
            if not fan['rgb_connector']: issues.append('Selected fan has no RGB plug')
            else: occupy(f['rgb_connector_id'],'rgb_header',{fan['rgb_connector']})
    for light in b.get('lighting',[]):
        led=part('lighting',light['part_id'])
        if led:
            power_draw+=led['power_w']
            occupy(light['connector_id'],'rgb_header',{led['rgb_connector']})
    if power_draw*1.2>psu['watts']:
        issues.append(f'Estimated power {power_draw:.0f}W (+20% headroom) exceeds PSU {psu["watts"]}W')
    return issues

def main():
    if len(sys.argv)==1 or sys.argv[1]=='--all':
        matched=0
        for ex in EXAMPLES.values():
            issues=verify(ex)
            is_valid=not issues
            passed=is_valid==ex['expected_compatible']
            matched+=passed
            print(('PASS' if passed else 'FAIL'), ex['id'], 'compatible' if is_valid else f'{len(issues)} issue(s)')
            if not passed: print('   ', '; '.join(issues))
        print(f'Expected results: {matched}/{len(EXAMPLES)}')
        return 0 if matched==len(EXAMPLES) else 1
    ex=EXAMPLES.get(sys.argv[1])
    if not ex:
        print('Unknown build id. Try --all')
        return 2
    errors=verify(ex)
    print(ex['description'])
    print('COMPATIBLE' if not errors else 'INCOMPATIBLE')
    for error in errors: print(' - '+error)
    return 0

if __name__=='__main__': raise SystemExit(main())
