"""A3 teaching diagrams: editable draw.io XML, exported by local draw.io.

Samples describe values BEFORE Tn. Changes are drawn AFTER the preceding edge.
The reference PNG defines visual style, never protocol behavior.
"""
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'image/axi-a3'
EXE = Path(r'C:\Program Files\draw.io\draw.io.exe')
BLUE, GREEN, ORANGE = '#123a91', '#176622', '#c57900'
PALE_BLUE, PALE_GREEN, PALE_ORANGE = '#edf4ff', '#edf7ed', '#fff2d5'


class Figure:
    def __init__(self, name, title, height):
        self.name, self.height = name, height
        self.doc = ET.Element('mxfile', host='app.diagrams.net')
        dia = ET.SubElement(self.doc, 'diagram', name=title)
        model = ET.SubElement(dia, 'mxGraphModel', page='1', pageWidth='1440', pageHeight=str(height))
        self.root = ET.SubElement(model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0')
        ET.SubElement(self.root, 'mxCell', id='1', parent='0')
        self.counter = 2
        self.box(0, 0, 1440, height, '', '#ffffff', 'none')
        self.text(30, 20, 1380, 70, title, 44, bold=True)

    def cell(self, **kw):
        c = ET.SubElement(self.root, 'mxCell', id=str(self.counter), parent='1', **kw)
        self.counter += 1
        return c

    def box(self, x, y, w, h, label, fill='#ffffff', stroke='#111111', size=32, color='#111111', rounded=False, bold=False):
        c = self.cell(value=label, vertex='1', style=f'rounded={int(rounded)};arcSize=10;whiteSpace=wrap;html=0;fontFamily=Microsoft YaHei;fontSize={size};fontColor={color};fontStyle={int(bold)};fillColor={fill};strokeColor={stroke};strokeWidth=2;align=center;verticalAlign=middle;spacing=8;')
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as':'geometry'})

    def text(self, x, y, w, h, label, size=32, color='#111111', bold=False):
        self.box(x,y,w,h,label,'none','none',size,color,bold=bold)

    def line(self, points, color='#111111', dash=False, arrow=False, width=3):
        c = self.cell(edge='1', style=f'endArrow={"block" if arrow else "none"};endFill=1;startArrow=none;rounded=0;strokeWidth={width};strokeColor={color};dashed={int(dash)};')
        g = ET.SubElement(c, 'mxGeometry', relative='1', **{'as':'geometry'})
        for p, role in [(points[0],'sourcePoint'),(points[-1],'targetPoint')]:
            ET.SubElement(g, 'mxPoint', x=str(p[0]), y=str(p[1]), **{'as':role})
        if len(points)>2:
            a=ET.SubElement(g,'Array',**{'as':'points'})
            for x,y in points[1:-1]: ET.SubElement(a,'mxPoint',x=str(x),y=str(y))

    def save(self):
        OUT.mkdir(parents=True,exist_ok=True)
        src=OUT/(self.name+'.drawio')
        ET.ElementTree(self.doc).write(src,encoding='utf-8',xml_declaration=True)
        dst=src.with_suffix('.png')
        p=subprocess.run([str(EXE),'--export','--format','png','--width','1440','--output',str(dst),str(src)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        if p.returncode or not dst.exists(): raise RuntimeError(p.stdout+p.stderr)
        print(dst.name,flush=True)


SCENARIOS=[]


def timing(name,title,rows,events,notes,rule,assumption,reset=False):
    n=len(rows[0][1]); left=235; right=1390; step=(right-left-45)/(n-0.5)
    edges=[left+45+i*step for i in range(n)]
    top=235; pitch=86; bottom=top+pitch*(len(rows)+1)
    fig=Figure(name,title,bottom+385)
    fig.text(30,92,1380,55,'时间向右；虚线为采样上升沿；按边沿前取值判断，信号在沿后更新。',32)
    if reset:
        split=edges[1]+18
        fig.box(left,top-12,split-left,bottom-top+40,'',PALE_BLUE,'none')
        fig.box(split,top-12,right-split,bottom-top+40,'',PALE_GREEN,'none')
    for idx,status in events.items():
        fig.box(edges[idx-1]-24,top-18,48,bottom-top+46,'',PALE_ORANGE if status=='wait' else '#dcedd9','none')
    for i,x in enumerate(edges):
        fig.text(x-36,top-65,72,45,f'T{i+1}',34,bold=True)
        fig.line([(x,top-10),(x,bottom+28)],'#555555',True,width=1)
        fig.line([(x,top+55),(x,top+4)],arrow=True,width=2)
    fig.text(15,top-5,205,55,'ACLK',32,bold=True)
    points=[(left,top+44)]
    for x in edges: points.extend([(x,top+44),(x,top),(x+step*.43,top),(x+step*.43,top+44)])
    points.append((right,top+44));fig.line(points)
    for row,(label,values,kind) in enumerate(rows):
        y=top+pitch*(row+1)
        fig.text(5,y-7,220,65,'PAYLOAD' if label=='INFORMATION' else label,32,bold=True)
        if kind=='bit':
            points=[(left,y+(0 if values[0] else 36))]
            for i in range(1,n):
                if values[i]!=values[i-1]:
                    x=edges[i-1]+18
                    points.extend([(x,y+(0 if values[i-1] else 36)),(x+12,y+(0 if values[i] else 36))])
            points.append((right,y+(0 if values[-1] else 36)));fig.line(points)
        else:
            starts=[0]+[i for i in range(1,n) if values[i]!=values[i-1]]+[n]
            for a,b in zip(starts,starts[1:]):
                x1=left if a==0 else edges[a-1]+24
                x2=right if b==n else edges[b-1]+24
                val=values[a]
                if val=='—': fig.line([(x1,y+18),(x2,y+18)],'#777777',width=2)
                else:
                    fig.line([(x1,y+18),(x1+9,y),(x2-9,y),(x2,y+18),(x2-9,y+36),(x1+9,y+36),(x1,y+18)],width=2)
                    fig.text(x1+5,y-6,x2-x1-10,48,str(val),32)
    if reset:
        fig.text(left,bottom-25,split-left,50,'复位有效',32,BLUE,True)
        fig.text(split,bottom-25,right-split,50,'复位已释放：正常工作',32,GREEN,True)
    w=(1380-20*(len(notes)-1))/len(notes)
    for i,(label,status) in enumerate(notes):
        color=ORANGE if status=='wait' else GREEN if status=='ok' else BLUE
        fill=PALE_ORANGE if status=='wait' else PALE_GREEN if status=='ok' else PALE_BLUE
        fig.box(30+i*(w+20),bottom+58,w,130,label,fill,color,32,color,True)
    fig.box(30,bottom+210,1380,72,rule,'#ffffff',BLUE,32,BLUE,True,True)
    fig.box(30,bottom+300,1380,65,assumption,'#ffffff','#888888',32)
    fig.save();SCENARIOS.append({'name':name,'rows':rows,'events':events})


def table(name,title,headers,rows,widths,footer):
    height=195+90*(len(rows)+1)+120
    fig=Figure(name,title,height)
    x=30
    for head,w in zip(headers,widths):fig.box(x,115,w,85,head,PALE_BLUE,BLUE,32,BLUE,bold=True);x+=w
    for i,row in enumerate(rows):
        x=30
        for val,w in zip(row,widths):
            fig.box(x,200+i*90,w,90,val,'#ffffff' if i%2 else '#f5f8fb','#cbd5e1',32);x+=w
    fig.box(30,height-100,1380,75,footer,PALE_GREEN,GREEN,32,GREEN,True)
    fig.save()


def main():
    timing('v2-01-reset','AXI Clock 与 Reset：一次读地址握手',[
        ('ARESETn',[0,0,1,1,1,1],'bit'),('ARVALID',[0,0,0,1,1,0],'bit'),('ARREADY',[0,0,0,0,1,1],'bit'),
        ('ARADDR',['—','—','—','0x1000','0x1000','—'],'bus'),('AWVALID /\nWVALID',[0]*6,'bit'),('RVALID /\nBVALID',[0]*6,'bit')],{4:'wait',5:'ok'},
        [('T2 沿后释放复位\nT3 沿后拉高 ARVALID','info'),('T4：VALID=1，READY=0\n地址保持，继续等待','wait'),('T5：VALID=1，READY=1\n读地址传输一次','ok')],
        '复位期间：主设备的三个 VALID、从设备的两个 VALID 均为 0。',
        '主设备驱动 AR；从设备驱动 ARREADY；其余通道空闲，读数据在图外返回。',True)
    timing('v2-02-valid-first','握手①：VALID 先到，等待期间保持信息',[
        ('VALID',[0,1,1,1,0],'bit'),('READY',[0,0,0,1,1],'bit'),('INFORMATION',['—','A','A','A','—'],'bus')],{2:'wait',3:'wait',4:'ok'},
        [('T2、T3：等待\nVALID=1，READY=0','wait'),('T4：成功握手\nA 只传输一次','ok')],
        '等待期间 VALID 不撤销，当前地址 / 数据 / 控制信息保持稳定。',
        '发送方驱动 VALID 与信息；接收方驱动 READY；A 表示当前完整通道载荷。')
    timing('v2-03-ready-first','握手②：READY 先到，信息到达即可接收',[
        ('VALID',[0,0,1,0],'bit'),('READY',[0,1,1,1],'bit'),('INFORMATION',['—','—','A','—'],'bus')],{3:'ok'},
        [('T2：READY=1\n没有 VALID，不发生传输','info'),('T3：两者均为 1\n完成 A 的传输','ok')],
        'READY 表示接收能力；只有 READY=1 不能构成一次传输。',
        '发送方驱动 VALID 与信息；接收方驱动 READY；复位已结束。')
    timing('v2-04-together','握手③：同时就绪，也可连续传输',[
        ('VALID',[0,1,1,0],'bit'),('READY',[0,1,1,1],'bit'),('INFORMATION',['—','A','B','—'],'bus')],{2:'ok',3:'ok'},
        [('T2：A 成功传输\n两信号在 T1 沿后拉高','ok'),('T3：B 成功传输\nVALID 无需先降为 0','ok')],
        '连续两个上升沿 VALID、READY 均为 1，表示两次传输。',
        '发送方驱动 VALID 与信息；接收方驱动 READY；A、B 是不同载荷。')
    scenarios=[('v2-06-write-aw-first','AW 先到',2,3),('v2-07-write-w-first','W 先到',3,2),('v2-08-write-together','AW 与 W 同拍',2,2)]
    for name,label,aw,w in scenarios:
        def pulse(k):return [int(i==k) for i in range(1,7)]
        timing(name,'AXI4 单拍写：'+label,[
            ('AWVALID',pulse(aw),'bit'),('AWREADY',[1]*6,'bit'),('WVALID',pulse(w),'bit'),('WREADY',[1]*6,'bit'),
            ('WLAST',pulse(w),'bit'),('BVALID',[0,0,0,1,1,0],'bit'),('BREADY',[0,0,0,0,1,1],'bit')],{4:'wait',5:'ok'},
            [(f'T{aw}：地址握手\nT{w}：唯一数据拍握手','info'),('T4：响应等待\nBVALID=1，BREADY=0','wait'),('T5：响应握手\n一笔写事务完成','ok')],
            'BVALID 必须在地址握手及末拍数据握手均完成之后产生。',
            '主：AWVALID/WVALID/WLAST/BREADY；从：其余；AWLEN=0，BRESP=OKAY。')
    timing('v2-09-read','AXI4 两拍读：末拍等待不等于重复传输',[
        ('ARVALID',[0,1,0,0,0,0,0],'bit'),('ARREADY',[1]*7,'bit'),('RVALID',[0,0,1,1,1,1,0],'bit'),
        ('RREADY',[0,0,1,0,0,1,1],'bit'),('RDATA',['—','—','D0','D1','D1','D1','—'],'bus'),('RLAST',[0,0,0,1,1,1,0],'bit')],{3:'ok',4:'wait',5:'wait',6:'ok'},
        [('T2：AR 握手\nT3：接收 D0','ok'),('T4、T5：末拍等待\nD1、RLAST 保持','wait'),('T6：接收 D1\n两拍读事务完成','ok')],
        '读数据在读地址握手后返回；RLAST 随最后一拍成功握手才结束突发。',
        '主：ARVALID/RREADY；从：其余；ARLEN=1，ARSIZE=2，INCR，RRESP=OKAY。')
    fig=Figure('v2-05-channels','AXI 五通道：方向独立，事务存在依赖',800)
    fig.box(55,170,255,470,'Master\n主设备',PALE_BLUE,BLUE,40,BLUE,True,True)
    fig.box(1130,170,255,470,'Slave\n从设备',PALE_GREEN,GREEN,40,GREEN,True,True)
    for i,(label,forward) in enumerate([('AW · 写地址',True),('W · 写数据',True),('B · 写响应',False),('AR · 读地址',True),('R · 读数据与响应',False)]):
        y=205+i*88;color=BLUE if forward else '#743c98'
        fig.text(380,y-32,680,50,label,34,color,True)
        fig.line([(330,y+27),(1110,y+27)] if forward else [(1110,y+27),(330,y+27)],color,arrow=True)
    fig.box(40,690,1360,75,'每条箭头都是一套 VALID / READY 握手；READY 的方向与箭头相反。','#ffffff',BLUE,32,BLUE,True)
    fig.save()
    table('v2-10-addresses','突发地址：同样 4 拍，不同地址规则',
        ['类型 / 起点','第 1 拍','第 2 拍','第 3 拍','第 4 拍'],[
            ['FIXED / 0x100C','0x100C','0x100C','0x100C','0x100C'],
            ['INCR / 0x100C','0x100C','0x1010','0x1014','0x1018'],
            ['WRAP / 0x100C','0x100C','0x1000','0x1004','0x1008'],
            ['INCR / 0x1001','0x1001','0x1004','0x1008','0x100C']],
        [340,260,260,260,260],'AxSIZE=2：最大 4 Byte/拍；AxLEN=3：4 拍；WRAP 容器为 16 Byte。')
    table('v2-11-boundary','4KB 边界：最后一个可能访问的字节也要检查',
        ['INCR 配置','末拍地址 / 最高字节','结果'],[
            ['起点 0x0FF0\n4 Byte × 4 拍','0x0FFC / 0x0FFF','合法：都在同一页'],
            ['起点 0x0FF0\n4 Byte × 5 拍','0x1000 / 0x1003','非法：跨过 0x1000'],
            ['起点 0x0FFF\n最大 4 Byte × 1 拍','0x0FFF / 0x0FFF','合法：首拍仅 lane 3']],
        [470,470,440],'地址窗口不能跨界；减少 WSTRB 有效位不能使一个跨界突发变合法。')
    table('v2-12-strobes','WSTRB：每一位控制一个字节通道',
        ['字节通道','WDATA 位段','WSTRB=0011'],[
            ['lane 0','[7:0]','bit 0=1：写入'],['lane 1','[15:8]','bit 1=1：写入'],
            ['lane 2','[23:16]','bit 2=0：不写'],['lane 3','[31:24]','bit 3=0：不写']],
        [440,440,500],'本例：32-bit 总线，AWADDR=0x1000，AWSIZE=2；仅更新 0x1000、0x1001。')
    table('v2-13-unaligned','非对齐 INCR：首拍不补满，下一拍回到对齐地址',
        ['拍号 / 地址','可用字节通道','写入时 WSTRB'],[
            ['1 / 0x1001','lane 1、2、3','1110：写 3 Byte'],
            ['2 / 0x1004','lane 0、1、2、3','1111：写 4 Byte'],
            ['3 / 0x1008','lane 0、1、2、3','1111：写 4 Byte'],
            ['4 / 0x100C','lane 0、1、2、3','1111：写 4 Byte']],
        [460,460,460],'32-bit 总线；AxSIZE=2，AxLEN=3；最大有效范围为 0x1001～0x100F，共 15 Byte。')
    (OUT/'v2-timing-samples.json').write_text(json.dumps(SCENARIOS,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': main()
