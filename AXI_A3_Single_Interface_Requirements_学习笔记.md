# AXI A3 章节介绍：Single Interface Requirements

A3 是这份 AXI 协议里最核心、最值得反复看的章节之一。它的标题是 **Single Interface Requirements**，重点讲的是：

> **一个 AXI Master 和一个 AXI Slave 直接交互时，最基本的协议规则是什么。**

A3 主要分成 4 大块：

1. **A3.1 Clock and reset**：时钟、复位
2. **A3.2 Basic read and write transactions**：VALID/READY 握手
3. **A3.3 Relationships between the channels**：5 个通道之间的依赖关系
4. **A3.4 Transaction structure**：Burst、LEN、SIZE、BURST、WSTRB、非对齐访问、RESP 等

这基本就是你后面看 AXI 波形、写 driver/monitor、做 protocol checker 的基础。

---

## 1. A3.1：Clock 和 Reset

AXI 接口只有一个全局时钟：

```text
ACLK
```

AXI 信号都是在 **ACLK 上升沿采样**的。

可以简单理解成：

```text
        ↑           ↑           ↑
ACLK ___|‾‾‾|_______|‾‾‾|_______|‾‾‾
        T1          T2          T3
```

协议真正判断一次传输有没有发生，是看某一个上升沿：

```text
VALID == 1
READY == 1
```

如果两者同时为 1：

```text
transfer occurs
```

### Reset

AXI 的复位：

```text
ARESETn
```

是：

```text
低有效
```

也就是：

```text
ARESETn = 0 → reset
ARESETn = 1 → normal
```

协议中有一个很重要的要求：

复位期间，Master 必须把：

```text
ARVALID = 0
AWVALID = 0
WVALID  = 0
```

Slave 必须把：

```text
RVALID = 0
BVALID = 0
```

所以从验证角度，这几个信号是 reset checker 很典型的检查点。

---

# 2. A3.2：VALID / READY 握手

这是整个 AXI 最核心的规则。

AXI 五个通道：

```text
AW
W
B
AR
R
```

全部使用同一种握手机制：

```text
VALID + READY
```

可以记成：

```text
发送方：VALID
接收方：READY
```

只有：

```text
VALID && READY
```

在 ACLK 上升沿成立的时候，才完成一次 transfer。

例如：

```text
VALID = 1
READY = 1
```

那么：

```text
        ↑
ACLK ___|‾‾‾

VALID __/‾‾‾‾
READY __/‾‾‾‾
        ↑
     transfer
```

---

## 3 个最基本的握手情况

A3 给了三个典型例子。

### 情况 1：VALID 先来

```text
VALID ──────┐
            └────────────
READY ────────────┐
                  └──────
                   ↑
                transfer
```

发送方数据准备好了：

```text
VALID = 1
```

但是接收方还没准备好：

```text
READY = 0
```

那么发送方必须等。

最关键的规则是：

> VALID 一旦拉高，在真正 handshake 之前不能撤掉。

而且对应的：

```text
ADDR / DATA / CONTROL
```

都必须保持稳定。

---

### 情况 2：READY 先来

接收方可以提前说：

```text
我随时可以接数据
```

也就是：

```text
READY = 1
```

然后 VALID 一来就可以立即完成 transfer。

例如：

```text
READY  ────1────────────
VALID  ──────────1──────
                 ↑
             transfer
```

这是 AXI 很推荐的一种设计方式，因为 latency 更低。

---

### 情况 3：VALID 和 READY 同时出现

```text
VALID ──────1────
READY ──────1────
            ↑
        transfer
```

一个周期就可以完成传输。

---

# 3. 一个非常重要的 AXI 规则

这个一定要记住：

## VALID 不能依赖 READY

也就是说发送方不能这样：

```systemverilog
if (READY)
    VALID <= 1;
```

协议不允许发送端等 READY 再决定是否产生 VALID。

正确思想应该是：

```text
我有东西要发
    ↓
VALID = 1
    ↓
等待 READY
```

而不是：

```text
等 READY
   ↓
我再 VALID
```

原因就是避免：

```text
deadlock
```

死锁。

---

## READY 可以依赖 VALID

反过来，接收端却可以：

```text
等 VALID
↓
再 READY
```

所以：

```text
VALID → 不能等 READY

READY → 可以等 VALID
```

这是 AXI handshake 最重要的一条规则。

---

# 4. 五个 Channel 的 handshake

A3 把五个通道总结得非常清楚：

