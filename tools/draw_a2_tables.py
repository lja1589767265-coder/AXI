"""Redraw the six signal tables from Chapter A2 as editable draw.io files."""

from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "image" / "axi-a2"
DRAWIO = Path(r"C:\Program Files\draw.io\draw.io.exe")
WIDTH = 1440
FONT = "Microsoft YaHei"
INK = "#172b42"
MUTED = "#697586"
LINE = "#27364a"
HEADER = "#dfe6ee"
ALT = "#f6f8fa"


TABLES = [
    (
        "table-a2-1-global-signals",
        "表 A2-1：全局信号",
        [
            (
                "ACLK",
                "时钟源",
                "全局时钟信号。同步信号（synchronous signal）在全局时钟的 rising edge 采样。\n参见第 A3-40 页的“时钟”。",
                118,
            ),
            (
                "ARESETn",
                "复位源",
                "全局复位信号。该信号低电平有效（active-LOW）。\n参见第 A3-40 页的“复位”。",
                118,
            ),
        ],
    ),
    (
        "table-a2-2-write-address-channel-signals",
        "表 A2-2：写地址通道信号",
        [
            ("AWID", "Master", "写 transaction 的标识标签（identification tag）。\n参见第 A5-81 页的“ID 信号”。", 105),
            ("AWADDR", "Master", "写 transaction 中第一次传输的地址。\n参见第 A3-48 页的“地址结构”。", 105),
            (
                "AWLEN",
                "Master",
                "长度（length），即一次写 transaction 中数据传输的确切数量。该信息决定（determines）与该地址相关联的（associated）数据传输数量。\nAXI3 与 AXI4 中的定义不同。\n参见第 A3-48 页的“突发长度”。",
                155,
            ),
            ("AWSIZE", "Master", "大小，即一次写 transaction 中每次数据传输的字节数。\n参见第 A3-49 页的“突发大小”。", 118),
            ("AWBURST", "Master", "突发类型，指示写 transaction 中每次传输之间地址如何变化。\n参见第 A3-49 页的“突发类型”。", 118),
            (
                "AWLOCK",
                "Master",
                "提供写 transaction 原子特性的信息。\nAXI3 与 AXI4 中的定义不同。\n参见第 A7-99 页的“锁定访问”。",
                135,
            ),
            ("AWCACHE", "Master", "指示写 transaction 必须如何在系统中推进。\n参见第 A4-69 页的“内存类型”。", 105),
            (
                "AWPROT",
                "Master",
                "写 transaction 的保护属性：特权级、安全级别和访问类型。\n参见第 A4-75 页的“访问权限”。",
                118,
            ),
            (
                "AWQOS",
                "Master",
                "写 transaction 的服务质量标识符。\nAXI3 中未实现。\n参见第 A8-102 页的“QoS 信号”。",
                135,
            ),
            (
                "AWREGION",
                "Master",
                "写 transaction 的区域指示符。\nAXI3 中未实现。\n参见第 A8-103 页的“多区域信号”。",
                135,
            ),
            (
                "AWUSER",
                "Master",
                "写地址通道的用户定义扩展。\nAXI3 中未实现。\n参见第 A8-104 页的“用户定义信号”。",
                135,
            ),
            ("AWVALID", "Master", "指示写地址通道信号有效。\n参见第 A3-42 页的“通道握手信号”。", 105),
            ("AWREADY", "Slave", "指示写地址通道上的一次传输可以被接收。\n参见第 A3-42 页的“通道握手信号”。", 105),
        ],
    ),
    (
        "table-a2-3-write-data-channel-signals",
        "表 A2-3：写数据通道信号",
        [
            ("WID", "Master", "写数据传输的 ID 标签（ID tag）。\n仅在 AXI3 中实现。\n参见第 A5-81 页的“ID 信号”。", 135),
            ("WDATA", "Master", "写数据。\n参见第 A3-43 页的“写数据通道”。", 105),
            ("WSTRB", "Master", "写选通，指示哪些字节通道包含有效数据。\n参见第 A3-54 页的“写选通”。", 118),
            ("WLAST", "Master", "指示这是否是一次写 transaction 中的最后一次数据传输。\n参见第 A3-43 页的“写数据通道”。", 118),
            ("WUSER", "Master", "写数据通道的用户定义扩展。\nAXI3 中未实现。\n参见第 A8-104 页的“用户定义信号”。", 135),
            ("WVALID", "Master", "指示写数据通道信号有效。\n参见第 A3-42 页的“通道握手信号”。", 105),
            ("WREADY", "Slave", "指示写数据通道上的一次传输可以被接收。\n参见第 A3-42 页的“通道握手信号”。", 105),
        ],
    ),
    (
        "table-a2-4-write-response-channel-signals",
        "表 A2-4：写响应通道信号",
        [
            ("BID", "Slave", "写响应的标识标签（identification tag）。\n参见第 A5-81 页的“ID 信号”。", 105),
            ("BRESP", "Slave", "写响应，指示一次写 transaction 的状态。\n参见第 A3-59 页的“读写响应结构”。", 118),
            ("BUSER", "Slave", "写响应通道的用户定义扩展。\nAXI3 中未实现。\n参见第 A8-104 页的“用户定义信号”。", 135),
            ("BVALID", "Slave", "指示写响应通道信号有效。\n参见第 A3-42 页的“通道握手信号”。", 105),
            ("BREADY", "Master", "指示写响应通道上的一次传输可以被接收。\n参见第 A3-42 页的“通道握手信号”。", 105),
        ],
    ),
    (
        "table-a2-5-read-address-channel-signals",
        "表 A2-5：读地址通道信号",
        [
            ("ARID", "Master", "读 transaction 的标识标签（identification tag）。\n参见第 A5-81 页的“ID 信号”。", 105),
            ("ARADDR", "Master", "读 transaction 中第一次传输的地址。\n参见第 A3-48 页的“地址结构”。", 105),
            ("ARLEN", "Master", "长度（length），即一次读 transaction 中数据传输的确切数量。AXI3 与 AXI4 中的定义不同。\n参见第 A3-48 页的“突发长度”。", 135),
            ("ARSIZE", "Master", "大小，即一次读 transaction 中每次数据传输的字节数。\n参见第 A3-49 页的“突发大小”。", 118),
            ("ARBURST", "Master", "突发类型，指示读 transaction 中每次传输之间地址如何变化。\n参见第 A3-49 页的“突发类型”。", 118),
            ("ARLOCK", "Master", "提供读 transaction 原子特性的信息。AXI3 与 AXI4 中的定义不同。\n参见第 A7-99 页的“锁定访问”。", 135),
            ("ARCACHE", "Master", "指示读 transaction 必须如何在系统中推进。\n参见第 A4-69 页的“内存类型”。", 105),
            ("ARPROT", "Master", "读 transaction 的保护属性：特权级、安全级别和访问类型。\n参见第 A4-75 页的“访问权限”。", 118),
            ("ARQOS", "Master", "读 transaction 的服务质量标识符。\nAXI3 中未实现。\n参见第 A8-102 页的“QoS 信号”。", 135),
            ("ARREGION", "Master", "读 transaction 的区域指示符。\nAXI3 中未实现。\n参见第 A8-103 页的“多区域信号”。", 135),
            ("ARUSER", "Master", "读地址通道的用户定义扩展。\nAXI3 中未实现。\n参见第 A8-104 页的“用户定义信号”。", 135),
            ("ARVALID", "Master", "指示读地址通道信号有效。\n参见第 A3-42 页的“通道握手信号”。", 105),
            ("ARREADY", "Slave", "指示读地址通道上的一次传输可以被接收。\n参见第 A3-42 页的“通道握手信号”。", 105),
        ],
    ),
    (
        "table-a2-6-read-data-channel-signals",
        "表 A2-6：读数据通道信号",
        [
            ("RID", "Slave", "读数据和响应的标识标签（identification tag）。\n参见第 A5-81 页的“ID 信号”。", 105),
            ("RDATA", "Slave", "读数据。\n参见第 A3-43 页的“读数据通道”。", 105),
            ("RRESP", "Slave", "读响应，指示一次读传输的状态。\n参见第 A3-59 页的“读写响应结构”。", 118),
            ("RLAST", "Slave", "指示这是否是一次读 transaction 中的最后一次数据传输。\n参见第 A3-43 页的“读数据通道”。", 118),
            ("RUSER", "Slave", "读数据通道的用户定义扩展。\nAXI3 中未实现。\n参见第 A8-104 页的“用户定义信号”。", 135),
            ("RVALID", "Slave", "指示读数据通道信号有效。\n参见第 A3-42 页的“通道握手信号”。", 105),
            ("RREADY", "Master", "指示读数据通道上的一次传输可以被接收。\n参见第 A3-42 页的“通道握手信号”。", 105),
        ],
    ),
]


