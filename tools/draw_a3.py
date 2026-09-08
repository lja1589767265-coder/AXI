"""Create editable teaching diagrams and export them with local draw.io.

These are teaching examples, not simulation captures. Run with Python 3.
"""
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'image' / 'axi-a3'
BLUE, GREEN, PURPLE, GRAY = '#2463ad', '#158060', '#7c3aed', '#64748b'


class Diagram:
    def __init__(self, name, title, height):
        self.name = name
        self.doc = ET.Element('mxfile', host='draw.io')
        dia = ET.SubElement(self.doc, 'diagram', name=title)
        model = ET.SubElement(dia, 'mxGraphModel', page='1', pageWidth='1080', pageHeight=str(height))
        self.root = ET.SubElement(model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0')
        ET.SubElement(self.root, 'mxCell', id='1', parent='0')
        self.i = 2
        self.box(0, 0, 1080, height, '', '#ffffff', 'none')
        self.text(30, 20, 1020, 55, title, 38, bold=True)

    def cell(self, **kw):
        c = ET.SubElement(self.root, 'mxCell', id=str(self.i), parent='1', **kw)
        self.i += 1
        return c

    def box(self, x, y, w, h, text, fill='#f1f5f9', stroke='#cbd5e1', size=32, color='#172b42'):
        c = self.cell(value=text, vertex='1', style=f'rounded=0;whiteSpace=wrap;html=0;fontFamily=Microsoft YaHei;fontSize={size};fontColor={color};fillColor={fill};strokeColor={stroke};')
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})

    def text(self, x, y, w, h, text, size=32, color='#172b42', bold=False):
        c = self.cell(value=text, vertex='1', style=f'text;html=0;whiteSpace=wrap;align=left;verticalAlign=middle;fontFamily=Microsoft YaHei;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};')
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})

    def line(self, points, color=GRAY, dash=False):
        c = self.cell(edge='1', style=f'endArrow=none;startArrow=none;rounded=0;strokeWidth=2;strokeColor={color};dashed={1 if dash else 0};')
        g = ET.SubElement(c, 'mxGeometry', relative='1', **{'as': 'geometry'})
        for p, role in [(points[0], 'sourcePoint'), (points[-1], 'targetPoint')]:
            ET.SubElement(g, 'mxPoint', x=str(p[0]), y=str(p[1]), **{'as': role})
        if len(points) > 2:
            a = ET.SubElement(g, 'Array', **{'as': 'points'})
            for x, y in points[1:-1]:
                ET.SubElement(a, 'mxPoint', x=str(x), y=str(y))

    def save(self):
        OUT.mkdir(parents=True, exist_ok=True)
        src = OUT / (self.name + '.drawio')
        ET.ElementTree(self.doc).write(src, encoding='utf-8', xml_declaration=True)
        dst = src.with_suffix('.png')
        result = subprocess.run([
            r'C:\Program Files\draw.io\draw.io.exe', '--export', '--format', 'png',
            '--width', '1080', '--output', str(dst), str(src)
        ], capture_output=True, text=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode or not dst.exists():
            raise RuntimeError(result.stdout + result.stderr)
        print(dst.name, flush=True)


def wave(name, title, rows, notes, annotations=None):
    n = len(rows[0][1])
    top, pitch, left, step = 300, 80, 230, 780 / n
    end = top + pitch * (len(rows) + 1)
    d = Diagram(name, title, end + 70 + 48 * len(notes))
    d.text(30, 85, 1020, 45, '时间向右；虚线为上升沿，按边沿前的值判断。')
    d.text(30, 130, 1020, 45, '蓝：主设备　绿：从设备　紫：响应　—：无效信息')
    d.text(30, 175, 1020, 45, '教学波形；数据变化在采样沿之后，非仿真采集。')
    for x, y, w, label, color in annotations or []:
        d.text(x, y, w, 38, label, 24, color, bold=True)
    for j in range(n):
        x = left + (j + 1) * step
        d.line([(x, top - 15), (x, end)], '#cbd5e1', True)
        d.text(x - 24, top - 50, 75, 40, f'T{j+1}')
    d.text(25, top, 200, 45, 'ACLK')
    pts = [(left, top + 5)]
    for j in range(n):
        a, b = left + j * step, left + (j + 1) * step
        pts += [(a + step / 2, top + 5), (a + step / 2, top + 40), (b, top + 40), (b, top + 5)]
    d.line(pts)
    for i, (label, vals, color, kind) in enumerate(rows):
        y = top + (i + 1) * pitch
        d.text(25, y, 200, 45, label, color=color)
        if kind == 'bit':
            pts = []
            for j, v in enumerate(vals):
                a, b = left + j * step + 8, left + (j + 1) * step + 8
                level = y + (5 if v else 40)
                if pts:
                    pts.append((a, pts[-1][1]))
                pts += [(a, level), (b, level)]
            d.line(pts, color)
        else:
            j = 0
            while j < n:
                k = j + 1
                while k < n and vals[k] == vals[j]:
                    k += 1
                d.box(left + j * step + 8, y, (k-j)*step, 48, vals[j], '#f8fafc', color, color=color)
                j = k
    for i, note in enumerate(notes):
        d.text(30, end + 15 + 48*i, 1020, 45, note)
    d.save()


def main():
    wave('01-reset', 'Clock 与 Reset：复位期间 VALID 必须为 0', [
        ('ARESETn', [0, 0, 1, 1], GRAY, 'bit'),
        ('ARVALID', [0, 0, 0, 0], BLUE, 'bit'),
        ('AWVALID', [0, 0, 0, 1], BLUE, 'bit'),
        ('WVALID', [0, 0, 0, 0], BLUE, 'bit'),
        ('RVALID', [0, 0, 0, 0], GREEN, 'bit'),
        ('BVALID', [0, 0, 0, 0], PURPLE, 'bit'),
        ('AWREADY', [0, 0, 1, 1], GREEN, 'bit'),
        ('AWADDR', ['—', '—', '—', 'A'], BLUE, 'data'),
    ], [], [
        (300, 215, 390, 'T1～T2：复位期间', GRAY),
        (800, 215, 250, 'T4：传输地址 A', PURPLE),
    ])
    wave('02-handshake', '握手：等待保持同一拍，连续握手传不同拍', [
        ('VALID', [0, 1, 1, 1, 0], BLUE, 'bit'),
        ('READY', [1, 0, 1, 1, 1], GREEN, 'bit'),
        ('Payload', ['—', 'A', 'A', 'B', '—'], BLUE, 'data'),
    ], ['本图以主设备发送的通道为例；Payload 为整组信息。',
        'T2 → T3 等待：VALID 与 A 保持；T3 接收 A。',
        'T4 接收 B：VALID 不必在两拍之间拉低。',
        '共传输两次；依据 A3.2.1。'])
    wave('03-write', 'AXI4 写：W 可以先到，B 必须等齐条件', [
        ('AWVALID', [0, 1, 1, 0, 0, 0], BLUE, 'bit'),
        ('AWREADY', [0, 0, 1, 1, 1, 1], GREEN, 'bit'),
        ('WVALID', [1, 1, 1, 0, 0, 0], BLUE, 'bit'),
        ('WREADY', [1, 0, 1, 1, 1, 1], GREEN, 'bit'),
        ('WDATA', ['D0', 'D1', 'D1', '—', '—', '—'], BLUE, 'data'),
        ('WLAST', [0, 1, 1, 0, 0, 0], BLUE, 'bit'),
        ('BVALID', [0, 0, 0, 1, 1, 0], PURPLE, 'bit'),
        ('BREADY', [0, 0, 0, 0, 1, 1], BLUE, 'bit'),
    ], ['32 位总线；AWADDR=0x1000，AWLEN=1（两拍）。',
        'AWSIZE=2（4 字节）；AWBURST=01（INCR 递增）。',
        '有效 W 拍 WSTRB=1111（四字节均有效）。',
        '有效 B 拍 BRESP=00（OKAY）；ID 固定为 0。',
        'T2 → T3 保持 AW 字段、D1、WLAST、WSTRB。',
        'T4 → T5 保持 B；T5 响应握手，T6 空闲。',
        'ARESETn=1；AWLOCK=0（普通访问）。',
        'AWCACHE、AWPROT、AWQOS、AWREGION、AWUSER=0。',
        '教学重绘；依据 A3.3.1。'])
    wave('04-read', '读突发：某一拍报错，后续仍须完成', [
        ('ARVALID', [1, 0, 0, 0, 0, 0], BLUE, 'bit'),
        ('ARREADY', [1, 1, 1, 1, 1, 1], GREEN, 'bit'),
        ('RVALID', [0, 1, 1, 1, 1, 0], GREEN, 'bit'),
        ('RREADY', [1, 1, 0, 1, 1, 1], BLUE, 'bit'),
        ('RDATA', ['—', 'D0', 'X', 'X', 'D2', '—'], GREEN, 'data'),
        ('RRESP', ['—', '00', '10', '10', '00', '—'], PURPLE, 'data'),
        ('RLAST', [0, 0, 0, 0, 1, 0], GREEN, 'bit'),
    ], ['32 位总线；ARADDR=0x2000，ARLEN=2（三拍）。',
        'ARSIZE=2（4 字节）；ARBURST=01（INCR 递增）。',
        '00=OKAY；10=SLVERR；X 为错误拍的稳定占位值。',
        'T3 → T4 等待：RDATA、RRESP、RLAST 均保持。',
        'T2、T4、T5 共三次 R 握手；T6 空闲。',
        'ARESETn=1；ID=0；ARLOCK=0（普通访问）。',
        'ARCACHE、ARPROT、ARQOS、ARREGION、ARUSER=0。',
        '依据 A3.2、A3.3.1、A3.4.5。'])
    d = Diagram('05-byte-lanes', '非对齐首拍：64 位总线，每拍最多 4 字节', 760)
    d.text(30, 85, 1020, 50, 'INCR 递增；起始地址 0x07；AxSIZE=2；AxLEN=3。')
    d.text(30, 135, 1020, 50, '四行代表四次数据握手；单元格内为字节地址。')
    d.text(30, 185, 1020, 50, '白色：未使用；蓝色：有效字节；lane 0 对应 [7:0]。')
    for lane in range(8):
        d.box(245 + (7-lane)*98, 260, 98, 60, str(lane))
    d.text(30, 260, 205, 60, '字节通道')
    for i, addr in enumerate([7, 8, 12, 16]):
        low = addr % 8
        high = ((addr//4)*4+3) % 8
        d.text(30, 340+i*75, 205, 60, f'第 {i+1} 拍')
        for lane in range(8):
            valid = low <= lane <= high
            d.box(245+(7-lane)*98, 340+i*75, 98, 60,
                  f'{addr//8*8+lane:02X}' if valid else '—',
                  '#dbeafe' if valid else '#ffffff')
    d.text(30, 660, 1020, 60, 'WSTRB 依次为 80、0F、F0、0F（十六进制）。')
    d.save()
    d = Diagram('06-burst-addresses', '同一起点：三种 Burst 怎样计算后续地址', 700)
    d.text(30, 90, 1020, 55, '起点 0x0C；每拍 4 字节；4 拍；均为对齐访问。')
    for i, (label, vals) in enumerate([
        ('FIXED 固定', ['0C', '0C', '0C', '0C']),
        ('INCR 递增', ['0C', '10', '14', '18']),
        ('WRAP 回绕', ['0C', '00', '04', '08']),
    ]):
        y = 220+i*100
        d.text(30, y, 290, 65, label)
        for j, val in enumerate(vals):
            d.box(330+j*175, y, 165, 65, '0x'+val, '#dbeafe' if i<2 else '#dcfce7')
    d.text(30, 530, 1020, 55, '每格代表一拍的地址；不是四次地址通道握手。')
    d.text(30, 585, 1020, 80, 'WRAP 容器为 [0x00, 0x10)，到 0x10 时回到 0x00。\n教学重绘；依据 A3.4.1。')
    d.save()


if __name__ == '__main__':
    main()
