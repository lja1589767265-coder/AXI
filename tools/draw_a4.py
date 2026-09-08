"""Create editable teaching diagrams and export them with local draw.io.

These are teaching examples, not simulation captures. Run with Python 3.
"""
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'image' / 'axi-a4'
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



def main():
    d = Diagram('01-attribute-map', 'AXI4：先判断处理规则，再判断权限', 900)
    d.box(30, 100, 1020, 90, '主设备发出地址和属性：ARCACHE / AWCACHE', '#dbeafe')
    items = [
        ('[1] Modifiable', '0：Device，通常不能拆分或合并\n1：可修改事务形状，仍有边界约束'),
        ('[3:2] 缓存查询', '00：不要求查缓存\n非 00：要求查询，分配建议并非强制分配'),
        ('[0] Bufferable', '结合高位和读写方向解释\n不能仅凭这一位判断响应来源'),
        ('AxPROT[2:0]', '[2] 指令 / 数据　[1] 非安全 / 安全\n[0] 特权 / 非特权（前者均编码为 1）'),
    ]
    for i,(a,b) in enumerate(items):
        y=220+i*135
        d.box(30,y,330,110,a,'#fef3c7')
        d.box(380,y,670,110,b,'#f8fafc')
    d.text(30,780,1020,90,'蓝：主设备　黄：判断字段；从上向下阅读。\n教学重绘；依据 A4.3、A4.4、A4.7。')
    d.save()

    d = Diagram('02-response-and-visibility', '写响应返回，与写入到达是两件事', 1010)
    d.box(30,100,290,80,'主设备','#dbeafe')
    d.box(390,100,300,80,'中间缓冲 / 缓存','#ffedd5')
    d.box(760,100,290,80,'最终目的地','#dcfce7')
    d.text(30,200,1020,70,'处理路径：主设备 → 中间节点 → 最终目的地\n下方各行比较规则，不表示固定周期或握手时序。')
    rows=[
      ('Device / Normal 非缓存，B=0','响应须来自最终目的地'),
      ('Device / Normal 非缓存，B=1','中间节点可响应；写入仍须及时到达'),
      ('Write-Through：高位非 00，B=0','中间节点可响应；写入仍须及时到达'),
      ('Write-Back：高位非 00，B=1','中间节点可响应；不要求此次写入到达'),
    ]
    for i,(a,b) in enumerate(rows):
        y=300+i*140
        d.box(30,y,1020,55,a,'#f1f5f9')
        d.box(30,y+55,1020,65,b,'#f3e8ff',color=PURPLE)
    d.text(30,880,1020,100,'B 指 AWCACHE[0]；高位指 AWCACHE[3:2]。\n紫：响应规则；“及时”没有固定周期数。\n教学重绘；依据 A4.3 Table A4-3、A4.4、A4.6。')
    d.save()

    d = Diagram('03-device-completion', 'Device 写：怎样确认前序写已到达', 990)
    d.text(30,90,1020,100,'前提：AXI4；同一主设备、同一 ID、同一从设备。\n这是顺序关系图，不是波形；没有固定拍数含义。')
    steps=[
      ('① 发出 Device Bufferable 写 W0、W1','AWCACHE=0001；中间缓冲可以先返回响应。','#dbeafe'),
      ('② 随后发出 Device Non-bufferable 写 W2','AWCACHE=0000；沿用同一 ID，访问同一从设备。','#dbeafe'),
      ('③ 顺序规则约束最终目的地的处理','前序 W0、W1 必须先到达，W2 才能返回响应。','#dcfce7'),
      ('④ 主设备收到 W2 的响应','此时可确认前序 W0、W1 已在最终目的地可见。','#f3e8ff'),
    ]
    for i,(a,b,c) in enumerate(steps):
        y=215+i*160
        d.box(30,y,1020,125,a+'\n'+b,c)
        if i<3: d.text(505,y+125,80,35,'↓')
    d.text(30,865,1020,95,'W0/W1/W2 是完整写事务名称，不是 W 通道数据拍。\n不同 ID 或不同从设备不在此保证范围内。\n教学重绘；依据 A4.8、A4.9.1。')
    d.save()

if __name__ == '__main__':
    main()
