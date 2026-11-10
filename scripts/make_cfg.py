"""Render the control-flow graph for Task 5 -> docs/cfg.png.

The graph follows the short-circuit convention required by the brief: every
atomic condition inside a compound ``if`` becomes its OWN decision node, so

    if 0 <= course.enrolled <= course.capacity or course.capacity < 1:

is mapped as three chained decisions (D2a, D2b, D2c) rather than one.

Run from the repository root:
    python scripts/make_cfg.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

DOCS = Path(__file__).resolve().parent.parent / "docs"
DOCS.mkdir(exist_ok=True)

DEC = "#1f4e79"      # decision edges
TER = "#7b2d26"      # terminal / return edges
DEAD = "#c00000"     # infeasible edge
GRY = "#8a8a8a"

SPINE = 0.0          # x of the vertical decision chain
ACT = 4.6            # x centre of the action/return boxes
EXIT = 7.9           # x centre of the exit bar

HALF_W = 1.55        # diamond half width
HALF_H = 0.31        # diamond half height
BOX_HW = 1.6         # action box half width
BOX_HH = 0.25        # action box half height

Y = {
    "E": 1.50, "D1": 0.55, "D2a": -0.75, "D2b": -1.95, "D2c": -3.15,
    "D3": -4.35, "D4": -5.55, "D5": -6.75, "D6": -7.95, "D7": -9.15,
    "R6": -10.35,
}
YA = {"P1": 0.55, "P2": -1.95, "R1": -4.35, "R2": -5.55, "R3": -6.75,
      "R4": -7.95, "R5": -9.15}


def diamond(ax, x, y, text, dead=False, num=None):
    ax.add_patch(Polygon(
        [(x - HALF_W, y), (x, y + HALF_H), (x + HALF_W, y), (x, y - HALF_H)],
        closed=True, facecolor="#eaf1fb", edgecolor=DEAD if dead else DEC,
        linewidth=1.5, linestyle="--" if dead else "-", zorder=3))
    ax.text(x, y, text, fontsize=7.4, ha="center", va="center", zorder=4,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.92))
    if num:
        ax.text(x + HALF_W + 0.02, y + HALF_H + 0.30, f"n{num}", fontsize=7,
                color=GRY, ha="center", va="center", zorder=4)


def box(ax, x, y, text, kind="process", dead=False, width=3.2, height=0.5,
        num=None):
    style = "round,pad=0.02,rounding_size=0.12" if kind == "return" else \
            "square,pad=0.02"
    ax.add_patch(FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height, boxstyle=style,
        facecolor="#fdf2e9" if kind == "return" else "#f4f4f4",
        edgecolor=DEAD if dead else TER, linewidth=1.5,
        linestyle="--" if dead else "-", zorder=3))
    ax.text(x, y, text, fontsize=7.4, ha="center", va="center", zorder=4,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.92))
    if num:
        ax.text(x + width / 2 + 0.02, y + height / 2 + 0.22, f"n{num}",
                fontsize=7, color=GRY, ha="center", va="center", zorder=4)


def terminator(ax, x, y, num=None):
    ax.add_patch(FancyBboxPatch(
        (x - 0.9, y - 0.225), 1.8, 0.45,
        boxstyle="round,pad=0.02,rounding_size=0.22",
        facecolor="#dce9f7", edgecolor=DEC, linewidth=1.6, zorder=3))
    ax.text(x, y, "Entry", fontsize=8.4, fontweight="bold",
            ha="center", va="center", zorder=4)
    if num:
        ax.text(x + 0.95, y + 0.37, f"n{num}", fontsize=7, color=GRY,
                ha="center", va="center", zorder=4)


def exit_bar(ax, y_top=1.0, y_bot=-11.1, num=None):
    ax.add_patch(FancyBboxPatch(
        (EXIT - 0.25, y_bot), 0.5, y_top - y_bot,
        boxstyle="round,pad=0.02,rounding_size=0.18",
        facecolor="#dce9f7", edgecolor=DEC, linewidth=1.6, zorder=3))
    ax.text(EXIT - 0.55, y_bot - 0.45, f"n{num}  X exit", fontsize=8,
            fontweight="bold", ha="left", va="center", color=DEC, zorder=4)


def arrow(ax, pts, color=DEC, dashed=False, label=None, dx=0.0, dy=0.24):
    """Polyline arrow; an arrowhead is drawn on the final segment only."""
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        ax.add_patch(FancyArrowPatch(
            a, b, arrowstyle="-" if i < len(pts) - 2 else "-|>",
            mutation_scale=10, linewidth=1.3, color=color,
            linestyle="--" if dashed else "-", shrinkA=0, shrinkB=0, zorder=2))
    if label:
        ax.text((pts[0][0] + pts[1][0]) / 2 + dx,
                (pts[0][1] + pts[1][1]) / 2 + dy, label, fontsize=7.6,
                fontweight="bold", color=color, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.12", facecolor="white",
                          edgecolor="none"), zorder=5)


def draw():
    fig, ax = plt.subplots(figsize=(13.2, 14.4), dpi=170)
    ax.set_axis_off()
    ax.set_xlim(-3.8, 12.4)
    ax.set_ylim(-14.6, 2.0)

    # -- nodes (n1..n19 in execution order) ----------------------------------
    terminator(ax, SPINE, Y["E"], num=1)
    diamonds = [
        (2, "D1",  "dues < 0 ?", False),
        (4, "D2a", "0 <= enrolled ?", False),
        (5, "D2b", "enrolled <= capacity ?", False),
        (6, "D2c", "capacity < 1 ?", False),
        (8, "D3",  "dues > 1000 ?", False),
        (10, "D4", "code in registered_courses ?", False),
        (12, "D5", "prerequisites_satisfied\nreturns False ?", False),
        (14, "D6", "check_credit_limit\nreturns False ?", False),
        (16, "D7", "enrolled > capacity ?", True),
    ]
    for num, key, text, dead in diamonds:
        diamond(ax, SPINE, Y[key], text, dead=dead, num=num)

    actions = [
        (3,  "P1", 0.55, "P1  raise ValueError\n'Invalid dues'", "process", False),
        (7,  "P2", -1.95, "P2  raise ValueError\n'Invalid capacity or enrollment'", "process", False),
        (9,  "R1", -4.35, "R1  return 'DUES_BLOCK'", "return", False),
        (11, "R2", -5.55, "R2  return 'ALREADY_REGISTERED'", "return", False),
        (13, "R3", -6.75, "R3  return 'PREREQUISITES_MISSING'", "return", False),
        (15, "R4", -7.95, "R4  return 'CREDIT_LIMIT'", "return", False),
        (17, "R5", -9.15, "R5  return 'WAITLISTED'", "return", True),
    ]
    for num, key, yy, text, kind, dead in actions:
        box(ax, ACT, yy, text, kind=kind, dead=dead, num=num)

    box(ax, SPINE, Y["R6"], "R6  return 'REGISTERED'", kind="return", width=3.2,
        num=18)
    exit_bar(ax, num=19)

    # -- spine edges (fall-through) -----------------------------------------
    spine_edges = [
        ("E", "D1", None),
        ("D1", "D2a", "F"),
        ("D2a", "D2b", "T"),
        ("D2b", "D2c", "T"),
        ("D2c", "D3", "F"),
        ("D3", "D4", "F"),
        ("D4", "D5", "F"),
        ("D5", "D6", "F"),
        ("D6", "D7", "F"),
        ("D7", "R6", "F"),
    ]
    for a, b, lbl in spine_edges:
        top = Y[a] - (0.225 if a == "E" else HALF_H)
        bot = Y[b] + (0.25 if b == "R6" else HALF_H)
        arrow(ax, [(SPINE, top), (SPINE, bot)], label=lbl, dx=0.42, dy=0.0)

    # -- on-true edges out to the action column ------------------------------
    for dkey, akey, lbl, dead in [
        ("D1", "P1", "T", False),
        ("D3", "R1", "T", False),
        ("D4", "R2", "T", False),
        ("D5", "R3", "T", False),
        ("D6", "R4", "T", False),
        ("D7", "R5", "T", True),
    ]:
        arrow(ax, [(SPINE + HALF_W, Y[dkey]), (ACT - BOX_HW, YA[akey])],
              color=DEAD if dead else DEC, dashed=dead, label=lbl, dx=0.0,
              dy=0.26)

    # the three short-circuit atoms of D2 merge into P2
    y2 = YA["P2"]
    arrow(ax, [(SPINE + HALF_W, Y["D2a"]), (2.25, Y["D2a"]), (2.25, y2 - 0.10),
               (ACT - BOX_HW, y2 - 0.10)], label="F", dx=0.0, dy=0.26)
    arrow(ax, [(SPINE + HALF_W, Y["D2b"]), (ACT - BOX_HW, y2)],
          label="F", dx=0.0, dy=0.26)
    arrow(ax, [(SPINE + HALF_W, Y["D2c"]), (2.55, Y["D2c"]), (2.55, y2 + 0.10),
               (ACT - BOX_HW, y2 + 0.10)], label="T", dx=0.0, dy=0.26)

    # -- everything terminates in X -----------------------------------------
    for akey in ("P1", "P2", "R1", "R2", "R3", "R4", "R5"):
        dead = akey == "R5"
        arrow(ax, [(ACT + BOX_HW, YA[akey]), (EXIT - 0.25, YA[akey])],
              color=DEAD if dead else TER, dashed=dead)
    arrow(ax, [(SPINE + 1.6, Y["R6"]), (EXIT - 0.25, Y["R6"])])

    # -- legend --------------------------------------------------------------
    ax.text(11.0, 1.55, "Legend", fontsize=9, fontweight="bold", color=DEC)
    ax.plot([10.85, 10.85], [1.35, -4.7], color="#bbbbbb", lw=1.0)
    items = [
        ("diamond", "decision node (one branch in, two out)"),
        ("rect", "process node  (P1, P2: raise)"),
        ("roundrect", "return node  (R1-R6)"),
        ("bar", "exit node X - single exit"),
        ("red", "dashed red = edge that can never be taken"),
    ]
    for i, (kind, text) in enumerate(items):
        y = 1.15 - i * 0.72
        if kind == "diamond":
            ax.add_patch(Polygon([(10.95, y), (11.5, y + 0.28), (12.05, y),
                                  (11.5, y - 0.28)], closed=True,
                                 facecolor="#eaf1fb", edgecolor=DEC, lw=1.2))
        elif kind == "rect":
            ax.add_patch(FancyBboxPatch((11.0, y - 0.22), 1.0, 0.44,
                          boxstyle="square,pad=0.02", facecolor="#f4f4f4",
                          edgecolor=TER, lw=1.2))
        elif kind == "roundrect":
            ax.add_patch(FancyBboxPatch((11.0, y - 0.22), 1.0, 0.44,
                          boxstyle="round,pad=0.02,rounding_size=0.18",
                          facecolor="#fdf2e9", edgecolor=TER, lw=1.2))
        elif kind == "bar":
            ax.add_patch(FancyBboxPatch((11.05, y - 0.26), 0.28, 0.52,
                          boxstyle="round,pad=0.02,rounding_size=0.14",
                          facecolor="#dce9f7", edgecolor=DEC, lw=1.2))
        else:
            ax.plot([11.0, 12.0], [y, y], color=DEAD, ls="--", lw=1.4)
        ax.text(12.2, y, text, fontsize=7.4, ha="left", va="center")

    # -- annotation footer ---------------------------------------------------
    ax.text(-3.6, -12.15,
            "Short-circuit rule applied (Tasks 2)\n"
            "-----------------------------------------------\n"
            "Line 48 is a compound condition, so it is NOT one\n"
            "decision node. Python evaluates the chain left to\n"
            "right and stops as soon as it knows the answer -\n"
            "exactly like   if age >= 18 and has_id:  , which\n"
            "becomes two checks and the second is reached only\n"
            "when the first is true.\n\n"
            "  D2 = not (0 <= enrolled <= capacity) or capacity < 1\n"
            "     = not (C2 and C3) or C4\n"
            "     C2 = 0 <= enrolled          -> D2a\n"
            "     C3 = enrolled <= capacity   -> D2b   (only if C2 true)\n"
            "     C4 = capacity < 1           -> D2c   (only if C2 and C3 true)\n\n"
            "Once an atom decides the answer the remaining atoms are\n"
            "skipped ('not evaluated'). That is why D2 is a chain and\n"
            "not a tree, and why D2's atoms keep D2a true in BP3-BP10.",
            fontsize=7.8, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f7f7f7",
                      edgecolor="#999999"))

    ax.text(4.3, -12.15,
            "Counts (Tasks 3 and 4)\n"
            "-----------------------------------------------\n"
            "N = 19 nodes   n1 E, n2 D1, n3 P1, n4 D2a, n5 D2b, n6 D2c,\n"
            "               n7 P2, n8 D3, n9 R1, n10 D4, n11 R2, n12 D5,\n"
            "               n13 R3, n14 D6, n15 R4, n16 D7, n17 R5,\n"
            "               n18 R6, n19 X\n"
            "E = 27 edges\n\n"
            "Formula 1   V(G) = E - N + 2 = 27 - 19 + 2 = 10\n"
            "Formula 2   V(G) = P + 1 = 9 + 1 = 10\n"
            "                    (9 predicate nodes: D1, D2a, D2b, D2c,\n"
            "                     D3, D4, D5, D6, D7)\n"
            "=> both formulas agree: V(G) = 10\n\n"
            "Basis paths = 10   (BP1..BP10, one per new edge)\n"
            "Feasible    = 9    - BP9 needs D7 -> R5 and is unreachable:\n"
            "                      D2b already rejects every input with\n"
            "                      enrolled > capacity, so a full course\n"
            "                      is reported REGISTERED instead of\n"
            "                      WAITLISTED (line 59 is dead code).",
            fontsize=7.8, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#fffdf0",
                      edgecolor="#d8c98a"))

    ax.set_title("Control-flow graph - registration_decision()  "
                 "(registration.py lines 44-60), short-circuit expanded",
                 fontsize=11.5, fontweight="bold", pad=10)
    fig.savefig(DOCS / "cfg.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    draw()
    print(f"wrote {DOCS / 'cfg.png'}")
