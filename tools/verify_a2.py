"""Validate the Chapter A2 Markdown and its six redrawn signal tables."""

from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A2.md"
IMAGE_DIR = ROOT / "image" / "axi-a2"

EXPECTED = {
    "table-a2-1-global-signals": ["ACLK", "ARESETn"],
    "table-a2-2-write-address-channel-signals": [
        "AWID", "AWADDR", "AWLEN", "AWSIZE", "AWBURST", "AWLOCK", "AWCACHE",
        "AWPROT", "AWQOS", "AWREGION", "AWUSER", "AWVALID", "AWREADY",
    ],
    "table-a2-3-write-data-channel-signals": [
        "WID", "WDATA", "WSTRB", "WLAST", "WUSER", "WVALID", "WREADY",
    ],
    "table-a2-4-write-response-channel-signals": [
        "BID", "BRESP", "BUSER", "BVALID", "BREADY",
    ],
    "table-a2-5-read-address-channel-signals": [
        "ARID", "ARADDR", "ARLEN", "ARSIZE", "ARBURST", "ARLOCK", "ARCACHE",
        "ARPROT", "ARQOS", "ARREGION", "ARUSER", "ARVALID", "ARREADY",
    ],
    "table-a2-6-read-data-channel-signals": [
        "RID", "RDATA", "RRESP", "RLAST", "RUSER", "RVALID", "RREADY",
    ],
}


def png_size(path: Path):
    with path.open("rb") as stream:
        assert stream.read(8) == b"\x89PNG\r\n\x1a\n", path
        length = struct.unpack(">I", stream.read(4))[0]
        assert stream.read(4) == b"IHDR" and length == 13, path
        return struct.unpack(">II", stream.read(8))


text = DOC.read_text(encoding="utf-8")
assert len(re.findall(r"^# ", text, flags=re.MULTILINE)) == 1
assert re.findall(r"^## (A2\.\d .+)$", text, flags=re.MULTILINE) == [
    "A2.1 全局信号",
    "A2.2 写地址通道信号",
    "A2.3 写数据通道信号",
    "A2.4 写响应通道信号",
    "A2.5 读地址通道信号",
    "A2.6 读数据通道信号",
]
assert "A2-31～A2-38" in text
assert "<details>" not in text
assert "background-color" not in text
assert "自测" not in text and "学习目标" not in text and "章节小结" not in text

refs = re.findall(r"!\[[^]]+\]\((image/axi-a2/table-a2-[^)]+\.png)\)", text)
assert len(refs) == 6 and len(set(refs)) == 6

for name, signals in EXPECTED.items():
    drawio = IMAGE_DIR / f"{name}.drawio"
    png = IMAGE_DIR / f"{name}.png"
    assert drawio.exists() and png.exists(), name
    assert png_size(png)[0] == 1440, png
    root = ET.parse(drawio).getroot()
    values = [cell.attrib.get("value", "") for cell in root.iter("mxCell")]
    assert "主设备" not in values and "从设备" not in values, name
    assert not any("事务" in value for value in values), name
    if name != "table-a2-1-global-signals":
        assert "Master" in values and "Slave" in values, name
    positions = [values.index(signal) for signal in signals]
    assert positions == sorted(positions), name
    assert "根据原表中文重绘" in values
    assert f"image/axi-a2/{name}.png" in refs

assert sum(len(signals) for signals in EXPECTED.values()) == 47
print("PASS: A2 structure, 47 signal rows, six draw.io/PNG pairs, and 1440px exports verified")
