"""Validate Chapter A3 Markdown and its 15 figures plus five tables."""

from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A3.md"
IMAGE_DIR = ROOT / "image" / "axi-a3"

FIGURES = [
    "figure-a3-1-exit-from-reset",
    "figure-a3-2-valid-before-ready-handshake",
    "figure-a3-3-ready-before-valid-handshake",
    "figure-a3-4-valid-with-ready-handshake",
    "figure-a3-5-read-transaction-handshake-dependencies",
    "figure-a3-6-axi3-write-transaction-handshake-dependencies",
    "figure-a3-7-axi4-axi5-write-transaction-handshake-dependencies",
    "figure-a3-8-narrow-transfer-8-bit",
    "figure-a3-9-narrow-transfer-32-bit",
    "figure-a3-10-big-endian-byte-invariant",
    "figure-a3-11-little-endian-byte-invariant",
    "figure-a3-12-mixed-endian-data-structure",
    "figure-a3-13-aligned-unaligned-32-bit-bus",
    "figure-a3-14-aligned-unaligned-64-bit-bus",
    "figure-a3-15-aligned-wrapping-64-bit-bus",
]

TABLES = [
    "table-a3-1-transaction-channel-handshake-pairs",
    "table-a3-2-burst-size-encoding",
    "table-a3-3-burst-type-encoding",
    "table-a3-4-regular-transactions-only-interoperability",
    "table-a3-5-rresp-bresp-encoding",
]

SUPPLEMENTAL = [
    "supplemental-awvalid-hold-until-awready",
    "supplemental-archannel-requirements",
    "supplemental-bchannel-requirements",
    "supplemental-multi-beat-write-response",
    "supplemental-no-combinational-input-output-path",
    "supplemental-read-data-after-address",
    "supplemental-reset-valid-requirements",
    "supplemental-valid-must-not-wait-for-ready",
    "supplemental-wchannel-requirements",
    "supplemental-rchannel-requirements",
]


def png_size(path: Path):
    with path.open("rb") as stream:
        assert stream.read(8) == b"\x89PNG\r\n\x1a\n", path
        length = struct.unpack(">I", stream.read(4))[0]
        assert stream.read(4) == b"IHDR" and length == 13, path
        return struct.unpack(">II", stream.read(8))


text = DOC.read_text(encoding="utf-8")
assert len(re.findall(r"^# ", text, flags=re.MULTILINE)) == 1
assert re.findall(r"^## (A3\.\d .+)$", text, flags=re.MULTILINE) == [
    "A3.1 时钟与复位 / Clock and reset",
    "A3.2 基本读写 transaction / Basic read and write transactions",
    "A3.3 通道之间的关系 / Relationships between the channels",
    "A3.4 Transaction 结构 / Transaction structure",
]
assert re.findall(r"^### (A3\.\d\.\d .+)$", text, flags=re.MULTILINE) == [
    "A3.1.1 时钟 / Clock", "A3.1.2 复位 / Reset",
    "A3.2.1 握手过程 / Handshake process",
    "A3.2.2 通道信号要求 / Channel signaling requirements",
    "A3.3.1 通道握手信号之间的依赖关系 / Dependencies between channel handshake signals",
    "A3.3.2 旧版兼容性考虑 / Legacy considerations",
    "A3.4.1 地址结构 / Address structure",
    "A3.4.2 传输的伪代码说明 / Pseudocode description of the transfers",
    "A3.4.3 Regular transaction / Regular transactions",
    "A3.4.4 数据读写结构 / Data read and write structure",
    "A3.4.5 读写响应结构 / Read and write response structure",
]
assert "A3-39～A3-60" in text
assert "<details>" not in text and "background-color" not in text
assert not any(word in text for word in ("学习目标", "自测题", "易错点", "下一章"))
assert "非官方中英双语对照翻译" in text
assert text.count("> **原文（English）**") == 142
assert text.count("> **原文图题（English）**") == 15
assert text.count("> **原文表题（English）**") == 5
assert "> 原文：" not in text

refs = re.findall(r"!\[[^]]+\]\((image/axi-a3/[^)]+\.png)\)", text)
expected = FIGURES + TABLES + SUPPLEMENTAL
assert len(refs) == len(expected) and len(set(refs)) == len(expected), refs

for name in expected:
    drawio = IMAGE_DIR / f"{name}.drawio"
    png = IMAGE_DIR / f"{name}.png"
    assert drawio.exists() and png.exists(), name
    assert png_size(png)[0] == 1440, png
    assert f"image/axi-a3/{name}.png" in refs
    root = ET.parse(drawio).getroot()
    values = [cell.attrib.get("value", "") for cell in root.iter("mxCell")]
    assert not any("主设备" in value or "从设备" in value or "事务" in value for value in values), name
    if name.startswith("supplemental-"):
        assert any("补充图" in value and "原文图" in value for value in values), name
        continue
    elif name.startswith("table-"):
        note = "根据原表双语重绘 / Bilingual redraw based on original table"
    else:
        note = "根据原图双语重绘 / Bilingual redraw based on original figure"
    assert note in values, name

assert (ROOT / "legacy" / "ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A3_learning-guide.md").exists()
print("PASS: A3 full bilingual structure, 15 figures, five tables, ten supplemental figures, 30 draw.io/PNG pairs, and 1440px exports verified")
