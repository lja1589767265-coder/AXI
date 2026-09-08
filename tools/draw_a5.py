"""Build editable draw.io teaching diagrams; export PNGs with local draw.io CLI."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'image' / 'axi-a5'
OUT.mkdir(parents=True, exist_ok=True)
BLUE, GREEN, PURPLE = '#2463ad', '#158060', '#7952b3'

class Diagram:
    def __init__(self, title, height):
        self.doc = ET.Element('mxfile', host='app.diagrams.net')
        page = ET.SubElement(self.doc, 'diagram', name=title)
        model = ET.SubElement(page, 'mxGraphModel', page='1', pageWidth='1080', pageHeight=str(height))
        self.root = ET.SubElement(model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0')
        ET.SubElement(self.root, 'mxCell', id='1', parent='0')
        self.i = 1
        self.box(0, 0, 1080, height, '', 'fillColor=#ffffff;strokeColor=none;')
        self.text(28, 18, 1024, 62, title, size=38)

    def box(self, x, y, w, h, value, style=''):
        self.i += 1
        c = ET.SubElement(self.root, 'mxCell', id=str(self.i), value=value,
                         style='whiteSpace=wrap;html=0;fontFamily=Microsoft YaHei;fontSize=32;fontColor=#172b42;'+style,
                         vertex='1', parent='1')
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as':'geometry'})

    def text(self, x, y, w, h, value, color='#172b42', size=32):
        self.box(x,y,w,h,value,f'text;align=left;verticalAlign=middle;spacing=0;fontColor={color};fontSize={size};')

    def line(self, points, color='#697586', width=2, dashed=False, arrow=False):
        self.i += 1
        c = ET.SubElement(self.root,'mxCell',id=str(self.i),edge='1',parent='1',
            style=f'edgeStyle=none;rounded=0;endArrow={"block" if arrow else "none"};strokeColor={color};strokeWidth={width};dashed={int(dashed)};')
        g=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
        for name, pt in [('sourcePoint',points[0]),('targetPoint',points[-1])]:
            ET.SubElement(g,'mxPoint',x=str(pt[0]),y=str(pt[1]),**{'as':name})
        if len(points)>2:
            a=ET.SubElement(g,'Array',**{'as':'points'})
            for x,y in points[1:-1]: ET.SubElement(a,'mxPoint',x=str(x),y=str(y))

    def save(self,name):
        path=OUT/(name+'.drawio')
        ET.ElementTree(self.doc).write(path,encoding='utf-8',xml_declaration=True)
        print(path)

def timing(name,title,rows,notes,n):
    left, step, top, pitch = 270, 760/n, 220, 77
    bottom=top+(len(rows)+1)*pitch
    d=Diagram(title,bottom+65+len(notes)*47)
    d.text(28,88,1024,45,'教学重绘｜时间向右；虚线为 ACLK 采样上升沿')
    d.text(28,135,1024,45,'蓝：主设备；绿：从设备；紫：响应；—：无关值')
    for j in range(n):
        x=left+(j+1)*step
        d.line([(x,top-10),(x,bottom)],'#dce3eb',1,True)
        d.text(x-25,top-50,65,40,f'T{j+1}')
    d.text(25,top,235,50,'ACLK')
    pts=[(left,top+5)]
    for j in range(n):
        a=left+j*step; b=a+step
        pts += [(a+step/2,top+5),(a+step/2,top+41),(b,top+41),(b,top+5)]
    d.line(pts,width=3)
    for i,(label,values,kind,color) in enumerate(rows):
        assert len(values)==n
        y=top+(i+1)*pitch
        d.text(25,y,235,50,label,color)
        if kind=='bit':
            pts=[]
            for j,v in enumerate(values):
                a=left+j*step+8; b=a+step; level=y+(5 if v else 41)
                if pts: pts.append((a,pts[-1][1]))
                pts.extend([(a,level),(b,level)])
            d.line(pts,color,3)
        else:
            j=0
            while j<n:
                k=j+1
                while k<n and values[k]==values[j]: k+=1
                d.box(left+j*step+8,y+2,(k-j)*step,45,str(values[j]),
                      f'fillColor=#f4f6fa;strokeColor={color};fontColor={color};')
                j=k
    for i,note in enumerate(notes): d.text(28,bottom+15+i*47,1020,45,note)
    d.save(name)

timing('01-read-reordering','读响应乱序：后发的 B 先完成',[
 ('ARVALID',[1,1,0,0,0,0,0],'bit',BLUE),
 ('ARREADY',[1,1,1,1,1,1,1],'bit',GREEN),
 ('ARID',['1','2','—','—','—','—','—'],'bus',BLUE),
 ('RVALID',[0,0,1,1,1,1,0],'bit',PURPLE),
 ('RREADY',[1,1,0,1,1,1,1],'bit',BLUE),
 ('RID',['—','—','2','2','1','1','—'],'bus',PURPLE),
 ('RDATA',['—','—','B0','B0','A0','A1','—'],'bus',PURPLE),
 ('RLAST',[0,0,1,1,0,1,0],'bit',PURPLE),
],['A：ID=1，2 拍；B：ID=2，1 拍；数据为占位符。',
   'T3 等待 → T4 接收 B0；等待中 RID / RDATA / RLAST 保持。',
   'A 地址 0x1000、ARLEN=1；B 地址 0x2000、ARLEN=0。',
   '固定：ARSIZE=2（4 字节），ARBURST=INCR（递增）。',
   '固定：RRESP=OKAY（成功）；其余属性取合法普通访问值。'],7)

timing('02-write-order','AXI4：W 按地址次序，B 可按不同 ID 乱序',[
 ('AWVALID',[1,1,0,0,0,0,0,0],'bit',BLUE),
 ('AWREADY',[1,1,1,1,1,1,1,1],'bit',GREEN),
 ('AWID',['1','2','—','—','—','—','—','—'],'bus',BLUE),
 ('WVALID',[0,1,1,1,1,0,0,0],'bit',BLUE),
 ('WREADY',[1,1,1,1,1,1,1,1],'bit',GREEN),
 ('WDATA',['—','A0','A1','B0','B1','—','—','—'],'bus',BLUE),
 ('WLAST',[0,0,1,0,1,0,0,0],'bit',BLUE),
 ('BVALID',[0,0,0,0,0,1,1,0],'bit',PURPLE),
 ('BREADY',[1,1,1,1,1,1,1,1],'bit',BLUE),
 ('BID',['—','—','—','—','—','2','1','—'],'bus',PURPLE),
],['A：ID=1，地址 0x1000；B：ID=2，地址 0x2000。',
   'A0/A1、B0/B1 是数据占位符；AXI4 没有 WID。',
   '固定：AWLEN=1（2 拍），AWSIZE=2（每拍 4 字节）。',
   '固定：AWBURST=INCR（递增），WSTRB=1111（二进制）。',
   'WSTRB 表示 4 个字节全有效；BRESP=OKAY（成功）。',
   '无等待拍；AWLOCK=0（普通访问），其余属性合法固定。'],8)

d=Diagram('互连扩展 ID：两个主设备都可以使用 ID=3',1030)
d.text(28,90,1020,60,'教学重绘｜示例：原 ID 为 2 位，增加 1 位来源编号')
for x,port,bits in [(40,'M0','0'),(580,'M1','1')]:
    d.box(x,185,460,125,f'主设备 {port}\n原 ID = 11（二进制）',f'rounded=1;fillColor=#edf4fc;strokeColor={BLUE};')
    d.line([(x+230,310),(x+230,405)],BLUE,3,arrow=True)
    d.box(x,405,460,115,f'互连附加来源位 {bits}\n扩展 ID = {bits}11', 'rounded=1;fillColor=#fff3df;strokeColor=#d58a25;')
    d.line([(x+230,520),(x+230,610)],'#d58a25',3,arrow=True)
d.box(40,610,1000,105,'从设备看到：011 和 111\n响应返回相应 RID / BID',f'rounded=1;fillColor=#eaf6f0;strokeColor={GREEN};')
d.text(40,755,1000,50,'响应 011 → 互连去掉来源位 0 → M0 收到 ID=11',PURPLE)
d.text(40,817,1000,50,'响应 111 → 互连去掉来源位 1 → M1 收到 ID=11',PURPLE)
d.text(40,891,1000,95,'读请求用 ARID，写请求用 AWID；响应为 RID / BID。\n本图为概念流程，不表示周期或固定延迟。')
d.save('03-interconnect-id')
