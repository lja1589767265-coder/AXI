# A6：AXI 顺序模型

> 译文性质：Arm 规范的非官方中文翻译。
>
> 原始文档：Arm IHI 0022H《AMBA AXI and ACE Protocol Specification》。
>
> 版本：Issue H，ID040120。
>
> 范围：Chapter A6，原文章节页码 A6-83～A6-92。
>
> 说明：正文按原文顺序完整翻译；省略每页重复的页眉、页脚、版权行和物理页码。

本章规定以下内容：

- AXI 顺序模型概述，见第 A6-84 页。
- 内存位置和外设区域，见第 A6-85 页。
- 事务和顺序，见第 A6-86 页。
- 观察和完成的定义，见第 A6-87 页。
- 主设备顺序保证，见第 A6-88 页。
- 顺序要求，见第 A6-89 页。
- 端点之前的响应，见第 A6-90 页。
- 有序写观察，见第 A6-91 页。

## A6.1 AXI 顺序模型概述

AXI 顺序模型以 `Transaction Identifier` 的使用为基础，该标识通过 `ARID` 或 `AWID` 传递。

同一通道上具有相同 ID 和相同目标的事务请求保证保持有序。具有相同 ID 的事务响应按照请求发出的顺序返回。

> 原文：Transaction requests on the same channel, with the same ID and destination are guaranteed to remain in order.
>
> 原文：Transaction responses with the same ID are returned in the same order as the requests were issued.

顺序模型不在以下事务之间提供任何顺序保证：

- 来自不同主设备的事务。
- 读事务和写事务。
- 具有不同 ID 的事务。
- 发往不同外设区域的事务。
- 发往不同内存位置的事务。

如果主设备要求在没有顺序保证的事务之间建立顺序，则主设备必须在发出第二笔事务之前，等待接收到第一笔事务的响应。

> 原文：If a master requires ordering between transactions that have no ordering guarantee, the master must wait to receive a response to the first transaction before issuing the second transaction.

## A6.2 内存位置和外设区域

AMBA 中的地址映射由内存位置和外设区域组成。

内存位置具有以下所有属性：

- 从某个内存位置读取一个字节，会返回最后一次写入该字节位置的值。
- 向某个内存位置写入一个字节，会把该位置的值更新为一个新值，后续读取该位置时会得到这个新值。
- 读取或写入某个内存位置不会对任何其他内存位置产生副作用。
- 内存的观察保证按每个位置给出。
- 内存位置的大小等于该组件的单副本原子性大小。

外设区域具有以下所有属性：

- 从外设区域中的某个地址读取数据，不一定返回最后一次写入该地址的值。
- 向外设区域中的某个字节地址写入数据，不一定会把该地址的值更新为后续读取能够得到的新值。
- 访问外设区域内的某个地址可能对该区域内的其他地址产生副作用。
- 外设的观察保证按区域给出。
- 外设区域的大小由实现定义，但该区域必须完全包含在单个从设备组件之内。

> 原文：The size of a Peripheral region is IMPLEMENTATION DEFINED, but it must be contained within a single slave component.

## A6.3 事务和顺序

事务是对一个或多个地址位置进行的一次读或写操作。这些位置由 `AxADDR` 以及任何相关限定属性确定，例如 `AxPROT` 中的 Non-secure 位。

- 只有对同一内存位置或同一外设区域的访问之间才提供顺序保证。
- 发往外设区域的事务必须完全包含在该区域内。
- 跨越多个内存位置的事务具有多个顺序保证。

> 原文：Ordering guarantees are given only between accesses to the same Memory location or Peripheral region.
>
> 原文：A transaction to a Peripheral region must be entirely contained within that region.

事务可以是 Device 类型或 Normal 类型：

- **Device**：请求的 `AxCACHE[1]` 被清零的一次读或写。Device 事务可以用于访问外设区域或内存位置。
- **Normal**：请求的 `AxCACHE[1]` 被置位的一次读或写。Normal 事务用于访问内存位置，预期不会用于访问外设区域。

> 原文：Device A read or write where the request has AxCACHE[1] deasserted.
>
> 原文：Normal A read or write where the request has AxCACHE[1] asserted.

对外设区域的 Normal 访问必须以符合协议的方式完成，但其结果由实现定义。

> 原文：A Normal access to a Peripheral region must complete in a protocol-compliant manner, but the result is IMPLEMENTATION DEFINED.

写事务可以是 Non-bufferable 或 Bufferable。可以对 Bufferable 写发送提前响应。

> 原文：A write transaction can be either Non-bufferable or Bufferable. It is possible to send an early response to Bufferable writes.

- Non-bufferable 写的 `AWCACHE[0]` 被清零。
- Bufferable 写的 `AWCACHE[0]` 被置位。

## A6.4 观察和完成的定义

