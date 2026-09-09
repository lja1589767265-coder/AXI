"""Redraw the three figures from Chapter A1 as editable draw.io files."""
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "image" / "axi-a1"
DRAWIO = Path(r"C:\Program Files\draw.io\draw.io.exe")
WIDTH = 1440
FONT = "Microsoft YaHei"
INK = "#172b42"
GRAY = "#697586"
LINE = "#27364a"
PALE = "#f3f5f7"
DATA = "#d9dee5"
BLUE = "#2463ad"
GREEN = "#158060"


class Figure:
    def __init__(self, title: str, height: int, title_size: int = 40):
        self.height = height
        self.doc = ET.Element("mxfile", host="app.diagrams.net")
        diagram = ET.SubElement(self.doc, "diagram", name=title)
        model = ET.SubElement(
            diagram,
            "mxGraphModel",
            page="1",
            pageWidth=str(WIDTH),
            pageHeight=str(height),
        )
        self.root = ET.SubElement(model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.counter = 2
        self.box(0, 0, WIDTH, height, "", fill="#ffffff", stroke="none")
        self.text(30, 18, 1380, 62, title, size=title_size, bold=True, align="center")

    def cell(self, **kwargs):
        cell = ET.SubElement(
            self.root, "mxCell", id=str(self.counter), parent="1", **kwargs
        )
        self.counter += 1
        return cell

    def box(
        self,
        x,
        y,
        width,
        height,
        label,
        fill="#ffffff",
        stroke=LINE,
        size=30,
        color=INK,
        bold=False,
        align="center",
    ):
        cell = self.cell(
            value=label,
            vertex="1",
            style=(
                f"rounded=0;whiteSpace=wrap;html=0;fontFamily={FONT};"
                f"fontSize={size};fontColor={color};fontStyle={int(bold)};"
                f"fillColor={fill};strokeColor={stroke};strokeWidth=2;"
                f"align={align};verticalAlign=middle;spacing=8;"
            ),
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(x),
            y=str(y),
            width=str(width),
            height=str(height),
            **{"as": "geometry"},
        )

    def text(self, x, y, width, height, label, size=30, color=INK, bold=False, align="left"):
        self.box(
            x,
            y,
            width,
            height,
            label,
            fill="none",
            stroke="none",
            size=size,
            color=color,
            bold=bold,
            align=align,
        )

    def line(self, x1, y1, x2, y2, arrow=False, width=2):
        self.polyline([(x1, y1), (x2, y2)], arrow=arrow, width=width)

    def polyline(self, points, color=LINE, dashed=False, arrow=False, width=2):
        cell = self.cell(
            edge="1",
            style=(
                f"endArrow={'block' if arrow else 'none'};endFill=1;"
                f"startArrow=none;strokeWidth={width};strokeColor={color};"
                f"dashed={int(dashed)};rounded=0;"
            ),
        )
        geometry = ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
        ET.SubElement(geometry, "mxPoint", x=str(points[0][0]), y=str(points[0][1]), **{"as": "sourcePoint"})
        ET.SubElement(geometry, "mxPoint", x=str(points[-1][0]), y=str(points[-1][1]), **{"as": "targetPoint"})
        if len(points) > 2:
            array = ET.SubElement(geometry, "Array", **{"as": "points"})
            for x, y in points[1:-1]:
                ET.SubElement(array, "mxPoint", x=str(x), y=str(y))

    def footer(self, label="根据原图双语重绘 / Bilingual redraw based on original figure"):
        self.text(
            30,
            self.height - 52,
            1380,
            34,
            label,
            size=24,
            color=GRAY,
            align="center",
        )

    def save(self, name: str, footer_text="根据原图双语重绘 / Bilingual redraw based on original figure"):
        OUT.mkdir(parents=True, exist_ok=True)
        self.footer(footer_text)
        source = OUT / f"{name}.drawio"
        ET.ElementTree(self.doc).write(source, encoding="utf-8", xml_declaration=True)
        target = source.with_suffix(".png")
        if not DRAWIO.exists():
            raise FileNotFoundError(f"draw.io CLI not found: {DRAWIO}")
        result = subprocess.run(
            [
                str(DRAWIO),
                "--export",
                "--format",
                "png",
                "--width",
                str(WIDTH),
                "--output",
                str(target),
                str(source),
            ],
            capture_output=True,
            text=True,
            timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode or not target.exists():
            raise RuntimeError(result.stdout + result.stderr)
        print(source)
        print(target)


def channel_base(title: str, height: int = 820, interface_height: int = 540):
    fig = Figure(title, height)
    fig.box(80, 140, 150, interface_height, "主设备接口\nMaster interface", fill=PALE, size=23, bold=True)
    fig.box(1210, 140, 150, interface_height, "从设备接口\nSlave interface", fill=PALE, size=23, bold=True)
    return fig


def draw_write():
    fig = channel_base(
        "图 A1-1：写通道架构 / Figure A1-1 Channel architecture of writes",
        height=860,
        interface_height=580,
    )
    fig.text(440, 112, 560, 46, "写地址通道 / Write address channel", size=25, bold=True, align="center")
    fig.box(230, 165, 220, 108, "地址和控制\nAddress and control", fill=DATA, size=23)
    fig.line(450, 219, 1210, 219)
    fig.line(470, 248, 600, 248, arrow=True, width=3)

    fig.text(440, 292, 560, 46, "写数据通道 / Write data channel", size=25, bold=True, align="center")
    fig.line(230, 345, 1210, 345)
    fig.line(230, 495, 1210, 495)
    x0, cell_w = 450, 170
    for index in range(4):
        fig.box(x0 + index * cell_w, 345, cell_w, 150, "写数据\nWrite data", fill=DATA, size=23)
        fig.line(x0 + index * cell_w + 35, 520, x0 + index * cell_w + 135, 520, arrow=True, width=3)

    fig.text(440, 570, 560, 46, "写响应通道 / Write response channel", size=25, bold=True, align="center")
    fig.line(230, 630, 1210, 630)
    fig.line(230, 720, 1210, 720)
    fig.box(1030, 630, 180, 90, "写响应\nWrite response", fill=DATA, size=23)
    fig.line(1170, 745, 1030, 745, arrow=True, width=3)
    fig.save("figure-a1-1-channel-architecture-writes")


def draw_read():
    fig = channel_base(
        "图 A1-2：读通道架构 / Figure A1-2 Channel architecture of reads",
        height=700,
        interface_height=430,
    )

    fig.text(440, 112, 560, 46, "读地址通道 / Read address channel", size=25, bold=True, align="center")
    fig.box(230, 165, 220, 108, "地址和控制\nAddress and control", fill=DATA, size=23)
    fig.line(450, 219, 1210, 219)
    fig.line(470, 248, 600, 248, arrow=True, width=3)

    fig.text(440, 310, 560, 46, "读数据通道 / Read data channel", size=25, bold=True, align="center")
    fig.line(230, 365, 1210, 365)
    fig.line(230, 515, 1210, 515)
    x0, cell_w = 450, 170
    for index in range(4):
        fig.box(x0 + index * cell_w, 365, cell_w, 150, "读数据\nRead data", fill=DATA, size=23)
        fig.line(x0 + index * cell_w + 135, 540, x0 + index * cell_w + 35, 540, arrow=True, width=3)
    fig.save("figure-a1-2-channel-architecture-reads")


def draw_interconnect():
    fig = Figure("图 A1-3：接口与互连 / Figure A1-3 Interface and interconnect", 760)
    master_x = [260, 580, 900]
    for index, x in enumerate(master_x, start=1):
        fig.box(x, 135, 220, 80, f"主设备 {index}\nMaster {index}", fill=PALE, size=23, bold=True)
        fig.line(x + 110, 215, x + 110, 315)

    fig.box(150, 315, 1140, 92, "互连 / Interconnect", fill=DATA, size=25, bold=True)

    slave_x = [110, 400, 690, 980]
    for index, x in enumerate(slave_x, start=1):
        fig.line(x + 110, 407, x + 110, 520)
        fig.box(x, 520, 220, 80, f"从设备 {index}\nSlave {index}", fill=PALE, size=23, bold=True)

    fig.text(5, 350, 140, 66, "接口\nInterface", size=23, bold=True, align="right")
    fig.line(135, 383, 205, 383, arrow=True, width=3)
    fig.text(1110, 220, 180, 66, "接口\nInterface", size=23, bold=True, align="left")
    fig.line(1100, 252, 1010, 252, arrow=True, width=3)
    fig.save("figure-a1-3-interface-interconnect")


def draw_channel_signals():
    fig = Figure("补充图：单个 AXI 通道的信号组成", 680)
    fig.text(30, 88, 1380, 42, "补充图（非原文图）", size=25, color=GRAY, align="center")

    fig.box(70, 175, 220, 380, "信息源", fill=PALE, size=32, bold=True)
    fig.box(1150, 175, 220, 380, "目的端", fill=PALE, size=32, bold=True)

    fig.text(480, 180, 480, 48, "信息信号", size=30, color=BLUE, bold=True, align="center")
    fig.polyline([(290, 245), (1150, 245)], color=BLUE, arrow=True, width=4)

    fig.text(480, 300, 480, 48, "VALID", size=30, color=BLUE, bold=True, align="center")
    fig.polyline([(290, 365), (1150, 365)], color=BLUE, arrow=True, width=4)

    fig.text(480, 420, 480, 48, "READY", size=30, color=GREEN, bold=True, align="center")
    fig.polyline([(1150, 485), (290, 485)], color=GREEN, arrow=True, width=4)

    fig.save("supplemental-channel-signals", footer_text="补充图（非原文图）")


def draw_timing_bit(fig, y, values, edges, left, right, color):
    high, low = y, y + 38
    points = [(left, high if values[0] else low)]
    for index in range(1, len(values)):
        if values[index] != values[index - 1]:
            x = edges[index - 1] + 18
            points.extend(
                [
                    (x, high if values[index - 1] else low),
                    (x + 12, high if values[index] else low),
                ]
            )
    points.append((right, high if values[-1] else low))
    fig.polyline(points, color=color, width=4)


def draw_timing_bus(fig, y, values, edges, left, right, color):
    starts = [0]
    starts.extend(index for index in range(1, len(values)) if values[index] != values[index - 1])
    starts.append(len(values))
    for start, end in zip(starts, starts[1:]):
        x1 = left if start == 0 else edges[start - 1] + 22
        x2 = right if end == len(values) else edges[end - 1] + 22
        value = values[start]
        if value == "—":
            fig.line(x1, y + 20, x2, y + 20, width=2)
            continue
        fig.polyline(
            [
                (x1, y + 20),
                (x1 + 10, y),
                (x2 - 10, y),
                (x2, y + 20),
                (x2 - 10, y + 40),
                (x1 + 10, y + 40),
                (x1, y + 20),
            ],
            color=color,
            width=3,
        )
        fig.text(x1 + 8, y - 5, x2 - x1 - 16, 50, value, size=27, color=color, align="center")


def draw_read_data_timing():
    fig = Figure("补充时序图：读数据通道", 1010)
    fig.text(30, 88, 1380, 42, "补充图（非原文图）", size=25, color=GRAY, align="center")
    fig.text(30, 128, 1380, 42, "蓝：从设备驱动    绿：主设备驱动    虚线：ACLK 采样上升沿", size=24, color=GRAY, align="center")

    left, right = 300, 1390
    edges = [400, 620, 840, 1060, 1280]
    top, pitch = 235, 100
    bottom = top + pitch * 6

    for index, x in enumerate(edges, start=1):
        fig.text(x - 42, top - 58, 84, 40, f"T{index}", size=25, bold=True, align="center")
        fig.polyline([(x, top - 8), (x, bottom + 12)], color="#dce3eb", dashed=True, width=2)

    fig.text(30, top - 4, 240, 50, "ACLK", size=27, bold=True)
    clock = [(left, top + 38)]
    half = 76
    for x in edges:
        clock.extend([(x, top + 38), (x, top), (x + half, top), (x + half, top + 38)])
    clock.append((right, top + 38))
    fig.polyline(clock, color=GRAY, width=3)

    rows = [
        ("RVALID", [0, 1, 0, 0, 0], "bit", BLUE),
        ("RREADY", [1, 1, 1, 1, 1], "bit", GREEN),
        ("RDATA", ["—", "D0", "—", "—", "—"], "bus", BLUE),
        ("RRESP", ["—", "读响应", "—", "—", "—"], "bus", BLUE),
        ("RLAST", [0, 1, 0, 0, 0], "bit", BLUE),
    ]
    for row_index, (label, values, kind, color) in enumerate(rows, start=1):
        y = top + pitch * row_index
        fig.text(30, y - 4, 240, 50, label, size=27, color=color, bold=True)
        if kind == "bit":
            draw_timing_bit(fig, y, values, edges, left, right, color)
        else:
            draw_timing_bus(fig, y, values, edges, left, right, color)

    rdata_y = top + pitch * 3
    fig.box(
        660,
        rdata_y - 10,
        730,
        60,
        "← 总线宽度：8/16/32/64/128/256/512/1024 位",
        fill="#ffffff",
        stroke="none",
        size=22,
        color=BLUE,
        bold=True,
        align="left",
    )

    fig.polyline([(620, top - 8), (620, bottom + 12)], color=GREEN, dashed=True, width=4)
    fig.box(505, 842, 230, 52, "T2：传输", fill="#edf7ed", stroke=GREEN, size=25, color=GREEN, bold=True)
    fig.save("supplemental-read-data-channel-timing", footer_text="补充图（非原文图）")


def draw_write_data_timing():
    fig = Figure("补充时序图：写数据通道", 1010)
    fig.text(30, 88, 1380, 42, "补充图（非原文图）", size=25, color=GRAY, align="center")
    fig.text(30, 128, 1380, 42, "蓝：主设备驱动    绿：从设备驱动    虚线：ACLK 采样上升沿", size=24, color=GRAY, align="center")

    left, right = 300, 1390
    edges = [400, 620, 840, 1060, 1280]
    top, pitch = 235, 100
    bottom = top + pitch * 6

    for index, x in enumerate(edges, start=1):
        fig.text(x - 42, top - 58, 84, 40, f"T{index}", size=25, bold=True, align="center")
        fig.polyline([(x, top - 8), (x, bottom + 12)], color="#dce3eb", dashed=True, width=2)

    fig.text(30, top - 4, 240, 50, "ACLK", size=27, bold=True)
    clock = [(left, top + 38)]
    half = 76
    for x in edges:
        clock.extend([(x, top + 38), (x, top), (x + half, top), (x + half, top + 38)])
    clock.append((right, top + 38))
    fig.polyline(clock, color=GRAY, width=3)

    rows = [
        ("WVALID", [0, 1, 0, 0, 0], "bit", BLUE),
        ("WREADY", [1, 1, 1, 1, 1], "bit", GREEN),
        ("WDATA", ["—", "D0", "—", "—", "—"], "bus", BLUE),
        ("WSTRB", ["—", "字节有效", "—", "—", "—"], "bus", BLUE),
        ("WLAST", [0, 1, 0, 0, 0], "bit", BLUE),
    ]
    for row_index, (label, values, kind, color) in enumerate(rows, start=1):
        y = top + pitch * row_index
        fig.text(30, y - 4, 240, 50, label, size=27, color=color, bold=True)
        if kind == "bit":
            draw_timing_bit(fig, y, values, edges, left, right, color)
        else:
            draw_timing_bus(fig, y, values, edges, left, right, color)

    wdata_y = top + pitch * 3
    fig.box(
        660,
        wdata_y - 10,
        730,
        60,
        "← 总线宽度：8/16/32/64/128/256/512/1024 位",
        fill="#ffffff",
        stroke="none",
        size=22,
        color=BLUE,
        bold=True,
        align="left",
    )
    wstrb_y = top + pitch * 4
    fig.box(
        660,
        wstrb_y - 10,
        730,
        60,
        "← 每 8 位数据对应 1 个字节选通信号",
        fill="#ffffff",
        stroke="none",
        size=22,
        color=BLUE,
        bold=True,
        align="left",
    )

    fig.polyline([(620, top - 8), (620, bottom + 12)], color=GREEN, dashed=True, width=4)
    fig.box(505, 842, 230, 52, "T2：传输", fill="#edf7ed", stroke=GREEN, size=25, color=GREEN, bold=True)
    fig.save("supplemental-write-data-channel-timing", footer_text="补充图（非原文图）")


def draw_write_response_timing():
    fig = Figure("补充时序图：4 拍写事务只产生 1 次写响应", 1220, title_size=36)
    fig.text(
        30,
        82,
        1380,
        42,
        "AW 地址握手已在此前完成；为突出数据拍与写响应的关系，本图省略 AW 通道",
        size=23,
        color=GRAY,
        align="center",
    )
    fig.text(30, 124, 1380, 42, "蓝：主设备驱动    绿：从设备驱动    虚线：完成握手的 ACLK 上升沿", size=24, color=GRAY, align="center")

    left, right = 280, 1390
    edges = [350, 540, 730, 920, 1110, 1300]
    top, pitch = 225, 92
    bottom = top + pitch * 7

    for index, x in enumerate(edges, start=1):
        fig.text(x - 38, top - 54, 76, 36, f"T{index}", size=23, bold=True, align="center")
        fig.polyline([(x, top - 8), (x, bottom + 12)], color="#dce3eb", dashed=True, width=2)

    fig.text(30, top - 4, 210, 46, "ACLK", size=25, bold=True)
    clock = [(left, top + 36)]
    half = 64
    for x in edges:
        clock.extend([(x, top + 36), (x, top), (x + half, top), (x + half, top + 36)])
    clock.append((right, top + 36))
    fig.polyline(clock, color=GRAY, width=3)

    rows = [
        ("WVALID", [1, 1, 1, 1, 0, 0], "bit", BLUE),
        ("WREADY", [1, 1, 1, 1, 1, 1], "bit", GREEN),
        ("WDATA", ["W1", "W2", "W3", "W4", "—", "—"], "bus", BLUE),
        ("WLAST", [0, 0, 0, 1, 0, 0], "bit", BLUE),
        ("BVALID", [0, 0, 0, 0, 1, 0], "bit", GREEN),
        ("BREADY", [1, 1, 1, 1, 1, 1], "bit", BLUE),
        ("BRESP", ["—", "—", "—", "—", "OKAY", "—"], "bus", GREEN),
    ]
    for row_index, (label, values, kind, color) in enumerate(rows, start=1):
        y = top + pitch * row_index
        fig.text(30, y - 4, 210, 46, label, size=25, color=color, bold=True)
        if kind == "bit":
            draw_timing_bit(fig, y, values, edges, left, right, color)
        else:
            draw_timing_bus(fig, y, values, edges, left, right, color)

    for x in edges[:4]:
        fig.polyline([(x, top - 8), (x, bottom + 12)], color=BLUE, dashed=True, width=3)
    fig.polyline([(edges[4], top - 8), (edges[4], bottom + 12)], color=GREEN, dashed=True, width=4)

    beat_labels = ["T1：W1", "T2：W2", "T3：W3", "T4：W4 + WLAST"]
    for x, label in zip(edges[:4], beat_labels):
        width = 180 if "WLAST" in label else 140
        fig.box(x - width / 2, 910, width, 50, label, fill="#eef4fb", stroke=BLUE, size=21, color=BLUE, bold=True)
    fig.box(1020, 910, 180, 50, "T5：1 次 B 响应", fill="#edf7ed", stroke=GREEN, size=21, color=GREEN, bold=True)
    fig.text(
        300,
        976,
        900,
        46,
        "W1～W4 是同一笔写事务的 4 个数据拍；响应针对完整事务，而不是每个数据拍",
        size=23,
        color=INK,
        bold=True,
        align="center",
    )
    fig.save("supplemental-write-response-channel-timing", footer_text="补充图（非原文图）")


def draw_buffered_write_timing():
    fig = Figure("补充时序案例：上一笔未响应，下一笔写事务仍可推进", 1360, title_size=36)
    fig.text(30, 82, 1380, 42, "案例假设：两笔均为单拍写，AWREADY、WREADY、BREADY 始终为高", size=24, color=GRAY, align="center")
    fig.text(30, 122, 1380, 42, "蓝：主设备驱动    绿：从设备驱动    虚线：完成握手的 ACLK 上升沿", size=24, color=GRAY, align="center")

    left, right = 280, 1390
    edges = [350, 510, 670, 830, 990, 1150, 1310]
    top, pitch = 225, 86
    bottom = top + pitch * 10

    for index, x in enumerate(edges, start=1):
        fig.text(x - 38, top - 54, 76, 36, f"T{index}", size=23, bold=True, align="center")
        fig.polyline([(x, top - 8), (x, bottom + 8)], color="#dce3eb", dashed=True, width=2)

    fig.text(30, top - 4, 210, 46, "ACLK", size=25, bold=True)
    clock = [(left, top + 36)]
    half = 54
    for x in edges:
        clock.extend([(x, top + 36), (x, top), (x + half, top), (x + half, top + 36)])
    clock.append((right, top + 36))
    fig.polyline(clock, color=GRAY, width=3)

    rows = [
        ("AWVALID", [1, 1, 0, 0, 0, 0, 0], "bit", BLUE),
        ("AWREADY", [1, 1, 1, 1, 1, 1, 1], "bit", GREEN),
        ("AWADDR", ["A1", "A2", "—", "—", "—", "—", "—"], "bus", BLUE),
        ("WVALID", [1, 1, 0, 0, 0, 0, 0], "bit", BLUE),
        ("WREADY", [1, 1, 1, 1, 1, 1, 1], "bit", GREEN),
        ("WDATA", ["D1", "D2", "—", "—", "—", "—", "—"], "bus", BLUE),
        ("WLAST", [1, 1, 0, 0, 0, 0, 0], "bit", BLUE),
        ("BVALID", [0, 0, 0, 0, 1, 1, 0], "bit", GREEN),
        ("BREADY", [1, 1, 1, 1, 1, 1, 1], "bit", BLUE),
        ("BRESP", ["—", "—", "—", "—", "B1: OKAY", "B2: OKAY", "—"], "bus", GREEN),
    ]
    for row_index, (label, values, kind, color) in enumerate(rows, start=1):
        y = top + pitch * row_index
        fig.text(30, y - 4, 210, 46, label, size=25, color=color, bold=True)
        if kind == "bit":
            draw_timing_bit(fig, y, values, edges, left, right, color)
        else:
            draw_timing_bus(fig, y, values, edges, left, right, color)

    for x in edges[:2]:
        fig.polyline([(x, top - 8), (x, bottom + 8)], color=BLUE, dashed=True, width=3)
    for x in edges[4:6]:
        fig.polyline([(x, top - 8), (x, bottom + 8)], color=GREEN, dashed=True, width=3)

    fig.box(270, 1138, 190, 54, "T1：写 1 请求", fill="#eef4fb", stroke=BLUE, size=23, color=BLUE, bold=True)
    fig.box(470, 1138, 190, 54, "T2：写 2 请求", fill="#eef4fb", stroke=BLUE, size=23, color=BLUE, bold=True)
    fig.box(925, 1138, 190, 54, "T5：写 1 响应", fill="#edf7ed", stroke=GREEN, size=23, color=GREEN, bold=True)
    fig.box(1125, 1138, 190, 54, "T6：写 2 响应", fill="#edf7ed", stroke=GREEN, size=23, color=GREEN, bold=True)
    fig.text(
        420,
        1200,
        740,
        48,
        "T2 时写 1 的 B 响应尚未返回，但写 2 已经完成 AW/W 握手",
        size=24,
        color=INK,
        bold=True,
        align="center",
    )
    fig.save("supplemental-buffered-write-timing", footer_text="补充图（非原文图）")


def draw_register_slice_structure():
    fig = Figure("补充图：寄存器切片是什么，为什么要加？", 1080, title_size=38)
    fig.text(
        30,
        86,
        1380,
        42,
        "示意一条 AXI 通道的流水分段；不表示具体 RTL 微架构",
        size=24,
        color=GRAY,
        align="center",
    )

    fig.text(55, 142, 1330, 46, "① 单个 AXI 通道经过 Register Slice", size=28, bold=True)
    fig.box(60, 205, 230, 230, "主设备", fill=PALE, size=28, bold=True)
    fig.box(
        510,
        185,
        420,
        270,
        "寄存器切片\nRegister Slice\n\n暂存通道信息\n保持 VALID/READY 握手语义",
        fill="#eef4fb",
        stroke=BLUE,
        size=25,
        color=INK,
        bold=True,
    )
    fig.box(1150, 205, 230, 230, "从设备或互连", fill=PALE, size=25, bold=True)

    fig.text(295, 205, 210, 40, "通道信息 + VALID", size=22, color=BLUE, bold=True, align="center")
    fig.polyline([(290, 270), (510, 270)], color=BLUE, arrow=True, width=4)
    fig.text(935, 205, 210, 40, "通道信息 + VALID", size=22, color=BLUE, bold=True, align="center")
    fig.polyline([(930, 270), (1150, 270)], color=BLUE, arrow=True, width=4)

    fig.text(295, 372, 210, 40, "READY", size=22, color=GREEN, bold=True, align="center")
    fig.polyline([(510, 360), (290, 360)], color=GREEN, arrow=True, width=4)
    fig.text(935, 372, 210, 40, "READY", size=22, color=GREEN, bold=True, align="center")
    fig.polyline([(1150, 360), (930, 360)], color=GREEN, arrow=True, width=4)

    fig.line(55, 500, 1385, 500, width=2)
    fig.text(55, 525, 1330, 46, "② 为什么要加：把难以收敛的长路径拆短（示例时钟周期：1 ns）", size=27, bold=True)

    fig.text(55, 610, 150, 50, "无切片", size=25, bold=True)
    fig.box(205, 595, 190, 78, "发送寄存器", fill=PALE, size=23, bold=True)
    fig.polyline([(395, 634), (1110, 634)], color=LINE, arrow=True, width=4)
    fig.text(500, 580, 510, 42, "组合延迟 1.3 ns > 1 ns：时序违例", size=22, color=GRAY, bold=True, align="center")
    fig.box(1110, 595, 190, 78, "接收寄存器", fill=PALE, size=23, bold=True)

    fig.text(55, 765, 150, 50, "有切片", size=25, color=BLUE, bold=True)
    fig.box(205, 750, 190, 78, "发送寄存器", fill=PALE, size=23, bold=True)
    fig.polyline([(395, 789), (620, 789)], color=BLUE, arrow=True, width=4)
    fig.text(405, 735, 200, 42, "0.7 ns < 1 ns", size=22, color=BLUE, bold=True, align="center")
    fig.box(620, 735, 240, 108, "寄存器切片\nRegister Slice", fill="#eef4fb", stroke=BLUE, size=22, color=BLUE, bold=True)
    fig.polyline([(860, 789), (1110, 789)], color=BLUE, arrow=True, width=4)
    fig.text(875, 735, 220, 42, "0.6 ns < 1 ns", size=22, color=BLUE, bold=True, align="center")
    fig.box(1110, 750, 190, 78, "接收寄存器", fill=PALE, size=23, bold=True)

    fig.box(
        210,
        885,
        480,
        70,
        "收益：两段都小于 1 ns，更易满足时序",
        fill="#eef4fb",
        stroke=BLUE,
        size=22,
        color=BLUE,
        bold=True,
    )
    fig.box(
        750,
        885,
        480,
        70,
        "代价：增加一个周期延迟和少量控制逻辑",
        fill="#edf7ed",
        stroke=GREEN,
        size=22,
        color=GREEN,
        bold=True,
    )
    fig.save("supplemental-register-slice-structure", footer_text="补充图（非原文图）")


def main():
    draw_write()
    draw_read()
    draw_interconnect()
    draw_channel_signals()
    draw_read_data_timing()
    draw_write_data_timing()
    draw_write_response_timing()
    draw_buffered_write_timing()
    draw_register_slice_structure()


if __name__ == "__main__":
    main()
