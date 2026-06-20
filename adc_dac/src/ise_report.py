#!/usr/bin/env python3
"""Parse Xilinx ISE report files and display a colored summary."""

import re
import sys
from pathlib import Path

# ANSI colors
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RED    = "\033[91m"
DIM    = "\033[2m"
WHITE  = "\033[97m"

def color_pct(used, total):
    pct = used / total * 100 if total else 0
    if pct >= 80:
        c = RED
    elif pct >= 50:
        c = YELLOW
    else:
        c = GREEN
    return f"{c}{pct:5.1f}%{RESET}"

def header(title):
    bar = "─" * 60
    print(f"\n{CYAN}{BOLD}┌{bar}┐{RESET}")
    print(f"{CYAN}{BOLD}│  {title:<58}│{RESET}")
    print(f"{CYAN}{BOLD}└{bar}┘{RESET}")

def row(label, used, total, unit=""):
    pct_str = color_pct(used, total) if total else f"{DIM}  n/a {RESET}"
    print(f"  {WHITE}{label:<40}{RESET} {YELLOW}{used:>6}{RESET} / {DIM}{total:<6}{RESET} {unit:4}  {pct_str}")

def divider():
    print(f"  {DIM}{'─' * 65}{RESET}")

# ── Parsers ──────────────────────────────────────────────────────────────────

def parse_utilization_block(text):
    """Extract 'N out of M' patterns with their labels."""
    pattern = re.compile(
        r'(?:Number of|Number)\s+([^\n:]+?):\s+'
        r'(\d[\d,]*)\s+out of\s+(\d[\d,]*)',
        re.IGNORECASE
    )
    results = {}
    for m in pattern.finditer(text):
        label = m.group(1).strip()
        used  = int(m.group(2).replace(',', ''))
        total = int(m.group(3).replace(',', ''))
        results[label] = (used, total)
    return results

def parse_syr(path):
    text = path.read_text(errors='replace')
    util = parse_utilization_block(text)

    header(f"Synthesis  ({path.name})")
    keys = [
        ("Slice Registers",           "FF"),
        ("Slice LUTs",                "LUT"),
        ("fully used LUT-FF pairs",   "pair"),
        ("bonded IOBs",               "IO"),
        ("BUFG/BUFGCTRLs",           "BUFG"),
        ("Block RAM/FIFO",            "BRAM"),
        ("DSP48A1s",                  "DSP"),
    ]
    found = False
    for key, unit in keys:
        for label, (used, total) in util.items():
            if key.lower() in label.lower():
                row(label, used, total, unit)
                found = True
                break
    if not found:
        print(f"  {DIM}No utilization data found.{RESET}")

def parse_par(path):
    text = path.read_text(errors='replace')
    util = parse_utilization_block(text)

    header(f"Place & Route  ({path.name})")
    keys = [
        ("Slice Registers",   "FF"),
        ("Slice LUTs",        "LUT"),
        ("occupied Slices",   "slice"),
        ("bonded IOBs",       "IO"),
        ("BUFG",              "BUFG"),
        ("Block RAM",         "BRAM"),
        ("DSP48",             "DSP"),
    ]
    found = False
    for key, unit in keys:
        for label, (used, total) in util.items():
            if key.lower() in label.lower():
                row(label, used, total, unit)
                found = True
                break
    if not found:
        print(f"  {DIM}No utilization data found.{RESET}")

