"""Redraw the 15 figures and five tables from Chapter A3 as editable draw.io files."""

from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "image" / "axi-a3"
DRAWIO = Path(r"C:\Program Files\draw.io\draw.io.exe")
WIDTH = 1440
FONT = "Microsoft YaHei"
INK = "#172b42"
MUTED = "#697586"
LINE = "#27364a"
HEADER = "#dfe6ee"
SHADE = "#c9cdd3"
LIGHT = "#f6f8fa"
BLUE = "#dbeafe"


class Figure:
    def __init__(self, title: str, height: int):
        self.title = title
        self.height = height
        self.doc = ET.Element("mxfile", host="app.diagrams.net")
        diagram = ET.SubElement(self.doc, "diagram", name=title)
        model = ET.SubElement(
            diagram, "mxGraphModel", page="1", pageWidth=str(WIDTH), pageHeight=str(height)
        )
        self.root = ET.SubElement(model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.counter = 2

    def cell(self, x, y, w, h, value="", *, fill="#ffffff", size=24, bold=False,
             align="center", stroke=LINE, rounded=False, color=INK):
        c = ET.SubElement(
            self.root, "mxCell", id=str(self.counter), value=value, vertex="1", parent="1",
            style=(
                f"rounded={int(rounded)};whiteSpace=wrap;html=0;fontFamily={FONT};"
                f"fontSize={size};fontColor={color};fontStyle={int(bold)};fillColor={fill};"
                f"strokeColor={stroke};strokeWidth=2;align={align};verticalAlign=middle;spacing=8;"
            ),
        )
        self.counter += 1
        ET.SubElement(c, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        return c.attrib["id"]

    def text(self, x, y, w, h, value, *, size=24, bold=False, align="center", color=INK):
        return self.cell(x, y, w, h, value, fill="none", stroke="none", size=size,
                         bold=bold, align=align, color=color)

    def edge(self, source=None, target=None, *, points=None, start=False, end=False,
             dashed=False, width=3, color=LINE):
        style = (
            "edgeStyle=none;rounded=0;orthogonalLoop=1;jettySize=auto;html=0;"
            f"strokeColor={color};strokeWidth={width};dashed={int(dashed)};"
            f"startArrow={'classic' if start else 'none'};startFill=1;"
            f"endArrow={'classic' if end else 'none'};endFill=1;"
        )
        attrs = {"id": str(self.counter), "edge": "1", "parent": "1", "style": style}
        if source is not None:
            attrs["source"] = source
        if target is not None:
            attrs["target"] = target
        e = ET.SubElement(self.root, "mxCell", **attrs)
        self.counter += 1
        geo = ET.SubElement(e, "mxGeometry", relative="1", **{"as": "geometry"})
        if points:
            arr = ET.SubElement(geo, "Array", **{"as": "points"})
            for x, y in points:
                ET.SubElement(arr, "mxPoint", x=str(x), y=str(y))
        return e.attrib["id"]

    def line(self, points, *, dashed=False, width=3, color=LINE):
        x1, y1 = points[0]
        x2, y2 = points[-1]
        e = ET.SubElement(
            self.root, "mxCell", id=str(self.counter), edge="1", parent="1",
            style=(
                "edgeStyle=none;rounded=0;html=0;startArrow=none;endArrow=none;"
                f"strokeColor={color};strokeWidth={width};dashed={int(dashed)};"
            ),
        )
        self.counter += 1
        geo = ET.SubElement(e, "mxGeometry", relative="1", **{"as": "geometry"})
        ET.SubElement(geo, "mxPoint", x=str(x1), y=str(y1), **{"as": "sourcePoint"})
        ET.SubElement(geo, "mxPoint", x=str(x2), y=str(y2), **{"as": "targetPoint"})
        if len(points) > 2:
            arr = ET.SubElement(geo, "Array", **{"as": "points"})
            for x, y in points[1:-1]:
                ET.SubElement(arr, "mxPoint", x=str(x), y=str(y))

    def frame(self):
        self.cell(0, 0, WIDTH, self.height, "", fill="#ffffff", stroke="#ffffff", size=1)

    def footer(self, note="根据原图双语重绘 / Bilingual redraw based on original figure"):
        self.text(25, self.height - 80, 1390, 40, self.title, size=27, bold=True)
        self.text(25, self.height - 40, 1390, 28, note, size=20, color=MUTED)

    def save(self, name: str):
        OUT.mkdir(parents=True, exist_ok=True)
        source = OUT / f"{name}.drawio"
        target = source.with_suffix(".png")
        ET.ElementTree(self.doc).write(source, encoding="utf-8", xml_declaration=True)
        if not DRAWIO.exists():
            raise FileNotFoundError(f"draw.io CLI not found: {DRAWIO}")
        result = subprocess.run(
            [str(DRAWIO), "--export", "--format", "png", "--width", str(WIDTH),
             "--output", str(target), str(source)],
            capture_output=True, text=True, timeout=120,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode or not target.exists():
            raise RuntimeError(result.stdout + result.stderr)
        print(target.name)


def make_table(name, title, headers, rows, widths=None, row_h=70):
    widths = widths or [1320 // len(headers)] * len(headers)
    height = 125 + row_h * (len(rows) + 1) + 80
    f = Figure(title, height)
    f.frame()
    x0, y = 60, 70
    for i, head in enumerate(headers):
        f.cell(x0 + sum(widths[:i]), y, widths[i], row_h, head, fill=HEADER, size=24, bold=True)
    y += row_h
    for r, row in enumerate(rows):
        fill = "#ffffff" if r % 2 == 0 else LIGHT
        for i, value in enumerate(row):
            f.cell(x0 + sum(widths[:i]), y, widths[i], row_h, value, fill=fill, size=23,
                   align="left" if len(value) > 24 else "center")
        y += row_h
    f.footer("根据原表双语重绘 / Bilingual redraw based on original table")
    f.save(name)


def draw_clock(f, y, x0=300, cycles=5, step=150, amp=34):
    pts = [(x0, y)]
    x = x0
    for _ in range(cycles):
        pts += [(x + step * .25, y), (x + step * .25, y - amp),
                (x + step * .75, y - amp), (x + step * .75, y), (x + step, y)]
        x += step
    f.line(pts)


def wave(f, y, levels, x0=300, step=150, amp=42):
    pts = [(x0, y if not levels[0] else y - amp)]
    prev = levels[0]
    for i, level in enumerate(levels[1:], start=1):
        x = x0 + i * step
        pts.append((x, y if not prev else y - amp))
        if level != prev:
            pts.append((x, y if not level else y - amp))
        prev = level
    pts.append((x0 + len(levels) * step, y if not prev else y - amp))
    f.line(pts)


def timing(name, title, markers, valid, ready, info_start, info_end):
    f = Figure(title, 600)
    f.frame()
    x0, step = 300, 150
    for label, idx in markers:
        x = x0 + idx * step
        f.text(x - 45, 35, 90, 32, label, size=22)
        f.line([(x, 70), (x, 430)], dashed=True, width=2, color="#a7b0bd")
    f.text(70, 105, 190, 42, "ACLK", size=23, bold=True, align="right")
    f.text(70, 205, 190, 42, "INFORMATION", size=22, bold=True, align="right")
    f.text(70, 305, 190, 42, "VALID", size=23, bold=True, align="right")
    f.text(70, 405, 190, 42, "READY", size=23, bold=True, align="right")
    draw_clock(f, 150, x0=x0, cycles=5, step=step)
    f.cell(x0 + info_start * step, 195, (info_end - info_start) * step, 55, "有效信息 / INFORMATION",
           fill=BLUE, size=22, bold=True)
    wave(f, 350, valid, x0=x0, step=step)
    wave(f, 450, ready, x0=x0, step=step)
    f.footer()
    f.save(name)


def supplemental_no_combinational_path():
    """Explain the interface input/output combinational-path prohibition."""
    f = Figure("为什么接口输入到输出之间不得存在组合路径", 1110)
    f.frame()
    f.text(70, 25, 1300, 38, "适用于 Master 接口和 Slave 接口", size=24, bold=True)

    f.cell(60, 80, 640, 320, "", fill="#fff7f7", stroke="#d85b5b", rounded=True)
    f.text(90, 100, 580, 40, "禁止：组合直通路径", size=25, bold=True, color="#b42318")
    left_in = f.cell(105, 190, 150, 75, "接口输入", fill="#ffffff", rounded=True, size=23, bold=True)
    left_logic = f.cell(305, 190, 150, 75, "组合逻辑", fill="#fee2e2", stroke="#d85b5b", rounded=True, size=23, bold=True)
    left_out = f.cell(505, 190, 150, 75, "接口输出", fill="#ffffff", rounded=True, size=23, bold=True)
    f.edge(left_in, left_logic, end=True, color="#b42318")
    f.edge(left_logic, left_out, end=True, color="#b42318")
    f.text(165, 300, 430, 50, "× 输入变化可在同一周期直接影响输出", size=21, bold=True, color="#b42318")

    f.cell(740, 80, 640, 320, "", fill="#f3fbf5", stroke="#4f9d69", rounded=True)
    f.text(770, 100, 580, 40, "合规：用时序边界切断路径", size=25, bold=True, color="#16794a")
    right_in = f.cell(770, 190, 125, 75, "接口输入", fill="#ffffff", rounded=True, size=21, bold=True)
    right_logic = f.cell(925, 190, 125, 75, "组合逻辑", fill="#ffffff", rounded=True, size=21, bold=True)
    right_reg = f.cell(1080, 178, 135, 100, "时序边界\n（寄存器）", fill="#dcfce7", stroke="#4f9d69", rounded=True, size=21, bold=True)
    right_out = f.cell(1245, 190, 105, 75, "接口输出", fill="#ffffff", rounded=True, size=20, bold=True)
    f.edge(right_in, right_logic, end=True)
    f.edge(right_logic, right_reg, end=True)
    f.edge(right_reg, right_out, end=True)
    f.text(1090, 292, 115, 34, "ACLK", size=21, bold=True, color="#16794a")
    f.line([(1148, 292), (1148, 278)], width=2, color="#16794a")
    f.text(835, 330, 450, 45, "✓ 输出只在时钟边沿之后更新", size=21, bold=True, color="#16794a")

    f.text(60, 435, 1320, 42, "为什么禁止", size=27, bold=True)
    reasons = [
        (60, "避免组合环路", "两个组件互连后，输入与输出的\n组合依赖可能首尾相接。"),
        (510, "缩短跨组件时序路径", "组合路径不会穿过多个接口级联，\n更容易满足 ACLK 时序。"),
        (960, "保证握手信号稳定", "VALID、READY 在采样边沿前稳定，\n避免毛刺或不确定状态传播。"),
    ]
    for x, heading, detail in reasons:
        f.cell(x, 485, 420, 145, "", fill="#f6f8fa", stroke="#a7b0bd", rounded=True)
        f.text(x + 20, 500, 380, 34, heading, size=22, bold=True)
        f.text(x + 20, 540, 380, 72, detail, size=20)

    f.text(60, 660, 1320, 42, "典型错误例子：VALID 与 READY 形成组合环路", size=26, bold=True, color="#b42318")
    master = f.cell(
        150, 730, 400, 150,
        "Master 组合逻辑\nrequest：内部已有待发送请求\n（非 AXI 接口信号）\nVALID = request AND READY",
        fill="#fff7f7", stroke="#d85b5b", rounded=True, size=19, bold=True,
    )
    slave = f.cell(
        890, 730, 400, 150,
        "Slave 组合逻辑\nspace：内部有可用接收空间\n（非 AXI 接口信号）\nREADY = space AND VALID",
        fill="#fff7f7", stroke="#d85b5b", rounded=True, size=19, bold=True,
    )
    valid_start = f.cell(550, 760, 1, 1, "", fill="none", stroke="none", size=1)
    valid_end = f.cell(889, 760, 1, 1, "", fill="none", stroke="none", size=1)
    ready_start = f.cell(890, 840, 1, 1, "", fill="none", stroke="none", size=1)
    ready_end = f.cell(549, 840, 1, 1, "", fill="none", stroke="none", size=1)
    f.edge(valid_start, valid_end, end=True, color="#b42318")
    f.edge(ready_start, ready_end, end=True, color="#b42318")
    f.text(650, 720, 240, 32, "VALID", size=21, bold=True, color="#b42318")
    f.text(650, 842, 240, 32, "READY", size=21, bold=True, color="#b42318")
    f.text(
        180, 900, 1080, 65,
        "即使 Master 已有待发送请求（request=1）、Slave 有可用接收空间（space=1），\n"
        "若初始 VALID=0、READY=0，两边仍可能一直互相等待，握手无法发生。",
        size=19, bold=True, color="#b42318",
    )

    f.footer("补充图（非原文图）")
    f.save("supplemental-no-combinational-input-output-path")


def supplemental_valid_not_wait_ready():
    """Contrast compliant VALID behavior with the prohibited wait-for-READY dependency."""
    f = Figure("为什么 VALID 不得等待 READY", 950)
    f.frame()
    f.text(70, 25, 1300, 48, "为什么 VALID 不得等待 READY", size=32, bold=True)
    f.text(70, 75, 1300, 35, "避免源端与目的端互相等待", size=22, color=MUTED)

    edges = [340, 560, 780, 1000, 1220]
    for idx, x in enumerate(edges):
        f.text(x - 40, 115, 80, 30, f"T{idx}", size=20, bold=True)
        f.line([(x, 145), (x, 790)], dashed=True, width=2, color="#a7b0bd")

    f.cell(250, 150, 1080, 320, "", fill="#f3fbf5", stroke="#4f9d69", rounded=True)
    f.text(270, 160, 250, 40, "合规", size=25, bold=True, color="#16794a")
    f.text(25, 215, 190, 40, "ACLK", size=22, bold=True, align="right")
    f.text(25, 305, 190, 40, "VALID", size=22, bold=True, align="right")
    f.text(25, 395, 190, 40, "READY", size=22, bold=True, align="right")

    clock = [(270, 275), (340, 275), (340, 225), (450, 225), (450, 275),
             (560, 275), (560, 225), (670, 225), (670, 275),
             (780, 275), (780, 225), (890, 225), (890, 275),
             (1000, 275), (1000, 225), (1110, 225), (1110, 275),
             (1220, 275), (1220, 225), (1310, 225)]
    f.line(clock, width=4)
    f.line([(270, 365), (580, 365), (580, 315), (1020, 315), (1020, 365), (1310, 365)],
           width=4, color="#16794a")
    f.line([(270, 455), (800, 455), (800, 405), (1310, 405)], width=4, color="#2563a6")
    f.cell(470, 285, 230, 45, "已有有效信息", fill="#fff1cc", stroke="#cc8500",
           rounded=True, size=19, bold=True, color="#8a5700")
    f.cell(900, 375, 200, 55, "T3：握手", fill="#dcfce7", stroke="#4f9d69",
           rounded=True, size=20, bold=True, color="#16794a")
    f.text(530, 425, 330, 32, "READY=0 时 VALID 仍保持 HIGH", size=18, bold=True,
           color="#16794a")

    f.cell(250, 500, 1080, 300, "", fill="#fff7f7", stroke="#d85b5b", rounded=True)
    f.text(270, 510, 250, 40, "禁止", size=25, bold=True, color="#b42318")
    f.text(25, 600, 190, 48, "VALID\n（错误）", size=21, bold=True, align="right",
           color="#b42318")
    f.text(25, 700, 190, 40, "READY", size=22, bold=True, align="right")
    f.line([(270, 665), (1310, 665)], width=4, color="#b42318")
    f.line([(270, 735), (1310, 735)], width=4, color="#2563a6")
    f.cell(320, 550, 470, 62, "源端错误：等待 READY=1\n才置位 VALID", fill="#fee2e2",
           stroke="#d85b5b", rounded=True, size=20, bold=True, color="#b42318")
    f.cell(820, 550, 440, 62, "AXI 允许目的端等待 VALID=1\n再置位 READY", fill="#fff0ee",
           stroke="#d85b5b", rounded=True, size=20, bold=True, color="#b42318")
    f.text(1000, 630, 270, 28, "VALID 始终为 LOW", size=18, bold=True, color="#b42318")
    f.text(1000, 700, 270, 28, "READY 始终为 LOW", size=18, bold=True, color="#2563a6")
    f.cell(430, 755, 720, 48, "结果：双方都等对方先置位，握手永远无法开始",
           fill="#fee2e2", stroke="#d85b5b", rounded=True, size=19, bold=True,
           color="#b42318")

    f.footer("补充图（非原文图）")
    f.save("supplemental-valid-must-not-wait-for-ready")


def reset_figure():
    f = Figure("图 A3-1：退出复位 / Figure A3-1 Exit from reset", 560)
    f.frame()
    x0, step = 350, 160
    for idx in (1, 2, 3, 4):
        f.line([(x0 + idx * step, 70), (x0 + idx * step, 380)], dashed=True, width=2, color="#a7b0bd")
    for y, label in [(135, "ACLK"), (250, "ARESETn"), (365, "VALID")]:
        f.text(75, y - 25, 220, 40, label, size=23, bold=True, align="right")
    draw_clock(f, 170, x0=x0, cycles=5, step=step)
    wave(f, 285, [0, 0, 1, 1, 1, 1], x0=x0, step=step)
    wave(f, 400, [0, 0, 0, 1, 1, 1], x0=x0, step=step)
    f.edge(points=[(x0 + 2 * step + 20, 250), (x0 + 2.55 * step, 310),
                   (x0 + 3 * step - 5, 365)], end=True, width=2, color="#596579")
    f.footer()
    f.save("figure-a3-1-exit-from-reset")


def dependency_figures():
    def build(name, title, labels, edges, footnote=None):
        f = Figure(title, 590 if footnote else 520)
        f.frame()
        ids = {}
        for label, x, y in labels:
            ids[label] = f.cell(x, y, 190, 60, label, fill="#ffffff", stroke="none", size=24, bold=True)
        for a, b, both in edges:
            f.edge(ids[a], ids[b], start=both, end=True, width=3)
        if footnote:
            f.text(80, f.height - 150, 1280, 40, footnote, size=21, color=MUTED)
        f.footer()
        f.save(name)

    build(
        "figure-a3-5-read-transaction-handshake-dependencies",
        "图 A3-5：读 transaction 握手依赖关系 / Figure A3-5 Read transaction handshake dependencies",
        [("ARVALID", 180, 120), ("ARREADY", 420, 300), ("RVALID", 760, 120), ("RREADY", 1040, 300)],
        [("ARVALID", "ARREADY", False), ("ARVALID", "RVALID", True),
         ("ARREADY", "RVALID", True), ("RVALID", "RREADY", False)],
    )
    labels = [("AWVALID", 90, 120), ("AWREADY", 210, 330), ("WVALID†", 500, 120),
              ("WREADY", 600, 330), ("BVALID", 960, 120), ("BREADY", 1100, 330)]
    common = [("AWVALID", "AWREADY", False), ("WVALID†", "AWREADY", False),
              ("AWVALID", "WREADY", False), ("WVALID†", "WREADY", False),
              ("WVALID†", "BVALID", True), ("WREADY", "BVALID", True),
              ("BVALID", "BREADY", False)]
    build(
        "figure-a3-6-axi3-write-transaction-handshake-dependencies",
        "图 A3-6：AXI3 写 transaction 握手依赖关系 / Figure A3-6 AXI3 write transaction handshake dependencies", labels, common,
        "† 对 WVALID 置位的依赖关系还要求 WLAST 置位 / Dependencies on WVALID also require WLAST",
    )
    build(
        "figure-a3-7-axi4-axi5-write-transaction-handshake-dependencies",
        "图 A3-7：AXI4 和 AXI5 写 transaction 握手依赖关系 / Figure A3-7 AXI4 and AXI5 write transaction handshake dependencies", labels,
        common + [("AWVALID", "BVALID", True), ("AWREADY", "BVALID", True)],
        "† 对 WVALID 置位的依赖关系还要求 WLAST 置位 / Dependencies on WVALID also require WLAST",
    )


def lane_grid(f, x, y, lane_count, rows, active_sets, row_labels, *, cell_w=120, cell_h=58,
              top_labels=None, bus_label="WDATA", metadata=None):
    total_w = lane_count * cell_w
    if metadata:
        f.text(x - 330, y + 25, 300, len(rows) * cell_h, metadata, size=17, align="right")
    tops = top_labels or [str((lane_count - i) * 8 - 1) for i in range(lane_count)]
    for i, label in enumerate(tops):
        f.text(x + i * cell_w - 30, y - 42, 60, 32, label, size=18)
    for r, values in enumerate(rows):
        for c, value in enumerate(values):
            active = c in active_sets[r]
            f.cell(x + c * cell_w, y + r * cell_h, cell_w, cell_h, value,
                   fill="#ffffff" if active else SHADE, size=20, bold=active)
        f.text(x + total_w + 18, y + r * cell_h, 170, cell_h, row_labels[r], size=19, align="left")
    f.text(x, y + len(rows) * cell_h + 8, total_w, 35, f"{bus_label}[{lane_count*8-1}:0]", size=19, bold=True)


def narrow_figures():
    f = Figure("图 A3-8：8 位传输的窄传输示例 / Figure A3-8 Narrow transfer example with 8-bit transfers", 620)
    f.frame()
    rows = [["", "", "", "D[7:0]"], ["", "", "D[15:8]", ""],
            ["", "D[23:16]", "", ""], ["D[31:24]", "", "", ""],
            ["", "", "", "D[7:0]"]]
    lane_grid(f, 350, 90, 4, rows, [{3}, {2}, {1}, {0}, {3}],
              ["第 1 次 / 1st transfer", "第 2 次 / 2nd transfer", "第 3 次 / 3rd transfer", "第 4 次 / 4th transfer", "第 5 次 / 5th transfer"],
              cell_w=180, top_labels=["31  24", "23  16", "15  8", "7  0"])
    f.footer(); f.save("figure-a3-8-narrow-transfer-8-bit")

    f = Figure("图 A3-9：32 位传输的窄传输示例 / Figure A3-9 Narrow transfer example with 32-bit transfers", 500)
    f.frame()
    rows = [
        ["D[63:56]", "D[55:48]", "D[47:40]", "D[39:32]", "", "", "", ""],
        ["", "", "", "", "D[31:24]", "D[23:16]", "D[15:8]", "D[7:0]"],
        ["D[63:56]", "D[55:48]", "D[47:40]", "D[39:32]", "", "", "", ""],
    ]
    lane_grid(f, 115, 90, 8, rows, [set(range(4)), set(range(4, 8)), set(range(4))],
              ["第 1 次 / 1st", "第 2 次 / 2nd", "第 3 次 / 3rd"], cell_w=140,
              top_labels=["63 56", "55 48", "47 40", "39 32", "31 24", "23 16", "15 8", "7 0"])
    f.footer(); f.save("figure-a3-9-narrow-transfer-32-bit")


def endian_figure(name, title, memory):
    f = Figure(title, 520)
    f.frame()
    x, y, cw = 200, 135, 210
    for i, label in enumerate(["31  24", "23  16", "15  8", "7  0"]):
        f.text(x + i * cw, y - 45, cw, 35, label, size=19)
    for i, value in enumerate(["0x0A", "0x0B", "0x0C", "0x0D"]):
        f.cell(x + i * cw, y, cw, 85, value, fill="#ffffff", size=25, bold=True)
    f.text(x, y + 88, 4 * cw, 40, "寄存器 / Register", size=21)
    mx = 1100
    for i, value in enumerate(memory):
        f.text(mx - 150, y + i * 64, 130, 60, "Addr" if i == 0 else f"Addr+{i}", size=20, align="right")
        f.cell(mx, y + i * 64, 140, 64, value, fill="#ffffff", size=22, bold=True)
    f.text(mx + 150, y + 75, 170, 100, "存储器 / Memory", size=20, bold=True)
    f.footer(); f.save(name)


def mixed_endian():
    f = Figure("图 A3-12：混合端序数据结构示例 / Figure A3-12 Example mixed-endian data structure", 760)
    f.frame()
    x, y, cw, rh = 220, 100, 200, 58
    for i, label in enumerate(["31  24", "23  16", "15  8", "7  0"]):
        f.text(x + i * cw, y - 40, cw, 32, label, size=18)
    # Header: little-endian byte ordering.
    f.cell(x, y, 2*cw, rh, "D0†", fill="#ffffff", size=21, bold=True)
    f.cell(x+2*cw, y, cw, rh, "源 / Source", fill="#ffffff", size=19)
    f.cell(x+3*cw, y, cw, rh, "数据包 / Packet", fill="#ffffff", size=19)
    f.cell(x, y+rh, 2*cw, rh, "校验和 / Checksum", fill="#ffffff", size=19)
    f.cell(x+2*cw, y+rh, 2*cw, rh, "D1†", fill="#ffffff", size=21, bold=True)
    f.cell(x+2*cw, y+2*rh, 2*cw, rh, "数据项 / Data items", fill="#ffffff", size=19)
    f.text(x+4*cw+25, y, 300, 3*rh, "头部，小端字节次序\nHeader, little-endian byte ordering", size=18, align="left")
    # Payload: big-endian byte ordering.
    py = y + 3*rh + 35
    for i in range(4):
        f.cell(x, py+i*rh, 4*cw, rh, "有效载荷 / Payload", fill="#ffffff", size=19)
    f.text(x+4*cw+25, py, 300, 4*rh, "有效载荷，大端字节次序\nPayload, big-endian byte ordering", size=18, align="left")
    f.text(x, py+4*rh+10, 4*cw, 45, "† 16-bit 连续目的字段 / 16-bit continuous Destination field", size=18, align="left")
    f.footer(); f.save("figure-a3-12-mixed-endian-data-structure")


def hex_rows(lanes, starts):
    return [[f"0x{a:02X}" for a in range(s + lanes - 1, s - 1, -1)] for s in starts]


def transfer_figures():
    # Figure A3-13: four 32-bit examples.
    specs = [
        ("地址 / Address：0x00\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：递增 / incrementing\n突发长度 / Burst length：4 次 / transfers",
         hex_rows(4, [0, 4, 8, 12]), [set(range(4))]*4),
        ("地址 / Address：0x01\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：递增 / incrementing\n突发长度 / Burst length：4 次 / transfers",
         hex_rows(4, [0, 4, 8, 12]), [{0,1,2}, set(range(4)), set(range(4)), set(range(4))]),
        ("地址 / Address：0x01\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：递增 / incrementing\n突发长度 / Burst length：5 次 / transfers",
         hex_rows(4, [0, 4, 8, 12, 16]), [{0,1,2}] + [set(range(4))]*4),
        ("地址 / Address：0x07\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：递增 / incrementing\n突发长度 / Burst length：5 次 / transfers",
         hex_rows(4, [4, 8, 12, 16, 20]), [{0}] + [set(range(4))]*4),
    ]
    f = Figure("图 A3-13：32 位总线上的对齐与非对齐传输 / Figure A3-13 Aligned and unaligned transfers on a 32-bit bus", 1560)
    f.frame(); y=80
    for meta, rows, active in specs:
        lane_grid(f, 470, y, 4, rows, active,
                  [f"第 {i+1} 次 / {['1st','2nd','3rd','4th','5th'][i]}" for i in range(len(rows))], cell_w=165,
                  top_labels=["31 24", "23 16", "15 8", "7 0"], metadata=meta)
        y += len(rows)*58 + 105
    f.footer(); f.save("figure-a3-13-aligned-unaligned-32-bit-bus")

    specs64 = [
        ("地址 / Address：0x00\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：递增 / incrementing\n突发长度 / Burst length：4 次 / transfers", [0,0,8,8],
         [set(range(4,8)), set(range(0,4)), set(range(4,8)), set(range(0,4))]),
        ("地址 / Address：0x07\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：递增 / incrementing\n突发长度 / Burst length：4 次 / transfers", [0,8,8,16],
         [{0}, set(range(4,8)), set(range(0,4)), set(range(4,8))]),
        ("地址 / Address：0x07\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：递增 / incrementing\n突发长度 / Burst length：5 次 / transfers", [0,8,8,16,16],
         [{0}, set(range(4,8)), set(range(0,4)), set(range(4,8)), set(range(0,4))]),
    ]
    f = Figure("图 A3-14：64 位总线上的对齐与非对齐传输 / Figure A3-14 Aligned and unaligned transfers on a 64-bit bus", 1340)
    f.frame(); y=80
    for meta, starts, active in specs64:
        rows=hex_rows(8, starts)
        lane_grid(f, 300, y, 8, rows, active,
                  [f"第 {i+1} 次 / {['1st','2nd','3rd','4th','5th'][i]}" for i in range(len(rows))], cell_w=120,
                  top_labels=["63 56", "55 48", "47 40", "39 32", "31 24", "23 16", "15 8", "7 0"], metadata=meta)
        y += len(rows)*58 + 115
    f.footer(); f.save("figure-a3-14-aligned-unaligned-64-bit-bus")

    f = Figure("图 A3-15：64 位总线上的对齐回绕传输 / Figure A3-15 Aligned wrapping transfers on a 64-bit bus", 650)
    f.frame()
    rows=hex_rows(8,[0,8,8,0])
    active=[set(range(0,4)), set(range(4,8)), set(range(0,4)), set(range(4,8))]
    lane_grid(f, 300, 110, 8, rows, active,
              [f"第 {i+1} 次 / {['1st','2nd','3rd','4th'][i]}" for i in range(4)], cell_w=120,
              top_labels=["63 56", "55 48", "47 40", "39 32", "31 24", "23 16", "15 8", "7 0"],
              metadata="地址 / Address：0x04\n传输大小 / Transfer size：32-bit\n突发类型 / Burst type：回绕 / wrapping\n突发长度 / Burst length：4 次 / transfers")
    f.footer(); f.save("figure-a3-15-aligned-wrapping-64-bit-bus")


def main():
    make_table(
        "table-a3-1-transaction-channel-handshake-pairs", "表 A3-1：Transaction 通道握手信号对 / Table A3-1 Transaction channel handshake pairs",
        ["Transaction 通道 / Transaction channel", "握手信号对 / Handshake pair"],
        [["写地址通道 / Write address channel", "AWVALID, AWREADY"], ["写数据通道 / Write data channel", "WVALID, WREADY"],
         ["写响应通道 / Write response channel", "BVALID, BREADY"], ["读地址通道 / Read address channel", "ARVALID, ARREADY"],
         ["读数据通道 / Read data channel", "RVALID, RREADY"]], widths=[660,660], row_h=76,
    )
    make_table(
        "table-a3-2-burst-size-encoding", "表 A3-2：突发大小编码 / Table A3-2 Burst size encoding",
        ["AxSIZE[2:0]", "每次传输的字节数 / Bytes in transfer"],
        [[f"0b{i:03b}", str(2**i)] for i in range(8)], widths=[660,660], row_h=62,
    )
    make_table(
        "table-a3-3-burst-type-encoding", "表 A3-3：突发类型编码 / Table A3-3 Burst type encoding",
        ["AxBURST[1:0]", "突发类型 / Burst type"],
        [["0b00", "FIXED"], ["0b01", "INCR"], ["0b10", "WRAP"], ["0b11", "保留 / Reserved"]],
        widths=[660,660], row_h=70,
    )
    make_table(
        "table-a3-4-regular-transactions-only-interoperability", "表 A3-4：Regular_Transactions_Only 互操作性 / Table A3-4 Regular_Transactions_Only Interoperability",
        ["", "Slave：False", "Slave：True"],
        [["Master：False", "兼容 / Compatible", "不兼容 / Not compatible\n如果 Master 发出非 Regular transaction，\n可能发生数据损坏或死锁。\nIf the master issues a transaction that is not Regular,\ndata corruption or deadlock might occur."],
         ["Master：True", "兼容 / Compatible", "兼容 / Compatible"]], widths=[240,540,540], row_h=175,
    )
    make_table(
        "table-a3-5-rresp-bresp-encoding", "表 A3-5：RRESP 和 BRESP 编码 / Table A3-5 RRESP and BRESP encoding",
        ["RRESP[1:0]\nBRESP[1:0]", "响应 / Response"],
        [["0b00", "OKAY"], ["0b01", "EXOKAY"], ["0b10", "SLVERR"], ["0b11", "DECERR"]],
        widths=[660,660], row_h=70,
    )
    reset_figure()
    supplemental_no_combinational_path()
    supplemental_valid_not_wait_ready()
    timing("figure-a3-2-valid-before-ready-handshake", "图 A3-2：VALID 先于 READY 的握手 / Figure A3-2 VALID before READY handshake",
           [("T1",1),("T2",2),("T3",3)], [0,1,1,1,0,0], [0,0,1,1,0,0], 1, 4)
    timing("figure-a3-3-ready-before-valid-handshake", "图 A3-3：READY 先于 VALID 的握手 / Figure A3-3 READY before VALID handshake",
           [("T1",1),("T2",2),("T3",3)], [0,0,1,1,0,0], [0,1,1,1,0,0], 2, 4)
    timing("figure-a3-4-valid-with-ready-handshake", "图 A3-4：VALID 与 READY 同时握手 / Figure A3-4 VALID with READY handshake",
           [("T1",1),("T2",2)], [0,1,1,0,0,0], [0,1,1,0,0,0], 1, 3)
    dependency_figures()
    narrow_figures()
    endian_figure("figure-a3-10-big-endian-byte-invariant", "图 A3-10：大端字节不变数据结构示例 / Figure A3-10 Example big-endian byte-invariant data structure",
                  ["0x0A", "0x0B", "0x0C", "0x0D"])
    endian_figure("figure-a3-11-little-endian-byte-invariant", "图 A3-11：小端字节不变数据结构示例 / Figure A3-11 Example little-endian byte-invariant data structure",
                  ["0x0D", "0x0C", "0x0B", "0x0A"])
    mixed_endian()
    transfer_figures()


if __name__ == "__main__":
    main()