对于外设区域访问，如果 Device 读或写访问 DRW1 先于 Device 读或写访问 DRW2 到达从设备组件，则 DRW1 被 DRW2 观察到。

> 原文：For accesses to Peripheral regions, a Device read or write access DRW1 is observed by a Device read or write access DRW2, when DRW1 arrives at the slave component before DRW2.

对于内存位置访问，以下各项均适用：

- 如果 W2 在写 W1 之后生效，则 W1 被写 W2 观察到。
- 如果读 R1 返回来自写 W3 的数据，并且 W2 位于 W3 之后，则 R1 被写 W2 观察到。
- 如果读 R2 返回来自写 W1 的数据，或者返回来自位于 W1 之后的写 W3 的数据，则 W1 被读 R2 观察到。

> 原文：A write W1 is observed by a write W2, if W2 takes effect after W1.
>
> 原文：A read R1 is observed by a write W2, if R1 returns data from a write W3, when W2 is after W3.
>
> 原文：A write W1 is observed by a read R2, if R2 returns data from either W1 or from write W3, when W3 is after W1.

读 R1 或写 W1 可以是 Device 类型或 Normal 类型。

写完成和读完成的定义如下：

- **写完成响应**：给出关联 `BRESP` 握手的周期，即 `BVALID` 和 `BREADY` 均置位的周期。

> 原文：The cycle when the associated BRESP handshake is given, when BVALID and BREADY are asserted.

- **读完成响应**：给出关联的最后一次 `RDATA` 握手的周期，即 `RVALID`、`RLAST` 和 `RREADY` 均置位的周期。

> 原文：The cycle when the last associated RDATA handshake is given, when RVALID, RLAST and RREADY are asserted.

## A6.5 主设备顺序保证

顺序模型保证分为三类：

- 接收到完成响应之前的可观察性保证。
- 完成响应所提供的可观察性保证。
- 响应顺序保证。

### A6.5.1 接收到完成响应之前的保证

以下所有保证均适用于来自同一主设备并使用相同 ID 的事务：

- Device 写 DW1 保证先于 Device 写 DW2 到达目标，其中 DW2 在 DW1 之后发出，并且两者发往同一外设区域。
- Device 读 DR1 保证先于 Device 读 DR2 到达目标，其中 DR2 在 DR1 之后发出，并且两者发往同一外设区域。
- 写 W1 保证被写 W2 观察到，其中 W2 在 W1 之后发出，并且两者发往同一内存位置。
- 已经被读 R2 观察到的写 W1，保证也被读 R3 观察到，其中 R3 在 R2 之后发出，并且两者发往同一内存位置。

> 原文：A Device write DW1 is guaranteed to arrive at the destination before Device write DW2, where DW2 is issued after DW1 and to the same Peripheral region.
>
> 原文：A Device read DR1 is guaranteed to arrive at the destination before Device read DR2, where DR2 is issued after DR1 and to the same Peripheral region.
>
> 原文：A write W1 is guaranteed to be observed by a write W2, where W2 is issued after W1 and to the same Memory location.
>
> 原文：A write W1 that has been observed by a read R2 is guaranteed to be observed by a read R3, where R3 is issued after R2 and to the same Memory location.

这些保证意味着，对同一内存位置的 Device 访问和 Normal 访问之间存在顺序保证。

### A6.5.2 完成响应所提供的保证

完成响应保证以下所有事项：

- 读请求的完成响应保证：该读请求对来自任意主设备的后续读或写请求均可观察。
- 写请求的完成响应保证：该写请求对来自任意主设备的后续读或写请求均可观察。这种可观察性是多副本原子系统的一项要求。

> 原文：A completion response to a read request guarantees that it is observable to a subsequent read or write request from any master.
>
> 原文：A completion response to a write request guarantees that it is observable to a subsequent read or write request from any master. This observability is a requirement of a system that is multi-copy atomic.

包含符合 Arm 架构的处理器的系统必须具有多副本原子性。也就是说，`Multi_Copy_Atomicity` 属性必须为 `True`。

> 原文：Systems that contain Arm Architecture-compliant processors must be multi-copy atomic. That is, the Multi_Copy_Atomicity property must be True.

Bufferable 写请求的响应可以从中间点发出。该响应不保证写操作已在端点完成，但保证该写操作对未来的事务可观察。

> 原文：The response to a Bufferable write request can be sent from an intermediate point. It does not guarantee that the write has completed at the endpoint, but it is observable to future transactions.

### A6.5.3 响应顺序保证

事务响应具有以下所有顺序保证：

- 读 R1 保证先于读 R2 的响应接收到响应，其中 R2 由同一主设备在 R1 之后发出，并且使用相同 ID。
- 写 W1 保证先于写 W2 的响应接收到响应，其中 W2 由同一主设备在 W1 之后发出，并且使用相同 ID。

