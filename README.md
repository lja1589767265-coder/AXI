# AXI 学习资料与实践记录

本项目用于整理 AMBA AXI 协议的学习笔记、示例代码和实践记录。

## AXI 简介

AXI（Advanced eXtensible Interface）是 Arm AMBA 体系中的片上通信接口协议。它采用相互独立的读写通道和基于 `VALID/READY` 的握手机制，常用于 SoC、FPGA 与各类 IP 核之间的高性能数据传输。

## 官方规范

- 文档名称：*AMBA AXI and ACE Protocol Specification*
- 文档编号：Arm IHI 0022H
- 涵盖协议：AXI3、AXI4、AXI4-Lite、AXI5、AXI5-Lite 及 ACE 系列协议
- 官方页面：[Arm Documentation — IHI0022H](https://developer.arm.com/documentation/ihi0022/h/)

Arm 官方规范受其版权条款保护，因此本仓库不提供 PDF 副本。请通过上述官方页面获取最新且适用的版本。

## 规范目录架构

IHI 0022H 共 500 页，是一份涵盖 AXI 和 ACE 多代协议的合集式规范。全文由前言、七个主体部分和术语表组成。

### Preface：前言

介绍文档适用范围、修订历史、阅读约定、相关资料和许可证。

需要注意，Issue H 表示文档的修订版本，并不是一种名为“AXI H”的协议版本。该文档覆盖的主要接口包括：

- AMBA 3：AXI3
- AMBA 4：AXI4、AXI4-Lite、ACE、ACE-Lite
- AMBA 5：AXI5、AXI5-Lite、ACE5 及其衍生接口

### Part A：AMBA AXI Protocol Specification

AXI 的公共基础规范，也是学习 AXI3 和 AXI4 的核心部分。

| 章节 | 主题 | 主要内容 |
| --- | --- | --- |
| A1 | Introduction | AXI 架构、基本概念和术语 |
| A2 | Signal Descriptions | AW、W、B、AR、R 五个通道及其信号 |
| A3 | Single Interface Requirements | 时钟、复位、`VALID/READY` 握手、读写事务和 Burst |
| A4 | Transaction Attributes | Memory Type、Cache、Protection 和事务属性 |
| A5 | Transaction Identifiers | ID、多个 Outstanding 事务和乱序完成 |
| A6 | AXI Ordering Model | 事务顺序、观察点和完成规则 |
| A7 | Atomic Accesses | Exclusive、Locked 和原子访问 |
| A8 | AMBA 4 Additional Signaling | QoS、Region 和 User 自定义信号 |
| A9 | Default Signaling and Interoperability | 默认信号值及精简接口之间的互操作性 |

初学时应重点掌握 A2、A3、A5 和 A6。其中 A3 是理解 AXI 时序和避免死锁的基础。

### Part B：AMBA AXI4-Lite Interface Specification

介绍面向控制寄存器访问的简化接口 AXI4-Lite，包括：

- AXI4-Lite 的定义和限制
- 与完整 AXI4 接口的差异
- AXI4 与 AXI4-Lite 之间的转换
- 接口转换时的保护与错误检测

AXI4-Lite 不支持 Burst，主要用于低吞吐量的寄存器配置和状态读取。

### Part C：AMBA AXI5 and AXI5-Lite Interface Specification

介绍 AXI5 和 AXI5-Lite 的新增能力、接口属性、信号要求，以及 AXI4-Lite 向 AXI5-Lite 升级时的兼容方式。

只使用常见 FPGA AXI4 IP 时，可以暂时跳过这一部分。

### Part D：AMBA ACE and ACE-Lite Protocol Specification

ACE 在 AXI 的基础上加入系统级缓存一致性能力。本部分涵盖：

- ACE 附加通道和信号
- Coherency Transaction 和 Snoop Transaction
- Cache Maintenance 和 Barrier
- Exclusive Access
- ACE-Lite、DVM 和外部 Snoop Filter
- 一致性互连及 Master 设计建议

普通 AXI 外设通常不需要实现这部分；它主要面向多核处理器和缓存一致性互连。

### Part E：AMBA 5 Protocol Features

集中介绍 AMBA 5 新增的通用能力，例如 Trace、QoS Accept、Persistent Cache、MPAM、Memory Tagging、Prefetch、Poison 和奇偶校验保护。

### Part F：AMBA ACE5 系列接口

介绍 AMBA 5 缓存一致性接口：

- ACE5
- ACE5-Lite
- ACE5-LiteDVM
- ACE5-LiteACP
- ACE/ACE-Lite 到 ACE5 系列的行为变化

### Part G：附录

提供工程设计和调试中常用的速查信息：

- 事务命名规则
- 各类接口的信号矩阵
- 接口属性汇总
- `ARSNOOP` 和 `AWSNOOP` 编码
- ID 使用约束
- `RRESP` 和 `BRESP` 响应码
- 不同文档修订版本之间的变化

文档最后还包含 Glossary，可用于查询协议术语。

## 推荐阅读路线

### 学习 AXI4

1. A1：了解整体架构和术语。
2. A2：认识五个独立通道。
3. A3：掌握握手、读写事务和 Burst。
4. A5：理解 ID、Outstanding 和乱序完成。
5. A6：理解保序和乱序规则。
6. A4：补充 Cache、Protection 等事务属性。
7. 根据项目需要阅读 A7～A9。

### 实现 AXI4-Lite 寄存器接口

建议依次阅读 A1、A2、A3 和 B1，重点关注：

- 五通道之间相互独立
- `VALID` 不得依赖 `READY` 才拉高
- 写地址和写数据可能在不同周期到达
- `BRESP` 和 `RRESP` 的错误响应

### 学习 AXI5 或 ACE

- AXI5/AXI5-Lite：Part A → Part C → Part E
- ACE/ACE-Lite：Part A → Part D
- ACE5 系列：Part A → Part D → Part E → Part F

## 项目后续内容

本仓库计划逐步补充：

- AXI 五通道及握手机制笔记
- AXI4 与 AXI4-Lite 的差异
- Burst、响应、乱序与 outstanding transaction 示例
- Verilog/SystemVerilog 设计与验证实践

## 说明

本项目为个人学习资料库，并非 Arm 官方项目。AXI、AMBA 及相关商标和文档版权归其各自权利人所有。
