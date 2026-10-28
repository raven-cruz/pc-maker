# PC Dress-Up

### important note 
All products and specs in this repo are synthetic! Intended for use in the prototype version of this game. Generated with ChatGPT.
_________________
## Contents

| File | Contents |
| --- | --- |
| `manifest.json` | Dataset metadata, format notes and connector standards |
| `motherboards.json` | 6 motherboards with 0–100 coordinate connector maps |
| `cpus.json` | 7 processors |
| `coolers.json` | 6 air/liquid coolers |
| `ram.json` | 8 memory kits |
| `gpus.json` | 4 graphics cards |
| `storage.json` | 8 M.2/SATA drives |
| `cases.json` | 4 PC cases |
| `psus.json` | 4 power supplies |
| `fans.json` | 3 case fans |
| `lighting.json` | 2 RGB/ARGB accessories |
| `ui_palette.json` | Optional colors for board-grid rendering |
| `example_builds.json` | 19 sample configurations (5 valid, 14 intentionally invalid) |
| `check_build.py` | Zero-dependency Python example compatibility checker |

## Test the examples

Python 3.9+ and standard library only:

```bash
cd pc_dressup_prototype
python check_build.py --all
python check_build.py valid_am5
python check_build.py invalid_rgb_header
```

`--all` verifies that every sample produces the expected compatible/incompatible classification.

## Connector map for your graphical motherboard

Each motherboard has:

```json
{
  "cpu_socket": "AM4",
  "cooler_mount": "AM4",
  "form_factor": "mATX",
  "memory": {"type": "DDR4", "pins": 288, "slots": 4},
  "connector_layout": {
    "coordinate_system": "top-down ... x/y/w/h 0-100",
    "connectors": [
      {
        "id": "M2_1", "kind": "m2_slot", "interface": "M2_M",
        "layout": {"x": 32, "y": 54, "w": 28, "h": 3},
        "key": "M", "lengths": [2242, 2260, 2280],
        "protocols": ["NVMe"], "max_pcie_generation": 4
      }
    ]
  }
}
```

Use `layout` coordinates as percentages of board bounding box to draw a rectangle for each connector. `kind` picks a color from `ui_palette.json`. These positions are **not physical engineering measurements** and may overlap on dense boards; they just create a recognizable layout for the game. CPU socket can be rendered as a rectangle while CPU itself occupies it.

Every connector has a stable ID (e.g. `PCIE1`, `M2_1`, `SATA4`, `ARGB1`). Sample builds explicitly assign parts to those IDs. When adding a component to the UI, list connectors where it can fit, highlight a candidate connector, and run `verify` to show any rule violations. You can add snap-to-grid rendering or draggable components later.

## Build structure

```json
{
  "motherboard": "mb_aster_b550m",
  "cpu": "cpu_a4_65",
  "cooler": "cooler_am4_stock",
  "ram": "ram_d4_16",
  "gpu": {"part_id": "gpu_mid170", "connector_id": "PCIE1"},
  "storage": [{"part_id": "ssd_nvme4_2280", "connector_id": "M2_1"}],
  "case": "case_pocket",
  "psu": "psu_atx650",
  "fans": [{"part_id": "fan_plain120", "connector_id": "CHA_FAN1"}],
  "lighting": []
}
```

All of these IDs can be looked up in the corresponding category JSON by `id`.

## Modeled compatibility rules

- CPU socket ↔ motherboard socket
- Cooler mounting bracket and approximate cooling capacity ↔ processor
- RAM type (DDR4 vs DDR5), UDIMM pin count, module count, capacity
- Motherboard form factor ↔ case fit
- Cooler height/radiator fit and GPU length ↔ case
- PSU form factor, approximate 20% power headroom, GPU auxiliary power connectors
- PCIe x16-length slot fit (PCIe generations are backward-compatible)
- M.2 protocol, key, drive length and per-board shared-SATA restrictions
- SATA data connectors, drive bays, PSU SATA power
- Front-panel USB 2.0, USB 3.x Type-A and USB Type-C **internal** header availability
- PWM fan and 5V 3-pin ARGB vs 12V 4-pin RGB header type, including occupied connector checks

Sample invalid builds illustrate conflicts, including wrong CPU socket, DDR5 on a DDR4 board, oversized GPU, unavailable front USB-C, M.2 SATA shared-port disablement, wrong RGB voltage, insufficient GPU power connectors and inadequate CPU cooling.

## Simplifications to refine later

- The schema doesn't model BIOS version and CPU-generation support, PCIe lane sharing except explicit M.2/SATA rules, motherboard/case standoff positions, GPU slot thickness interference, RAM height against air coolers, fan splitters/hubs, PWM vs 3-pin DC negotiation, detailed power rails/transient draw, or motherboard VRM limits.
- M.2 speed may step down without incompatibility; the checker does not flag performance bottlenecks.
- Header requirements are deliberately treated as strict: a case front USB port without its matching internal header is classified as incompatible, although a real PC could often leave it disconnected.
- `cooling_capacity_w` and PSU headroom rules are rough invented gameplay metrics, not hardware recommendations.
- Model names are fictional, but form-factor/socket names are familiar hardware conventions.

The `check_build.py` logic is intended as a transparent starter, **not** a comprehensive real-world compatibility engine.
