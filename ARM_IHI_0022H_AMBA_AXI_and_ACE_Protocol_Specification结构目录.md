## 目录结构

### Preface：前言

介绍文档适用范围、版本历史、术语、排版约定和许可证。

需要特别注意：

- Issue H 是文档修订版本，并不是“AXI H”协议。
- AXI3 属于 AMBA 3。
- AXI4、AXI4-Lite 属于 AMBA 4。
- AXI5、AXI5-Lite 属于 AMBA 5。

### Part A：AXI 基础协议

这是整份文档最重要的部分，也是学习 AXI4 的核心。

| 章节 | 内容 | 重要程度 |
| ---- | ---- | -------- |
| A1 | AXI 架构、基本概念和术语 | 入门必读 |
| A2 | 五个通道及其信号定义 | 必读 |
| A3 | 时钟、复位、握手、读写事务、Burst | 必读 |
| A4 | Cache、Protection、Memory Type 等事务属性 | 进阶 |
| A5 | Transaction ID、Outstanding、乱序返回 | 进阶 |
| A6 | AXI 顺序模型 | 进阶难点 |
| A7 | Exclusive、Locked、Atomic 原子访问 | 按需 |
| A8 | QoS、Region、User 自定义信号 | 按需 |
| A9 | 默认信号值及不同接口间的兼容性 | 工程参考 |

其中最关键的是：

- **A2**：认识 `AW`、`W`、`B`、`AR`、`R` 五个通道。
- **A3**：理解 `VALID/READY` 握手和通道之间的依赖关系。
- **A5**：理解多个未完成事务和 ID。
- **A6**：理解事务何时允许乱序、何时必须保序。

### Part B：AXI4-Lite

专门介绍简化版 AXI4-Lite：

- 不支持 Burst。
- 通常不使用事务 ID。
- 主要用于寄存器读写和控制接口。
- 介绍 AXI4 与 AXI4-Lite 之间的转换和兼容规则。

如果你要设计普通 AXI-Lite 寄存器从设备，应阅读 **Part A 的 A1～A3，再阅读 Part B**。

### Part C：AXI5 和 AXI5-Lite

介绍 AMBA 5 中的接口扩展：

- C1：AXI5 新能力和信号。
- C2：AXI5-Lite，以及与 AXI4-Lite 的兼容和升级。

如果当前项目只使用 FPGA 中常见的 AXI4/AXI4-Lite，可以暂时跳过。

### Part D：ACE 和 ACE-Lite

ACE 是在 AXI 基础上加入缓存一致性功能的协议，主要面向多核处理器系统。

包含：

- 一致性事务及额外信号。
- Snoop 探测事务。
- Cache Maintenance。
- Barrier 屏障事务。
- DVM 分布式虚拟内存事务。
- ACE-Lite。
- 一致性互连要求。

这部分内容较复杂，普通 FPGA 外设和 AXI4 IP 通常不需要阅读。

### Part E：AMBA 5 新增功能

介绍 AMBA 5 为 AXI5、ACE5 增加的通用特性，例如：

- QoS Accept。
- Trace 信号。
- Loopback。
- Persistent Cache。
- MPAM。
- Memory Tagging。
- Prefetch。
- Poison 和奇偶校验保护。

适用于实现 AXI5 或研究高端 SoC 互连的场景。

### Part F：ACE5 系列

介绍 AMBA 5 的缓存一致性接口：

- ACE5。
- ACE5-Lite。
- ACE5-LiteDVM。
- ACE5-LiteACP。
- ACE 与 ACE5 的差异。

主要供处理器、缓存一致性互连和高级 SoC 设计人员使用。

### Part G：附录和速查表

这是工程调试时很实用的部分：

- G1：一致性事务命名。
- G2：各协议的信号列表。
- G3：接口属性汇总。
- G4：`ARSNOOP`、`AWSNOOP` 编码。
- G5：ID 使用约束。
- G6：`RRESP`、`BRESP` 响应码。
- G7：各文档版本之间的修改记录。
- Glossary：术语表。

## 推荐学习顺序

如果目标是学习常见的 AXI4：

1. **A1**：建立整体概念。
2. **A2**：认识五个独立通道。
3. **A3.2～A3.4**：学习握手、读写事务和 Burst。
4. **A5**：学习 ID、Outstanding 和乱序。
5. **A6**：学习顺序模型。
6. **A4**：补充 Cache、Protection 等属性。
7. 根据需要阅读 A7～A9。

如果目标是实现 AXI4-Lite 寄存器接口，优先阅读 **A1、A2、A3 和 B1**，其余部分可以后看。