| Channel | VALID | READY |
|---|---|---|
| Write Address | AWVALID | AWREADY |
| Write Data | WVALID | WREADY |
| Write Response | BVALID | BREADY |
| Read Address | ARVALID | ARREADY |
| Read Data | RVALID | RREADY |

所以不要把：

```text
VALID / READY
```

理解成 AXI 只有一组。

实际上是：

```text
AWVALID / AWREADY

WVALID / WREADY

BVALID / BREADY

ARVALID / ARREADY

RVALID / RREADY
```

五套完全独立的 handshake。

---

# 5. A3.3：Channel 之间是什么关系

这是 AXI 和 AHB 很不一样的地方。

AXI 的五个通道：

```text
AR
R

AW
W
B
```

本质上都是独立的。

读：

```text
Master               Slave

AR ------------------>
   address

R  <------------------
      data
```

写：

```text
Master               Slave

AW ------------------>
   address

W  ------------------>
   data

B  <------------------
   response
```

---

## 写地址和写数据谁先？

这是一个非常容易误解的问题。

答案：

> **不要求 AW 一定先于 W。**

可能：

```text
AW先
```

也可能：

```text
W先
```

甚至：

```text
AW和W同周期
```

例如：

```text
cycle     1    2    3

AW        ✓
W              ✓
B                   ✓
```

也可以：

```text
cycle     1    2    3

W         ✓
AW             ✓
B                   ✓
```

协议为什么允许 W 先？

因为 AW channel 和 W channel 中间可能插入不同数量的：

```text
register slice
```

例如：

```text
AW path：

Master → REG → REG → Slave

W path：

Master → REG → Slave
```

那么 W 就可能先到 Slave。

---

# 6. 但是 B response 有严格依赖

虽然：

```text
AW
W
```

谁先到不固定，但：

```text
B
```

不能乱来。

AXI4 中，Slave 产生：

```text
BVALID
```

之前必须确认：

```text
AW handshake完成
+
最后一个W handshake完成
```

也就是：

```text
AWVALID && AWREADY
```

发生过，并且：

```text
WVALID && WREADY && WLAST
```

发生过。

才能：

```text
BVALID = 1
```

可以简单画成：

```text
AW handshake ─────┐
                  ├──> BVALID
last W handshake ─┘
```

这是写通道非常重要的 dependency。

---

# 7. Read 的依赖更简单

读操作：

```text
AR
↓
R
```

Slave 必须先真正接收到读地址。

也就是：

```text
ARVALID && ARREADY
```

握手完成以后，才能针对这个 request 返回：

```text
RVALID
```

所以基本关系：

```text
AR handshake
      ↓
RVALID
```

但是：

```text
RVALID
```

不能等待：

```text
RREADY
```

否则仍然可能死锁。

---

# 8. A3.4：Transaction Structure

这一部分开始进入 AXI Burst。

也是 AXI 学习的第二大重点。

Master 只需要发送：

```text
起始地址
+
LEN
+
SIZE
+
BURST
```

Slave 就可以计算整个 burst 后面的地址。

比如：

```text
AWADDR  = 0x1000
AWSIZE  = 2
AWLEN   = 3
AWBURST = INCR
```

就已经描述了一整个 Burst。

---

# 9. AxLEN

协议规定：

```text
Burst_Length = AxLEN + 1
```

所以：

```text
AxLEN = 0
```

不是 0 beat，而是：

```text
1 beat
```

例如：

| AxLEN | beat 数 |
|---:|---:|
| 0 | 1 |
| 1 | 2 |
| 3 | 4 |
| 7 | 8 |
| 15 | 16 |
| 255 | 256 |

所以你以后看到：

```text
AWLEN = 3
```

第一反应应该是：

```text
4 beat
```

不是 3 beat。

---

# 10. AxSIZE

SIZE 决定：

> **每一个 beat 传输多少 Byte。**

公式：

```text
bytes_per_beat = 2 ^ AxSIZE
```

例如：

| AxSIZE | Byte/beat |
|---:|---:|
| 0 | 1 Byte |
| 1 | 2 Byte |
| 2 | 4 Byte |
| 3 | 8 Byte |
| 4 | 16 Byte |

例如：

```text
AWSIZE = 2
```

表示：

```text
2² = 4 Byte
```

也就是：

```text
32 bit / beat
```

---

# 11. AxBURST

AXI 有三种 burst：

```text
FIXED
INCR
WRAP
```

编码：

```text
00 → FIXED
01 → INCR
10 → WRAP
11 → Reserved
```

---