def parse_twr(path):
    text = path.read_text(errors='replace')

    header(f"Timing  ({path.name})")

    # ── Overall result ────────────────────────────────────────────────────────
    errors_m = re.search(r'Timing errors:\s*(\d+)\s+Score:\s*(\d+)', text)
    if errors_m:
        n_errors = int(errors_m.group(1))
        score    = int(errors_m.group(2))
        status   = f"{GREEN}PASSED{RESET}" if n_errors == 0 else f"{RED}FAILED  ({n_errors} errors){RESET}"
        print(f"  {WHITE}{'Overall timing':<40}{RESET} {status}")
        if score > 0:
            print(f"  {WHITE}{'Score (lower=better)':<40}{RESET} {RED}{score}{RESET}")

    # ── Design statistics: minimum period / max frequency ─────────────────────
    minper_m = re.search(r'Minimum period:\s*([\d.]+)ns.*?Maximum frequency:\s*([\d.]+)MHz', text, re.IGNORECASE)
    if minper_m:
        period = float(minper_m.group(1))
        freq   = float(minper_m.group(2))
        print(f"  {WHITE}{'Max frequency (design stat)':<40}{RESET} {GREEN}{freq:.3f} MHz{RESET}  {DIM}(min period {period:.3f} ns){RESET}")

    # ── Per-constraint summary from Derived Constraint Report ─────────────────
    # Parse the table rows: constraint name | period req | actual direct | actual deriv | errors direct | errors deriv
    table_row = re.compile(
        r'^\|(\S[^|]+?)\s*\|\s*([\d.]+)ns\s*\|\s*([\d.]+)ns\s*\|\s*([^\|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|',
        re.MULTILINE
    )
    constraints = []
    for m in table_row.finditer(text):
        name      = m.group(1).strip()
        req_ns    = float(m.group(2))
        actual_ns = float(m.group(3))
        errors    = int(m.group(5)) + int(m.group(6))
        constraints.append((name, req_ns, actual_ns, errors))

    if constraints:
        divider()
        print(f"  {BOLD}{WHITE}{'Constraint':<32} {'Req':>8}  {'Actual':>8}  {'Slack':>8}  {'Errors':>6}{RESET}")
        divider()
        for name, req, actual, errors in constraints:
            slack     = req - actual
            sc        = GREEN if slack >= 0 else RED
            err_str   = f"{RED}{errors}{RESET}" if errors > 0 else f"{DIM}0{RESET}"
            print(f"  {WHITE}{name:<32}{RESET} {DIM}{req:>7.3f}ns{RESET}  "
                  f"{YELLOW}{actual:>7.3f}ns{RESET}  {sc}{slack:>+7.3f}ns{RESET}  {err_str:>6}")

    # ── Worst setup slack across all paths ────────────────────────────────────
    setup_slacks = [
        float(m.group(1))
        for m in re.finditer(r'Slack \(setup path\):\s*([-\d.]+)ns', text)
    ]
    hold_slacks = [
        float(m.group(1))
        for m in re.finditer(r'Slack \(hold path\):\s*([-\d.]+)ns', text)
    ]
    if setup_slacks or hold_slacks:
        divider()
        if setup_slacks:
            ws = min(setup_slacks)
            c  = GREEN if ws >= 0 else RED
            print(f"  {WHITE}{'Worst setup slack':<40}{RESET} {c}{ws:+.3f} ns{RESET}")
        if hold_slacks:
            wh = min(hold_slacks)
            c  = GREEN if wh >= 0 else RED
            print(f"  {WHITE}{'Worst hold slack':<40}{RESET} {c}{wh:+.3f} ns{RESET}")

    # ── Paths covered ─────────────────────────────────────────────────────────
    paths_m = re.search(r'Constraints cover\s+(\d+)\s+paths', text)
    if paths_m:
        print(f"  {DIM}Paths analyzed: {paths_m.group(1)}{RESET}")

def parse_mrp(path):
    text = path.read_text(errors='replace')
    util = parse_utilization_block(text)

    header(f"Map  ({path.name})")
    keys = [
        ("Slice Registers",          "FF"),
        ("Slice LUTs",               "LUT"),
        ("occupied Slices",          "slice"),
        ("bonded IOBs",              "IO"),
        ("BUFG",                     "BUFG"),
        ("Block RAM",                "BRAM"),
        ("DSP48",                    "DSP"),
        ("PLL_ADV",                  "PLL"),
        ("BUFIO2",                   "BUFIO"),
    ]
    found = False
    for key, unit in keys:
        for label, (used, total) in util.items():
            if key.lower() in label.lower():
                row(label, used, total, unit)
                found = True
                break
    if not found:
        print(f"  {DIM}No utilization data found.{RESET}")


# ── Main ─────────────────────────────────────────────────────────────────────

PARSERS = {
    '.syr': parse_syr,
    '.par': parse_par,
    '.twr': parse_twr,
    '.mrp': parse_mrp,
}

def main():
    if len(sys.argv) < 2:
        # Auto-discover in current directory
        paths = [p for p in Path('.').iterdir() if p.suffix in PARSERS]
        if not paths:
            print(f"{RED}No ISE report files found in current directory.{RESET}")
            print(f"Usage: {sys.argv[0]} [file1 file2 ...]")
            sys.exit(1)
    else:
        paths = [Path(a) for a in sys.argv[1:]]

    # Process in a logical order
    order = ['.syr', '.mrp', '.par', '.twr']
    paths = sorted(paths, key=lambda p: order.index(p.suffix) if p.suffix in order else 99)

    for path in paths:
        if not path.exists():
            print(f"{RED}File not found: {path}{RESET}")
            continue
        parser = PARSERS.get(path.suffix)
        if parser:
            parser(path)
        else:
            print(f"{YELLOW}Skipping unsupported file: {path}{RESET}")

    print()

if __name__ == '__main__':
    main()
