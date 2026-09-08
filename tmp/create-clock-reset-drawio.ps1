$parts = [System.Collections.Generic.List[string]]::new()
$parts.Add('<mxfile host="app.diagrams.net"><diagram name="Clock and Reset" id="axi-clock-reset"><mxGraphModel dx="1400" dy="1000" grid="1" gridSize="10" page="1" pageScale="1" pageWidth="1400" pageHeight="1000"><root><mxCell id="0"/><mxCell id="1" parent="0"/>')
$script:n=1
function Box($text,$x,$y,$w,$h,$style) {
 $script:n++; $v=[System.Security.SecurityElement]::Escape($text)
 $parts.Add("<mxCell id=`"$script:n`" value=`"$v`" style=`"$style`" vertex=`"1`" parent=`"1`"><mxGeometry x=`"$x`" y=`"$y`" width=`"$w`" height=`"$h`" as=`"geometry`"/></mxCell>")
}
function Line($coords,$color='#25324A',$width=3,$dash=0) {
 $script:n++; $p=$coords.Split(' '); $a=$p[0].Split(','); $b=$p[-1].Split(',')
 $mid=''; for($i=1;$i -lt $p.Count-1;$i++){ $q=$p[$i].Split(','); $mid+="<mxPoint x=`"$($q[0])`" y=`"$($q[1])`"/>" }
 $parts.Add("<mxCell id=`"$script:n`" style=`"endArrow=none;startArrow=none;strokeColor=$color;strokeWidth=$width;dashed=$dash;rounded=0;`" edge=`"1`" parent=`"1`"><mxGeometry relative=`"1`" as=`"geometry`"><mxPoint x=`"$($a[0])`" y=`"$($a[1])`" as=`"sourcePoint`"/><mxPoint x=`"$($b[0])`" y=`"$($b[1])`" as=`"targetPoint`"/><Array as=`"points`">$mid</Array></mxGeometry></mxCell>")
}
$t='text;html=0;strokeColor=none;fillColor=none;fontFamily=Microsoft YaHei;fontSize=18;fontColor=#25324A;align=left;verticalAlign=middle;'
Box 'AXI Clock 与 Reset：一次读地址握手' 50 25 1250 55 ($t+'fontSize=30;fontStyle=1;')
Box '案例：复位 → 发起请求 → 等待 READY → 上升沿完成传输' 50 85 1250 35 $t
Box '' 235 140 405 555 'fillColor=#EDF3FC;strokeColor=none;'
Box '' 640 140 670 555 'fillColor=#F0F8F2;strokeColor=none;'
Box '复位期间：ARESETn = 0' 265 140 365 35 $t
Box '正常工作：ARESETn = 1' 740 140 500 35 $t
$edges=280,460,640,820,1000,1180
for($i=0;$i -lt 6;$i++){ $x=$edges[$i]; Box "T$($i+1) ↑" ($x-28) 185 85 30 ($t+'fontStyle=1;'); Line "$x,220 $x,690" '#B0BCCB' 1 1 }
Box '' 806 220 28 470 'fillColor=#FDE7B1;strokeColor=none;opacity=45;'
Box '' 986 220 28 470 'fillColor=#B9E5C4;strokeColor=none;opacity=55;'
$labels=@('ACLK','ARESETn','ARVALID','ARREADY','AWVALID / WVALID','RVALID / BVALID')
$ys=245,325,405,485,565,645
for($i=0;$i -lt 6;$i++){Box $labels[$i] 35 ($ys[$i]-8) 200 40 ($t+'fontSize=17;fontStyle=1;')}
$c='235,270'; foreach($x in $edges){$c+=" $x,270 $x,240 $($x+70),240 $($x+70),270"};$c+=' 1310,270'; Line $c
Line '235,350 640,350 640,320 1310,320' '#315FA4'
Line '235,430 720,430 720,400 1080,400 1080,430 1310,430' '#315FA4'
Line '235,510 900,510 900,480 1310,480' '#267348'
Line '235,590 1310,590'
Line '235,670 1310,670'
Box '0' 300 315 35 30 $t
Box '1' 690 310 35 30 $t
Box 'T3：同步释放复位' 510 700 280 35 $t
Box "T4：ARVALID=1，ARREADY=0`n等待，尚未传输" 720 750 310 75 ($t+'fillColor=#FFF4D9;strokeColor=#D7A33A;rounded=1;align=center;fontSize=17;')
Box "T5：ARVALID=1，ARREADY=1`n在此上升沿完成传输" 1040 750 310 75 ($t+'fillColor=#E8F5EB;strokeColor=#45935D;rounded=1;align=center;fontSize=17;')
Box "Master 复位检查`nARVALID = AWVALID = WVALID = 0" 50 850 620 75 ($t+'strokeColor=#8EA7CC;rounded=1;align=center;')
Box "Slave 复位检查`nRVALID = BVALID = 0" 700 850 620 75 ($t+'strokeColor=#8EA7CC;rounded=1;align=center;')
Box '注：其他通道在本例中保持空闲；ARREADY 在复位期间为 0 仅为示例。波形为教学示意。' 50 945 1300 30 ($t+'fontSize=16;')
$parts.Add('</root></mxGraphModel></diagram></mxfile>')
$dest=Join-Path (Get-Location) 'images/axi-a3-clock-reset.drawio'
[System.IO.File]::WriteAllText($dest,($parts -join "`n"),[System.Text.UTF8Encoding]::new($false))
[xml]$check=Get-Content -LiteralPath $dest -Raw
Write-Output "Created: $dest; cells: $($check.mxfile.diagram.mxGraphModel.root.mxCell.Count)"
