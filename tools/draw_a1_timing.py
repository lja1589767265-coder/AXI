"""Render protocol-consistent teaching waveforms; not simulation captures."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = 'C:/Windows/Fonts/msyh.ttc'
BLUE, GREEN, GRAY = '#2463ad', '#158060', '#697586'

def render(name, title, rows, events):
    n = 6
    left, step, top, pitch = 250, 128, 180, 86
    bottom = top + pitch * (len(rows) + 1)
    im = Image.new('RGB', (1080, bottom + 260), 'white')
    d = ImageDraw.Draw(im)
    def txt(x, y, s, size=32, fill='#172b42'):
        d.text((x, y), s, font=ImageFont.truetype(FONT, size), fill=fill)
    txt(35, 24, title, 38)
    txt(35, 85, '教学时序｜非仿真截图｜虚线处为采样上升沿', 32, GRAY)
    for j in range(n):
        x = left + (j + 1) * step
        for yy in range(top-20, bottom, 14):
            d.line((x, yy, x, min(yy+7, bottom)), fill='#dce3eb', width=2)
        txt(x - 26, top - 65, f'T{j+1}', 30)
    def bit(y, values, color):
        # Each cell ends on its sampling edge. Changes occur 8 px after
        # the preceding edge, so the previous value is sampled unambiguously.
        pts = []
        for j, v in enumerate(values):
            a, b = left+j*step+8, left+(j+1)*step+8
            level = y + (4 if v else 38)
            if pts:
                pts.append((a, pts[-1][1]))
            pts.extend([(a, level), (b, level)])
        d.line(pts, fill=color, width=3)
    txt(35, top, 'CLK', 32)
    pts = [(left, top+4)]
    for j in range(n):
        a, b = left+j*step, left+(j+1)*step
        pts.extend([(a+step/2, top+4), (a+step/2, top+38),
                    (b, top+38), (b, top+4)])
    d.line(pts, fill=GRAY, width=3)
    for i, (label, values, kind, color) in enumerate(rows):
        y = top + (i+1)*pitch
        txt(28, y, label, 31, color)
        if kind == 'bit':
            bit(y, values, color)
        else:
            j = 0
            while j < n:
                k = j+1
                while k<n and values[k] == values[j]:
                    k += 1
                a, b = left+j*step+8, left+k*step+8
                d.polygon([(a,y+21),(a+6,y),(b-6,y),(b,y+21),
                           (b-6,y+42),(a+6,y+42)],
                          fill='#f3f6fa', outline=color, width=2)
                text = values[j]
                font = ImageFont.truetype(FONT, 30)
                w = d.textbbox((0,0), text, font=font)[2]
                txt((a+b-w)/2,y+1,text,30,color)
                j = k
    for i, line in enumerate(events):
        txt(35, bottom+25+i*45, line, 30)
    txt(35, bottom+210, '蓝：主设备驱动   绿：从设备/响应路径   —：无关值', 28, GRAY)
    path = ROOT/'images'/name
    path.parent.mkdir(exist_ok=True)
    im.save(path)
    print(path)

render('a1-ahb-wait.png', 'AHB-Lite：A 的数据等待，B 的地址也被保持', [
 ('HADDR',['A','B','B','B','—','—'],'bus',BLUE),
 ('HTRANS',['NONSEQ','NONSEQ','NONSEQ','NONSEQ','IDLE','IDLE'],'bus',BLUE),
 ('HREADY',[1,0,0,1,1,1],'bit',GREEN),
 ('HRDATA',['—','—','—','D(A)','D(B)','—'],'bus',GREEN),
], ['T1：接收 A 地址；随后展示 B 地址。',
    'T2、T3：HREADY=0，A 未完成，B 尚未被接受。',
    'T4：A 完成且 B 被接受；T5：B 完成。'])

render('a1-axi-outstanding.png', 'AXI：A 数据未返回，B 请求已被接收', [
 ('ARADDR',['A','B','—','—','—','—'],'bus',BLUE),
 ('ARVALID',[1,1,0,0,0,0],'bit',BLUE),
 ('ARREADY',[1,1,1,1,1,1],'bit',GREEN),
 ('RDATA',['—','—','—','D(A)','D(B)','—'],'bus',GREEN),
 ('RVALID',[0,0,0,1,1,0],'bit',GREEN),
 ('RREADY',[1,1,1,1,1,1],'bit',BLUE),
 ('RLAST',[0,0,0,1,1,0],'bit',GREEN),
], ['T1：AR 握手接收 A；T2：AR 握手接收 B。',
    'T2 后至 T4 前：两笔事务均未完成。',
    'T4、T5：R 握手，依次完成 A、B（均为单拍）。'])
