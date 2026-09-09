# AXI 协议翻译与学习资料记录

本仓库用于整理 AMBA AXI 协议中文翻译、旧版学习导读、设计示例和验证实践。A1 已按忠实翻译规范重新制作，A2～A3 暂时保留为旧版学习导读；从 A5 及后续章节开始，正文按照忠实翻译规范制作。

## 个人学习进度

- 截至 2026-09-09，已重点学习：A1、A2、A3、A5。
- A6 正在学习，尚未看完。
- 除上述章节外，其他章节尚未开始系统学习。

## 文档索引

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| [ARM IHI 0022H AMBA AXI and ACE Protocol Specification 结构目录](ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification结构目录.md) | 介绍 IHI 0022H 的 Preface、Part A～G 及推荐学习顺序 | 已完成 |
| [A1：简介](ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A1.md) | 按 PDF 原文顺序制作 A1.1～A1.3.4 全文中英双语对照，含 3 张原图双语重绘和 6 张补充结构/时序图（包括寄存器切片结构图） | 已完成（全文双语稿） |
| [AXI 写事务动态时序演示](axi-write-timing-demo.html) | AXI 动态时序图的交互原型；后续以此为统一基础，扩展读写事务、握手、背压、突发传输和多笔未完成事务等时序场景 | 原型阶段 |
| [README 翻译文档制作规范](README写作规范.md) | 规定忠实翻译、全文双语例外、英文术语括注、补充图边界、draw.io 重绘和逐项验收方法 | 已更新（A5 起执行） |
| [A2：AXI 接口信号导读](ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A2.md) | 按原文六节介绍全局信号和五通道，结合时序图解释读写及握手 | 已完成（旧版学习导读） |
| [A3：AXI 单接口要求](ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A3.md) | 基于新笔记整理：时钟复位、握手依赖、突发地址与字节通道、Regular 属性和响应；含 13 张重绘图及 10 道自测题 | 已完成（旧版学习导读） |
| [A5：Transaction Identifiers](ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A5.md) | 按 PDF 原文顺序完整翻译 A5.1、A5.2 及 A5.2.1～A5.2.3，含表 A5-1 的 draw.io 中文重绘 | 已完成（忠实翻译稿） |
| [A6：AXI 顺序模型](ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A6.md) | 按 PDF 原文顺序完整翻译 A6.1～A6.8；原章没有图表 | 已完成（忠实翻译稿） |
| [A4：事务属性导读](ARM_IHI_0022H_AMBA_AXI_and_ACE_Protocol_Specification_A4.md) | 覆盖 A4 全章：AxCACHE、内存类型、缓冲、AxPROT 与 Device 写完成保证，含三幅教学图及自测 | 已完成 |

## 后续计划

1. 按忠实翻译规范继续制作 A7 及后续章节。
2. 使用 draw.io 中文重绘后续章节中的原图和原表，并同时保存 `.drawio` 与 PNG。
3. 每章完成后逐项核对标题、段落、Note、Caution、列表、公式、图表、脚注和关键英文原句。
4. 以 `axi-write-timing-demo.html` 为动态时序图基础，逐步建立可复用的场景和信号模型，用于生成各种 AXI 读写时序图。

## AXI 翻译文档制作规范（A5 及后续）

详细规则见 [README 翻译文档制作规范](README写作规范.md)。简要要求如下：

1. 默认采用纯中文正文，只在关键规范句后附完全一致的英文原句；明确要求全文双语的章节逐段保留完整英文原文。
2. 严格保持原文的小节、段落、Note、Caution、列表、公式、图表和脚注顺序，不遗漏、不合并、不提前或重新组织。
3. 省略每页重复的页眉、页脚、版权行和物理页码；正文中的实质性交叉引用必须保留。
4. 不主动增加学习目标、教学案例、额外时序图、易错点、总结、自测题、黄色高亮或其他原文不存在的内容。
5. 信号名、字段名、接口名、编码和协议名称保留英文；重要协议名词首次出现时可以采用 `术语（terminology）` 形式括注英文，术语形式和规范强度必须保持一致。
6. 包含 `must`、`must not`、`required`、`permitted`、`no requirement`、`deprecated`、`IMPLEMENTATION DEFINED` 或存在歧义的关键句必须附英文原句。
7. 原文中的每张图和每个表都使用 draw.io 中文重绘，并放回原文对应位置；原文没有图表时不额外制作。
8. 重绘必须保留编号、标题、结构、行列、图例、标签、全部数据和脚注，不增加教学结论框。
9. 每个图表同时保存同名 `.drawio` 和高清 PNG，默认导出宽度为 1440 像素；Markdown 只引用 PNG。
10. 翻译前建立术语表和源内容清单，完成后按清单逐项核对数量、顺序和内容。
11. 关键英文原句必须与 PDF 完全一致；`deprecated` 不得翻成“禁止”或“不支持”，其他规范强度也不得改变。
12. 完成前检查 Markdown 结构、图片路径、draw.io/PNG 配对、图表视觉质量和 `git diff --check`。
13. 用户明确要求的补充图只呈现相邻原文直接涉及的信息，采用中文且不附重复解释，不得自行扩展时序、行为、示例或结论。

## 官方规范

- 文档名称：*AMBA AXI and ACE Protocol Specification*
- 文档编号：Arm IHI 0022H
- 官方页面：[Arm Documentation — IHI0022H](https://developer.arm.com/documentation/ihi0022/h/)

Arm 官方规范受其版权条款保护，因此本仓库不提供 PDF 副本。请通过官方页面获取适用版本。

## 说明

本仓库为个人翻译与学习资料库，并非 Arm 官方项目。AXI、AMBA 及相关商标和文档版权归其各自权利人所有。
