"""Build the two editable A5.1 AXI transaction-ID timing diagrams.

Samples are the values observed immediately before each Tn rising edge.
Signal changes are drawn just after the preceding edge, matching A3 v2.
"""
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "image" / "axi-a5"
DRAWIO = Path(r"C:\Program Files\draw.io\draw.io.exe")
WIDTH = 1440
FONT = "Microsoft YaHei"

INK = "#172b42"
NEUTRAL = "#697586"
GRID = "#dce3eb"
BLUE = "#123a91"
GREEN = "#176622"
PURPLE = "#743c98"
PALE_BLUE = "#edf4ff"
PALE_GREEN = "#edf7ed"
PALE_PURPLE = "#f3eef9"


class Figure:
    def __init__(self, title: str, height: int):
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
        self.text(30, 18, 1380, 70, title, size=44, bold=True)

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
        stroke="#111111",
        size=32,
        color=INK,
        rounded=False,
        bold=False,
        align="center",
    ):
        cell = self.cell(
            value=label,
            vertex="1",
            style=(
                f"rounded={int(rounded)};arcSize=10;whiteSpace=wrap;html=0;"
                f"fontFamily={FONT};fontSize={size};fontColor={color};"
                f"fontStyle={int(bold)};fillColor={fill};strokeColor={stroke};"
                f"strokeWidth=2;align={align};verticalAlign=middle;spacing=8;"
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

    def text(
        self,
        x,
        y,
        width,
        height,
        label,
        size=32,
        color=INK,
        bold=False,
        align="left",
    ):
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

    def line(self, points, color="#111111", dashed=False, arrow=False, width=3):
        cell = self.cell(
            edge="1",
            style=(
                f'endArrow={"block" if arrow else "none"};endFill=1;'
                f"startArrow=none;rounded=0;strokeWidth={width};"
                f"strokeColor={color};dashed={int(dashed)};"
            ),
        )
        geometry = ET.SubElement(
            cell, "mxGeometry", relative="1", **{"as": "geometry"}
        )
        for point, role in ((points[0], "sourcePoint"), (points[-1], "targetPoint")):
            ET.SubElement(
                geometry,
                "mxPoint",
                x=str(point[0]),
                y=str(point[1]),
                **{"as": role},
            )
        if len(points) > 2:
            array = ET.SubElement(geometry, "Array", **{"as": "points"})
            for x, y in points[1:-1]:
                ET.SubElement(array, "mxPoint", x=str(x), y=str(y))

    def save(self, name: str):
        OUT.mkdir(parents=True, exist_ok=True)
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


def draw_bit(fig, y, values, edges, left, right, color):
    high, low = y, y + 36
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
    fig.line(points, color=color, width=3)


def draw_bus(fig, y, values, edges, left, right, color):
    starts = [0]
    starts.extend(
        index
        for index in range(1, len(values))
        if values[index] != values[index - 1]
    )
    starts.append(len(values))
    for start, end in zip(starts, starts[1:]):
        x1 = left if start == 0 else edges[start - 1] + 24
        x2 = right if end == len(values) else edges[end - 1] + 24
        value = values[start]
        if value == "—":
            fig.line([(x1, y + 18), (x2, y + 18)], color=NEUTRAL, width=2)
            continue
        fig.line(
            [
                (x1, y + 18),
                (x1 + 9, y),
                (x2 - 9, y),
                (x2, y + 18),
                (x2 - 9, y + 36),
                (x1 + 9, y + 36),
                (x1, y + 18),
            ],
            color=color,
            width=2,
        )
        fig.text(
            x1 + 5,
            y - 6,
            x2 - x1 - 10,
            48,
            str(value),
            color=color,
            align="center",
        )


def timing(name, title, scope, rows, notes, rule, echo, assumption):
    samples = len(rows[0][1])
    assert all(len(values) == samples for _label, values, _kind, _color in rows)
    left, right = 245, 1410
    step = (right - left - 50) / (samples - 0.5)
    edges = [left + 50 + index * step for index in range(samples)]
    top, pitch = 310, 82
    bottom = top + pitch * (len(rows) + 1)
    cards_y = bottom + 48
    height = cards_y + 500
    fig = Figure(title, height)
    fig.text(
        30,
        92,
        1380,
        55,
        "时间向右；虚线为 ACLK 采样上升沿；按边沿前取值判断，信号在沿后更新。",
    )
    fig.text(
        30,
        145,
        1380,
        45,
        "蓝：主设备驱动；绿：从设备就绪；紫：从设备响应；—：无关值",
    )
    fig.text(30, 190, 1380, 45, scope, color=NEUTRAL, bold=True)

    for index, x in enumerate(edges):
        fig.text(
            x - 35,
            top - 52,
            70,
            42,
            f"T{index + 1}",
            bold=True,
            align="center",
        )
        fig.line([(x, top - 8), (x, bottom + 22)], color=GRID, dashed=True, width=1)
        fig.line([(x, top + 54), (x, top + 4)], arrow=True, width=2)

    fig.text(12, top - 4, 215, 55, "ACLK", bold=True)
    clock = [(left, top + 42)]
    for x in edges:
        clock.extend(
            [(x, top + 42), (x, top), (x + step * 0.43, top), (x + step * 0.43, top + 42)]
        )
    clock.append((right, top + 42))
    fig.line(clock, color=NEUTRAL, width=3)

    for row_index, (label, values, kind, color) in enumerate(rows):
        y = top + pitch * (row_index + 1)
        fig.text(12, y - 3, 215, 55, label, color=color, bold=True)
        if kind == "bit":
            draw_bit(fig, y + 5, values, edges, left, right, color)
        else:
            draw_bus(fig, y + 5, values, edges, left, right, color)

    gap = 20
    card_width = (1380 - gap * (len(notes) - 1)) / len(notes)
    for index, (label, fill, color) in enumerate(notes):
        fig.box(
            30 + index * (card_width + gap),
            cards_y,
            card_width,
            132,
            label,
            fill,
            color,
            color=color,
            rounded=True,
            bold=True,
        )
    fig.box(
        30,
        cards_y + 160,
        1380,
        92,
        rule,
        "#ffffff",
        BLUE,
        color=BLUE,
        rounded=True,
        bold=True,
    )
    fig.box(
        30,
        cards_y + 275,
        1380,
        92,
        echo,
        "#ffffff",
        PURPLE,
        color=PURPLE,
        rounded=True,
        bold=True,
    )
    fig.text(
        30,
        cards_y + 388,
        1380,
        75,
        assumption,
        color=NEUTRAL,
        align="center",
    )
    fig.save(name)


def handshakes(data, prefix):
    return [
        index + 1
        for index, (valid, ready) in enumerate(
            zip(data[f"{prefix}VALID"], data[f"{prefix}READY"])
        )
        if valid and ready
    ]


def build_read():
    rows = [
        ("ARVALID", [1, 1, 1, 0, 0, 0, 0], "bit", BLUE),
        ("ARREADY", [1] * 7, "bit", GREEN),
        ("ARID", ["1", "2", "1", "—", "—", "—", "—"], "bus", BLUE),
        ("ARADDR", ["A", "B", "C", "—", "—", "—", "—"], "bus", BLUE),
        ("RVALID", [0, 0, 0, 1, 1, 1, 0], "bit", PURPLE),
        ("RREADY", [1] * 7, "bit", BLUE),
        ("RID", ["—", "—", "—", "2", "1", "1", "—"], "bus", PURPLE),
        ("RDATA", ["—", "—", "—", "B0", "A0", "C0", "—"], "bus", PURPLE),
        ("RLAST", [0, 0, 0, 1, 1, 1, 0], "bit", PURPLE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "AR") == [1, 2, 3]
    assert handshakes(data, "R") == [4, 5, 6]
    assert [data["ARID"][i - 1] for i in handshakes(data, "AR")] == ["1", "2", "1"]
    assert [data["RID"][i - 1] for i in handshakes(data, "R")] == ["2", "1", "1"]
    assert [data["RDATA"][i - 1] for i in handshakes(data, "R")] == ["B0", "A0", "C0"]
    timing(
        "a5-1-multi-id-read",
        "AXI ID：一个物理端口上的多条逻辑有序流",
        "读地址 AR 与读数据 R｜三笔单拍读事务，无背压",
        rows,
        [
            ("T1～T3 连续发出\nT3 后有 3 笔读事务未完成", PALE_BLUE, BLUE),
            ("不同 ID 可乱序\nT4：后发的 B(ID=2) 先返回", PALE_PURPLE, PURPLE),
            ("同 ID 必须保序\nA、C 均为 ID=1：T5 A → T6 C", PALE_PURPLE, PURPLE),
        ],
        "ID=1 与 ID=2 构成两条逻辑有序流；连续发出为并行处理创造条件，但不承诺固定性能。",
        "从设备驱动 RID：B 请求的 ARID=2 → RID=2；A、C 请求的 ARID=1 → RID=1。",
        "教学重绘；A=0x1000，B=0x2000，C=0x3000；ARLEN=0，RRESP=OKAY，其余属性取合法普通访问值。",
    )


def build_write():
    rows = [
        ("AWVALID", [1, 0, 1, 0, 0], "bit", BLUE),
        ("AWREADY", [1] * 5, "bit", GREEN),
        ("AWID", ["0", "—", "0", "—", "—"], "bus", BLUE),
        ("WVALID", [1, 0, 1, 0, 0], "bit", BLUE),
        ("WREADY", [1] * 5, "bit", GREEN),
        ("WDATA", ["D0", "—", "E0", "—", "—"], "bus", BLUE),
        ("WLAST", [1, 0, 1, 0, 0], "bit", BLUE),
        ("BVALID", [0, 1, 0, 1, 0], "bit", PURPLE),
        ("BREADY", [1] * 5, "bit", BLUE),
        ("BID", ["—", "0", "—", "0", "—"], "bus", PURPLE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "AW") == [1, 3]
    assert handshakes(data, "W") == [1, 3]
    assert handshakes(data, "B") == [2, 4]
    assert [data["BID"][i - 1] for i in handshakes(data, "B")] == ["0", "0"]
    assert handshakes(data, "B")[0] < handshakes(data, "AW")[1]
    timing(
        "a5-1-fixed-id-serial-write",
        "AXI ID：固定 ID=0 的串行实现",
        "写地址 AW、写数据 W 与写响应 B｜两笔单拍写事务，无背压",
        rows,
        [
            ("事务 D\nT1：地址与数据握手\nT2：收到 BID=0", PALE_PURPLE, PURPLE),
            ("事务 E\nD 完成后才在 T3 发出\nT4：收到 BID=0", PALE_GREEN, GREEN),
        ],
        "主设备和从设备可以不利用多个事务 ID：ID 固定为 0，一次只处理一笔，事务按发出顺序完成。",
        "从设备驱动 BID：D、E 请求的 AWID 均为 0，对应写响应的 BID 也均为 0。",
        "教学重绘；D=0x4000，E=0x5000；AWLEN=0，WSTRB 全有效，BRESP=OKAY，其余属性取合法普通访问值。",
    )


def main():
    build_read()
    build_write()


if __name__ == "__main__":
    main()
