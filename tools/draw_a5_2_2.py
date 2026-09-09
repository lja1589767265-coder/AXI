"""Build the A5.2.2 interconnect write-data ordering timing example."""
from draw_a5_1 import BLUE, GREEN, PALE_BLUE, PALE_GREEN, PALE_PURPLE, PURPLE, handshakes, timing


def main():
    rows = [
        ("AWVALID", [1, 1, 0, 0, 0, 0, 0], "bit", BLUE),
        ("AWREADY", [1, 1, 1, 1, 1, 1, 1], "bit", GREEN),
        ("AW来源", ["M0", "M1", "—", "—", "—", "—", "—"], "bus", BLUE),
        ("AW事务", ["A", "B", "—", "—", "—", "—", "—"], "bus", BLUE),
        ("WVALID", [0, 1, 1, 1, 1, 0, 0], "bit", BLUE),
        ("WREADY", [1, 1, 1, 1, 1, 1, 1], "bit", GREEN),
        ("WDATA", ["—", "A0", "A1", "B0", "B1", "—", "—"], "bus", BLUE),
        ("WLAST", [0, 0, 1, 0, 1, 0, 0], "bit", BLUE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "AW") == [1, 2]
    assert handshakes(data, "W") == [2, 3, 4, 5]
    assert [data["AW来源"][i - 1] for i in handshakes(data, "AW")] == ["M0", "M1"]
    assert [data["AW事务"][i - 1] for i in handshakes(data, "AW")] == ["A", "B"]
    assert [data["WDATA"][i - 1] for i in handshakes(data, "W")] == ["A0", "A1", "B0", "B1"]
    assert [data["WLAST"][i - 1] for i in handshakes(data, "W")] == [0, 1, 0, 1]

    timing(
        "a5-2-2-interconnect-write-data-order",
        "互连合并写事务：W 数据必须跟随 AW 事务顺序",
        "观察互连的同一个下游 AXI4 接口｜A 来自 M0，B 来自 M1",
        rows,
        [
            ("T1～T2：互连依次转发地址\nAW 事务顺序为 A → B", PALE_BLUE, BLUE),
            ("T2～T3：先转发 A0、A1\nA1 携带 WLAST=1", PALE_GREEN, GREEN),
            ("T4～T5：再转发 B0、B1\nB1 携带 WLAST=1", PALE_GREEN, GREEN),
        ],
        "下游 AW 事务顺序为 A → B，因此下游 W 数据必须为 A0 → A1 → B0 → B1；不能让 B 越过 A。",
        "AXI4 的 W 通道没有 WID，不能交织成 A0 → B0 → A1 → B1。AXI3 曾允许不同 ID 的写数据交织。",
        "“地址顺序”是 AW 事务的转发顺序，不是地址值排序。本例 A=0x2000、B=0x1000；两笔均为 2 拍 INCR，且无背压。",
    )


if __name__ == "__main__":
    main()