> 原文：A read R1 is guaranteed to receive a response before the response to a read R2, where R2 is issued from the same master after R1 with the same ID.
>
> 原文：A write W1 is guaranteed to receive a response before the response to a write W2, where W2 is issued from the same master after W1 with the same ID.

## A6.6 顺序要求

为了满足主设备顺序保证，对从设备和互连组件有特定要求。

### A6.6.1 从设备顺序要求

对于外设位置，发往外设位置的事务执行顺序由实现定义。通常预期该执行顺序与到达顺序一致，但这并不是一项要求。

> 原文：For Peripheral locations, the execution order of transactions to Peripheral locations is IMPLEMENTATION DEFINED.
>
> 原文：This execution order is typically expected to match the arrival order, but that is not a requirement.

对于内存位置：

- 对于发往同一内存位置且具有相同 ID 的写 W1 和写 W2，如果 W2 在 W1 之后被接收，则 W1 必须排在 W2 之前。
- 对于发往同一内存位置的写 W1 和写 W2，如果 W2 在给出 W1 的完成响应之后被接收，则 W1 必须排在 W2 之前。
- 对于发往同一内存位置的写 W1 和读 R2，如果 R2 在给出 W1 的完成响应之后被接收，则 W1 必须排在 R2 之前。
- 对于发往同一内存位置的读 R1 和写 W2，如果 W2 在给出 R1 的完成响应之后被接收，则 R1 必须排在 W2 之前。

> 原文：A write W1 must be ordered before a write W2 with the same ID, to the same Memory location, where W2 is received after W1 is received.
>
> 原文：A write W1 must be ordered before a write W2 to the same Memory location, where W2 is received after the completion response for W1 is given.
>
> 原文：A write W1 must be ordered before a read R2 to the same Memory location, where R2 is received after the completion response for W1 is given.
>
> 原文：A read R1 must be ordered before a write W2 to the same Memory location, where W2 is received after the completion response for R1 is given.

响应顺序要求如下：

- 对于具有相同 ID 的读 R1 和读 R2，如果 R2 在 R1 之后被接收，则 R1 的响应必须先于 R2 的响应返回。
- 对于具有相同 ID 的写 W1 和写 W2，如果 W2 在 W1 之后被接收，则 W1 的响应必须先于 W2 的响应返回。

> 原文：The response to read R1 must be returned before the response to a read R2, where R2 is received after R1 with the same ID.
>
> 原文：The response to write W1 must be returned before the response to a write W2, where W2 is received after W1 with the same ID.

### A6.6.2 互连顺序要求

互连组件具有以下属性：

- 请求在一个端口上被接收，并在另一个端口上发出或由互连作出响应。
- 响应在一个端口上被接收，并在另一个端口上发出或由互连消耗。

当互连发出请求或响应时，必须遵守以下要求：

> 原文：When the interconnect issues requests or responses, it must adhere to the following requirements:

- 对于具有相同 ID 且发往相同或重叠位置的读请求 R1 和 R2，如果 R2 在 R1 之后被接收，则必须先发出 R1，再发出 R2。
- 对于具有相同 ID 且发往相同或重叠位置的写请求 W1 和 W2，如果 W2 在 W1 之后被接收，则必须先发出 W1，再发出 W2。
- 对于具有相同 ID 且发往同一外设区域的 Device 读请求 DR1 和 DR2，如果 DR2 在 DR1 之后被接收，则必须先发出 DR1，再发出 DR2。
- 对于具有相同 ID 且发往同一外设区域的 Device 写请求 DW1 和 DW2，如果 DW2 在 DW1 之后被接收，则必须先发出 DW1，再发出 DW2。
- 对于具有相同 ID 的读响应 R1 和 R2，如果 R2 在 R1 之后被接收，则必须先发出 R1，再发出 R2。
- 对于具有相同 ID 的写响应 W1 和 W2，如果 W2 在 W1 之后被接收，则必须先发出 W1，再发出 W2。

> 原文：A read R1 request must be issued before a read R2 request, where R2 is received after R1, with the same ID and to the same or overlapping locations.
>
> 原文：A write W1 request must be issued before a write W2 request, where W2 is received after W1, with the same ID, to the same or overlapping locations.
>
> 原文：A Device read DR1 request must be issued before a Device read DR2 request, where DR2 is received after DR1, with the same ID and to the same Peripheral region.
>
> 原文：A Device write DW1 request must be issued before a Device write DW2 request, where DW2 is received after DW1, with the same ID and to the same Peripheral region.
>
> 原文：A read R1 response must be issued before a read R2 response, where R2 is received after R1, with the same ID.
>
> 原文：A write W1 response must be issued before a write W2 response, where W2 is received after W1, with the same ID.

当互连作为从设备组件工作时，还必须遵守从设备要求。

