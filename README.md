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

## 后续内容

本仓库计划逐步补充：

- AXI 五通道及握手机制笔记
- AXI4 与 AXI4-Lite 的差异
- Burst、响应、乱序与 outstanding transaction 示例
- Verilog/SystemVerilog 设计与验证实践

## 说明

本项目为个人学习资料库，并非 Arm 官方项目。AXI、AMBA 及相关商标和文档版权归其各自权利人所有。