## FIXED

每拍地址都一样：

```text
0x1000
0x1000
0x1000
0x1000
```

典型用途：

```text
FIFO
```

---

## INCR

每次增加：

```text
2 ^ AxSIZE
```

例如：

```text
AxSIZE = 2
```

每 beat：

```text
4 Byte
```

地址：

```text
0x1000
0x1004
0x1008
0x100C
```

这是最常见的 burst。

---

## WRAP

WRAP 前面像 INCR：

```text
地址++
```

但是到达边界以后：

```text
wrap到低地址
```

典型用途是：

```text
cache line
```

---

# 12. 4KB Boundary

A3 还有一条特别重要的规则：

> **一个 burst 不能跨 4KB 地址边界。**

比如：

```text
0x0000 - 0x0FFF
```

是一块 4KB。

下一块：

```text
0x1000 - 0x1FFF
```

所以一个 Burst 不能：

```text
0x0FF0
...
0x1004
```

跨过去。

原因之一就是可能跨到另外一个 Slave 地址空间。

这也是 AXI verification 非常常见的 constraint：

```systemverilog
burst不能cross 4KB
```

---

# 13. WSTRB

A3.4 还介绍了非常重要的：

```text
WSTRB
```

每一个 bit 对应：

```text
WDATA中的1 Byte
```

比如：

```text
WDATA[31:0]
WSTRB[3:0]
```

对应：

```text
WSTRB[0] → WDATA[7:0]
WSTRB[1] → WDATA[15:8]
WSTRB[2] → WDATA[23:16]
WSTRB[3] → WDATA[31:24]
```

例如：

```text
WSTRB = 4'b0011
```

表示：

```text
WDATA[15:0] 有效
WDATA[31:16] 不写
```

所以：

```text
WSTRB
```

本质就是：

> **Byte Enable。**

---

# 14. Unaligned Transfer

AXI 支持：

```text
unaligned access
```

例如：

```text
32-bit transfer
```

正常对齐地址：

```text
0x1000
0x1004
0x1008
```

但 AXI 也允许：

```text
0x1001
```

这种非 4Byte 对齐地址。

此时需要结合：

```text
AxADDR
+
WSTRB
```

判断到底哪些 byte lane 有效。

A3 第 56～58 页专门画了 aligned / unaligned 的例子。

---

# 15. Response

A3 最后还定义了 AXI response：

```text
RRESP
BRESP
```

编码：

| RESP | 含义 |
|---|---|
| `00` | OKAY |
| `01` | EXOKAY |
| `10` | SLVERR |
| `11` | DECERR |

最常见：

```text
OKAY
```

---

## SLVERR

说明：

```text
地址已经找到slave
```

但是 Slave 自己报错。

例如：

```text
写只读寄存器
unsupported transfer size
FIFO error
slave timeout
```

---

## DECERR

一般表示：

```text
地址decode不到任何slave
```

例如：

```text
Master访问 0xFFFF0000
```

但是 interconnect 的地址 map 里面根本没有这个地址。

通常：

```text
Interconnect → DECERR
```

---

# 16. 把整个 A3 压缩成一张图

你可以先把 A3 记成：

```text
                    A3
                     │
       ┌─────────────┼─────────────┐
       │             │             │
    handshake      channel       burst
       │          dependency        │
 VALID/READY          │         ADDR/LEN
       │            AW/W/B       SIZE/BURST
       │             AR/R           │
       │                            │
  VALID不能等READY               WSTRB
                              unaligned
                                  │
                                RESP
```

---

# 17. 学习 A3 的重点顺序

建议 A3 不要平均用力，按这个顺序：

## 第一优先级：A3.2 VALID/READY

一定真正搞懂：

```text
VALID什么时候拉高
READY什么时候拉高
什么时候算transfer
stall期间什么必须保持稳定
```

## 第二优先级：A3.3 Channel Dependencies

尤其：

```text
AW/W谁先都可以
B什么时候才能返回
AR和R的依赖
```

## 第三优先级：A3.4 Burst

重点：

```text
AxLEN
AxSIZE
AxBURST
地址计算
4KB boundary
```

## 第四优先级

```text
WSTRB
unaligned transfer
RESP
```

这几块搞懂以后，基本就已经能开始 **看 AXI 波形和写简单 AXI sequence/monitor** 了。

---

## 资料来源

- ARM IHI 0022H — *AMBA AXI and ACE Protocol Specification*
- A3: *Single Interface Requirements*
- 重点页：A3-40 ～ A3-60
