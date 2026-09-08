"""A6 teaching diagrams, editable sources and local draw.io PNG exports."""
from pathlib import Path
import subprocess
import draw_a4

draw_a4.OUT = Path(__file__).resolve().parents[1] / 'image' / 'axi-a6'
from draw_a4 import Diagram


def main():
    d = Diagram('01-ordering-scopes', '先问：你要保证哪一种顺序？', 1000)
    d.text(30, 95, 1020, 85, '同一主设备先发 A，再发 B；读、写分别讨论。\n教学重绘｜条件比较图，不表示时钟或延迟。')
    rows = [
        ('请求保持次序', '同通道、同 ID、同一目的地\n具体地址范围见 A6.6.2', '#dbeafe'),
        ('响应返回次序', '同方向、同 ID\n即使目的地不同，响应仍按请求次序返回', '#f3e8ff'),
        ('访问效果的观察次序', 'Memory：按位置；Peripheral：按区域\n不能仅凭响应保序，推出跨地址写入保序', '#dcfce7'),
        ('更强的可选写保证', 'Ordered_Write_Observation=True\n同主设备、同 ID 的写，可跨目的地 / 地址保序', '#ffedd5'),
    ]
    for i, (a, b, c) in enumerate(rows):
        y = 215 + i * 175
        d.box(30, y, 1020, 55, a, c)
        d.box(30, y + 55, 1020, 100, b, '#f8fafc')
    d.text(30, 925, 1020, 50, 'ID：事务标识；蓝：请求；紫：响应；绿：访问效果。')
    d.save()

    # Reuse the established timing renderer without executing A5 examples.
    source = (Path(__file__).parent / 'draw_a5.py').read_text(encoding='utf-8')
    scope = {'__file__': __file__}
    exec(source.split("timing('01-read-reordering'")[0], scope)
    scope['OUT'] = draw_a4.OUT
    scope['timing']('02-write-then-read', '先写后读：等到写响应，再发依赖的读', [
        ('AWVALID',[1,0,0,0,0,0,0,0],'bit',scope['BLUE']),
        ('AWREADY',[1,1,1,1,1,1,1,1],'bit',scope['GREEN']),
        ('WVALID',[1,0,0,0,0,0,0,0],'bit',scope['BLUE']),
        ('WREADY',[1,1,1,1,1,1,1,1],'bit',scope['GREEN']),
        ('BVALID',[0,1,1,0,0,0,0,0],'bit',scope['PURPLE']),
        ('BREADY',[0,0,1,1,1,1,1,1],'bit',scope['BLUE']),
        ('ARVALID',[0,0,0,1,0,0,0,0],'bit',scope['BLUE']),
        ('ARREADY',[1,1,1,1,1,1,1,1],'bit',scope['GREEN']),
        ('RVALID',[0,0,0,0,1,1,1,0],'bit',scope['PURPLE']),
        ('RREADY',[1,1,1,1,0,0,1,1],'bit',scope['BLUE']),
        ('RDATA',['—','—','—','—','1','1','1','—'],'bus',scope['PURPLE']),
    ], [
        'T1 接收地址和写数据；T2 等 B；T3 写完成响应。',
        'T4 接收读地址；T5/T6 等待；T7 接收唯一读数据拍。',
        '主设备驱动 AW / W / AR 载荷及 BREADY / RREADY。',
        '从设备驱动各请求 READY、B / R 载荷及其 VALID。',
        '省略固定值：AWADDR=ARADDR=0x1000，WDATA=1。',
        'AWID=ARID=BID=RID=0；AWLEN=ARLEN=0（1 拍）。',
        'AWSIZE=ARSIZE=2（4 字节）；WLAST=RLAST=1。',
        'AWBURST=ARBURST=INCR（递增）；WSTRB=1111。',
        'WSTRB 为二进制，4 字节全有效；BRESP=RRESP=OKAY。',
        'AWCACHE=ARCACHE=0010（Normal 非缓存、非缓冲）。',
        'AWLOCK=ARLOCK=0（普通）；AWPROT=ARPROT=000。',
        '复位已释放；其他可选字段合法固定；无其他写入者。',
        '等候时保持载荷；此图为一种合法调度，无固定延迟含义。',
    ], 8)
    src = draw_a4.OUT / '02-write-then-read.drawio'
    subprocess.run([r'C:\Program Files\draw.io\draw.io.exe', '--export', '--format', 'png',
                    '--width', '1080', '--output', str(src.with_suffix('.png')), str(src)],
                   check=True, capture_output=True, timeout=60,
                   creationflags=subprocess.CREATE_NO_WINDOW)

    d = Diagram('03-early-response', '提前回应以后，责任仍留在中间节点', 1080)
    d.text(30, 95, 1020, 85, '前提：允许提前响应的 Bufferable 写，无下游观察者。\n教学重绘｜概念阶段图，不表示周期或固定延迟。')
    rows = [
        ('① 主设备发出写 W1', '中间节点接收并保存数据', '#dbeafe'),
        ('② 中间节点向上游提前回应', '仍要遵守同 ID 的写响应次序', '#f3e8ff'),
        ('③ 最终目的地尚未完成', 'Normal：守住相同或重叠 Memory 位置\nDevice：守住同一 Peripheral 区域', '#ffedd5'),
        ('④ 向下游传播，并收到下游写响应', '此前持续负责 W1 的顺序与可观察性', '#dcfce7'),
    ]
    for i, (a, b, c) in enumerate(rows):
        y = 215 + i * 175
        d.box(30, y, 1020, 140, a + '\n' + b, c)
        if i < 3:
            d.text(510, y + 140, 60, 35, '↓')
    d.text(30, 940, 1020, 105, '不能丢弃尚未向下游传播的数据。\nDevice 写不能等待另一笔请求到来才继续传播。\n蓝：主设备；橙：互连 / 中间节点；紫：响应；绿：目的地。')
    d.save()


if __name__ == '__main__':
    main()