class TableFigure:
    def __init__(self, title: str, rows):
        self.title = title
        self.rows = rows
        self.height = 145 + 76 + sum(row[3] for row in rows) + 72
        self.doc = ET.Element("mxfile", host="app.diagrams.net")
        diagram = ET.SubElement(self.doc, "diagram", name=title)
        model = ET.SubElement(
            diagram,
            "mxGraphModel",
            page="1",
            pageWidth=str(WIDTH),
            pageHeight=str(self.height),
        )
        self.root = ET.SubElement(model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.counter = 2

    def cell(self, x, y, width, height, value, *, fill, bold=False, align="left", size=25):
        cell = ET.SubElement(
            self.root,
            "mxCell",
            id=str(self.counter),
            value=value,
            vertex="1",
            parent="1",
            style=(
                "rounded=0;whiteSpace=wrap;html=0;"
                f"fontFamily={FONT};fontSize={size};fontColor={INK};"
                f"fontStyle={int(bold)};fillColor={fill};strokeColor={LINE};"
                f"strokeWidth=2;align={align};verticalAlign=middle;spacing=12;"
            ),
        )
        self.counter += 1
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(x),
            y=str(y),
            width=str(width),
            height=str(height),
            **{"as": "geometry"},
        )

    def text(self, x, y, width, height, value, *, size=24, bold=False, align="center", color=MUTED):
        cell = ET.SubElement(
            self.root,
            "mxCell",
            id=str(self.counter),
            value=value,
            vertex="1",
            parent="1",
            style=(
                "text;whiteSpace=wrap;html=0;strokeColor=none;fillColor=none;"
                f"fontFamily={FONT};fontSize={size};fontColor={color};"
                f"fontStyle={int(bold)};align={align};verticalAlign=middle;spacing=0;"
            ),
        )
        self.counter += 1
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(x),
            y=str(y),
            width=str(width),
            height=str(height),
            **{"as": "geometry"},
        )

    def build(self):
        self.cell(0, 0, WIDTH, self.height, "", fill="#ffffff", size=1)
        self.text(30, 22, 1380, 66, self.title, size=40, bold=True, color=INK)
        left = 35
        widths = (190, 185, 995)
        y = 112
        for x, width, label, align in zip(
            (left, left + widths[0], left + widths[0] + widths[1]),
            widths,
            ("信号", "来源", "说明"),
            ("center", "center", "left"),
        ):
            self.cell(x, y, width, 76, label, fill=HEADER, bold=True, align=align, size=27)
        y += 76
        for index, (signal, source, description, row_height) in enumerate(self.rows):
            fill = "#ffffff" if index % 2 == 0 else ALT
            self.cell(left, y, widths[0], row_height, signal, fill=fill, bold=True, align="center")
            self.cell(left + widths[0], y, widths[1], row_height, source, fill=fill, align="center")
            self.cell(left + widths[0] + widths[1], y, widths[2], row_height, description, fill=fill)
            y += row_height
        self.text(30, self.height - 54, 1380, 34, "根据原表中文重绘", size=23)

    def save(self, name: str):
        self.build()
        OUT.mkdir(parents=True, exist_ok=True)
        source = OUT / f"{name}.drawio"
        target = source.with_suffix(".png")
        ET.ElementTree(self.doc).write(source, encoding="utf-8", xml_declaration=True)
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
            timeout=90,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode or not target.exists():
            raise RuntimeError(result.stdout + result.stderr)
        print(source)
        print(target)


def main():
    for name, title, rows in TABLES:
        TableFigure(title, rows).save(name)


if __name__ == "__main__":
    main()
