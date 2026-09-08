"""Check A3 artifact references, documented address examples and teaching samples.

This checks static examples, not an RTL implementation or all AXI rules.
"""
from pathlib import Path
import re
import json
import hashlib
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A3.md'
body=DOC.read_text(encoding='utf-8')

# Preserve the user-provided source exactly.
source=ROOT/'AXI_A3_Single_Interface_Requirements_学习笔记.md'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='bb0782f9a33969fbdc3f81cb594b690e44aba1ae0beea3a44a1647bb9027b7bc'
assert body.count('<details>')==body.count('</details>')==10
assert len(re.findall(r'^# ',body,re.M))==1
assert not re.search('[┌┐└┘├┤─│↑↓→←]',body)
assert 'http://' not in body and 'https://' not in body
assert body.count('```')%2==0
for block in re.findall(r'<details>(.*?)</details>',body,re.S):
    assert re.search(r'^  <summary>.+</summary>$',block,re.M)
    assert '\n\n  <span ' in block
    assert block.endswith('\n\n')
refs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body)
assert len(refs)==len(set(refs))==13
for ref in refs:
    assert '/v2-' in ref
    p=ROOT/ref
    assert p.exists() and p.with_suffix('.drawio').exists()
    root=ET.parse(p.with_suffix('.drawio')).getroot()
    for cell in root.iter('mxCell'):
        m=re.search(r'fontSize=(\d+)',cell.get('style',''))
        if m: assert int(m[1])>=32
    with Image.open(p) as image:
        image.verify()
    with Image.open(p) as image:
        assert image.width==1440
assert DOC.name in (ROOT/'README.md').read_text(encoding='utf-8')

# Execute the published algorithm, then compare with independently hand-derived cases.
code=re.search(r'```python\n(.*?)\n```',body,re.S)[1]
scope={}
exec(compile(code,str(DOC),'exec'),scope)
describe=scope['describe_beats']
cases=[
    ((0x1001,2,4,4,'INCR'),[(0x1001,1,3),(0x1004,0,3),(0x1008,0,3),(0x100c,0,3)]),
    ((0x100c,2,4,4,'WRAP'),[(0x100c,0,3),(0x1000,0,3),(0x1004,0,3),(0x1008,0,3)]),
    ((0x1001,2,3,4,'FIXED'),[(0x1001,1,3)]*3),
    ((0,0,5,4,'INCR'),[(0,0,0),(1,1,1),(2,2,2),(3,3,3),(4,0,0)]),
    ((4,2,3,8,'INCR'),[(4,4,7),(8,0,3),(12,4,7)]),
    ((4,2,4,8,'WRAP'),[(4,4,7),(8,0,3),(12,4,7),(0,0,3)]),
    ((7,2,5,8,'INCR'),[(7,7,7),(8,0,3),(12,4,7),(16,0,3),(20,4,7)]),
    ((0xfff,2,1,4,'INCR'),[(0xfff,3,3)]),
]
for args,expected in cases: assert describe(*args)==expected,(args,describe(*args))
for start,length,expected in [(0xff0,4,True),(0xff0,5,False),(0xfff,1,True)]:
    beats=describe(start,2,length,4,'INCR')
    addresses=[a+(lane-lo) for a,lo,hi in beats for lane in range(lo,hi+1)]
    assert (len({a//4096 for a in addresses})==1)==expected
assert sum(hi-lo+1 for a,lo,hi in describe(0x1001,2,4,4,'INCR'))==15

# Sample arrays describe the BEFORE-edge values represented in draw.io.
sample_path=ROOT/'image/axi-a3/v2-timing-samples.json'
samples=json.loads(sample_path.read_text(encoding='utf-8')) if sample_path.exists() else []
summary={}
for s in samples:
    rows={label:values for label,values,kind in s['rows']}
    transfers={}
    for prefix in ('','AW','W','B','AR','R'):
        v,r=prefix+'VALID',prefix+'READY'
        if v not in rows or r not in rows:continue
        transfers[prefix or 'generic']=[i+1 for i,(a,b) in enumerate(zip(rows[v],rows[r])) if a and b]
        for i in range(len(rows[v])-1):
            if rows[v][i] and not rows[r][i]:
                assert rows[v][i+1]==1,(s['name'],v,i)
                payloads={'':['INFORMATION'],'AR':['ARADDR'],'R':['RDATA','RLAST'],'W':['WLAST']}.get(prefix,[])
                for p in payloads:
                    if p in rows:assert rows[p][i+1]==rows[p][i],(s['name'],p,i)
    if 'write-' in s['name']:
        assert len(transfers['AW'])==len(transfers['W'])==len(transfers['B'])==1
        bvalid=rows['BVALID'].index(1)+1
        assert bvalid>max(transfers['AW'][0],transfers['W'][0])
        assert rows['WLAST'][transfers['W'][0]-1]==1
        assert transfers['B']==[5]
    if s['name']=='v2-09-read':
        assert transfers=={'AR':[2],'R':[3,6]}
        assert rows['RVALID'].index(1)+1>transfers['AR'][0]
        assert [rows['RLAST'][i-1] for i in transfers['R']]==[0,1]
    if s['name']=='v2-01-reset':
        assert transfers['AR']==[5]
        assert rows['ARVALID'].index(1)>rows['ARESETn'].index(1)
        for i,reset in enumerate(rows['ARESETn']):
            if not reset:
                for name in ('ARVALID','AWVALID /\nWVALID','RVALID /\nBVALID'):assert rows[name][i]==0
    summary[s['name']]=transfers
print(json.dumps({'status':'PASS','figures':len(refs),'editable_sources':len(refs),'self_tests':10,'address_cases':len(cases),'boundary_cases':3,'timing':summary,'original_note':'unchanged'},ensure_ascii=False,indent=2))