> 原文：When the interconnect is acting as a slave component, it must also adhere to the slave requirements.

对与事务关联的 AXI ID 值进行任何处理时，必须确保保持原始 ID 值的顺序要求。

> 原文：Any manipulation of the AXI ID values that are associated with a transaction must ensure that the ordering requirements of the original ID values are maintained.

## A6.7 端点之前的响应

为了提高系统性能，中间组件可以对某些事务发出响应。这种操作称为提前响应。发出提前响应的中间组件必须确保满足可见性和顺序保证。

> 原文：The intermediate component issuing an early response must ensure that visibility and ordering guarantees are met.

### A6.7.1 提前读响应

对于 Normal 读事务，如果本地内存中的数据相对于所有发往相同或重叠地址的先前写操作都是最新的，则中间组件可以使用该本地内存中的读数据作出响应。在这种情况下，不要求请求继续传播到中间组件之外。

> 原文：For Normal read transactions, an intermediate component can respond with read data from a local memory if it is up-to-date with respect to all earlier writes to the same or overlapping address.
>
> 原文：In this case, the request is not required to propagate beyond the intermediate component.

中间组件必须遵守 ID 顺序规则，这意味着只有当具有相同 ID 的所有先前读事务都已经获得响应时，才可以发送该读响应。

> 原文：An intermediate component must observe ID ordering rules, which means a read response can only be sent if all earlier reads with the same ID have already had a response.

### A6.7.2 提前写响应

对于没有下游观察者的 Bufferable 写事务，中间组件可以发送提前写响应。如果中间组件发送提前写响应，则可以在本地保存数据副本，但在丢弃该数据之前，必须把事务传播到下游。

> 原文：For Bufferable write transactions, an intermediate component can send an early write response for transactions that have no downstream observers.

> 原文：If the intermediate component sends an early write response, the intermediate component can store a local copy of the data, but must propagate the transaction downstream, before discarding that data.

中间组件必须遵守 ID 顺序规则，这意味着只有当具有相同 ID 的所有先前写事务都已经获得响应时，才可以发送该写响应。

> 原文：An intermediate component must observe ID ordering rules, that means a write response can only be sent if all earlier writes with the same ID have already had a response.

发送提前写响应之后，该组件必须负责该事务的顺序和可观察性，直至写事务已经传播到下游并接收到写响应。在发送提前写响应与接收到下游响应之间的期间，该组件必须确保：

> 原文：After sending an early write response, the component must be responsible for ordering and observability of that transaction until the write has been propagated downstream and a write response is received.
>
> 原文：During the period between sending the early write response and receiving a response from downstream, the component must ensure that:

- 如果为 Normal 事务给出了提前写响应，则所有后续发往相同或重叠内存位置的事务，都必须排在已获得提前响应的写事务之后。
- 如果为 Device 事务给出了提前写响应，则所有后续发往同一外设区域的事务，都必须排在已获得提前响应的写事务之后。

> 原文：If an early write response was given for a Normal transaction, all subsequent transactions to the same or overlapping Memory locations are ordered after the write that has had an early response.
>
> 原文：If an early write response was given for a Device transaction, then all subsequent transactions to the same Peripheral region are ordered after the write that has had an early response.

为 Device Bufferable 事务给出提前写响应时，预期中间组件传播该写事务时不依赖其他事务。中间组件不能在传播先前的 Device 写之前，等待另一笔读或写到达。

> 原文：The intermediate component cannot wait for another read or write to arrive before propagating a previous Device write.

## A6.8 有序写观察

为了提高与支持不同顺序模型的接口协议之间的兼容性，从设备接口可以为写事务提供更强的顺序保证。这种更强的顺序保证称为有序写观察。

`Ordered_Write_Observation` 属性用于定义接口是否表现出有序写观察。对于单个接口，该属性可以为 `True` 或 `False`。

- `True`：接口被定义为具有有序写观察属性。
- `False`：接口不具有有序写观察属性。

如果未声明 `Ordered_Write_Observation`，则认为其值为 `False`。

> 原文：If Ordered_Write_Observation is not declared, it is considered False.

表现出有序写观察的接口为写事务提供不依赖于目标或地址的保证：

- 写 W1 保证被写 W2 观察到，其中 W2 由同一主设备在 W1 之后发出，并且两者具有相同 ID。

> 原文：A write W1 is guaranteed to be observed by a write W2, where W2 is issued after W1, from the same master, with the same ID.

连接到表现出有序写观察的从设备接口时，使用 Producer-Consumer 顺序模型的主设备不需要等待较早写事务的完成响应，就可以发出存在依赖关系的写事务。

> 原文：A master using the Producer-Consumer ordering model that is connected to a slave interface that exhibits Ordered Write Observation is not required to wait for the completion response from earlier writes before issuing dependent writes.
