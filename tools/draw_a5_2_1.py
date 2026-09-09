"""Build the A5.2.1 read-data reordering-depth timing example."""
from draw_a5_1 import BLUE, GREEN, PURPLE, PALE_BLUE, PALE_GREEN, PALE_PURPLE, handshakes, timing


def build_depth_2():
    rows = [
        ("ARVALID", [1, 1, 0, 0, 0, 0], "bit", BLUE),
        ("ARREADY", [1, 1, 1, 1, 1, 1], "bit", GREEN),
        ("ARID", ["1", "2", "—", "—", "—", "—"], "bus", BLUE),
        ("ARADDR", ["A", "B", "—", "—", "—", "—"], "bus", BLUE),
        ("RVALID", [0, 0, 1, 1, 0, 0], "bit", PURPLE),
        ("RREADY", [1, 1, 1, 1, 1, 1], "bit", BLUE),
        ("RID", ["—", "—", "2", "1", "—", "—"], "bus", PURPLE),
        ("RDATA", ["—", "—", "B0", "A0", "—", "—"], "bus", PURPLE),
        ("RLAST", [0, 0, 1, 1, 0, 0], "bit", PURPLE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "AR") == [1, 2]
    assert handshakes(data, "R") == [3, 4]
    assert [data["ARID"][i - 1] for i in handshakes(data, "AR")] == ["1", "2"]
    assert [data["RID"][i - 1] for i in handshakes(data, "R")] == ["2", "1"]
    assert [data["RDATA"][i - 1] for i in handshakes(data, "R")] == ["B0", "A0"]

    timing(
        "a5-2-1-read-reordering-depth",
        "读数据重排深度：两笔待处理地址的重排示例",
        "假设从设备声明重排深度为 2｜A、B 为不同 ID 的单拍读事务",
        rows,
        [
            ("T1：接收 A，ARID=1\nA 进入待处理集合", PALE_BLUE, BLUE),
            ("T2：接收 B，ARID=2\n此后共有 2 笔待处理地址", PALE_BLUE, BLUE),
            ("T3～T4：先返回 B，再返回 A\n在两笔事务范围内发生重排", PALE_PURPLE, PURPLE),
        ],
        "重排深度为 2：从设备能够在两笔待处理读地址的范围内调整返回次序；不表示每次都必须乱序。",
        "若重排深度为 1，从设备按序处理所有事务，只能先返回 A、再返回 B。相同 ID 的事务也始终必须保序。",
        "重排深度是设计者声明的静态能力，主设备不能通过 AXI 信号查询。A=0x1000，B=0x2000，ARLEN=0，RRESP=OKAY。",
    )


def build_depth_1():
    rows = [
        ("ARVALID", [1, 1, 0, 0, 0, 0], "bit", BLUE),
        ("ARREADY", [1, 1, 1, 1, 1, 1], "bit", GREEN),
        ("ARID", ["1", "2", "—", "—", "—", "—"], "bus", BLUE),
        ("ARADDR", ["A", "B", "—", "—", "—", "—"], "bus", BLUE),
        ("RVALID", [0, 0, 1, 1, 0, 0], "bit", PURPLE),
        ("RREADY", [1, 1, 1, 1, 1, 1], "bit", BLUE),
        ("RID", ["—", "—", "1", "2", "—", "—"], "bus", PURPLE),
        ("RDATA", ["—", "—", "A0", "B0", "—", "—"], "bus", PURPLE),
        ("RLAST", [0, 0, 1, 1, 0, 0], "bit", PURPLE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "AR") == [1, 2]
    assert handshakes(data, "R") == [3, 4]
    assert [data["ARID"][i - 1] for i in handshakes(data, "AR")] == ["1", "2"]
    assert [data["RID"][i - 1] for i in handshakes(data, "R")] == ["1", "2"]
    assert [data["RDATA"][i - 1] for i in handshakes(data, "R")] == ["A0", "B0"]

    timing(
        "a5-2-1-read-reordering-depth-1",
        "读数据重排深度为 1：按地址接收顺序返回",
        "A、B 为不同 ID 的单拍读事务｜从设备可以接收两笔，但不重排",
        rows,
        [
            ("T1：接收 A，ARID=1\nA 进入待处理集合", PALE_BLUE, BLUE),
            ("T2：接收 B，ARID=2\n此后仍有 2 笔未完成事务", PALE_BLUE, BLUE),
            ("T3～T4：先返回 A，再返回 B\n返回次序与地址次序一致", PALE_GREEN, GREEN),
        ],
        "重排深度为 1：从设备按顺序处理所有读事务，即使 A、B 使用不同 ID，后发的 B 也不越过 A。",
        "重排深度描述调整返回次序的能力，不是未完成事务容量；本例仍然连续接收了两笔地址。",
        "重排深度是设计者声明的静态能力，主设备不能通过 AXI 信号查询。A=0x1000，B=0x2000，ARLEN=0，RRESP=OKAY。",
    )


def main():
    build_depth_2()
    build_depth_1()


if __name__ == "__main__":
    main()
