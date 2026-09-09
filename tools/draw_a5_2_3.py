"""Build the A5.2.3 interconnect ID-extension and response-routing examples."""
from draw_a5_1 import BLUE, GREEN, PALE_BLUE, PALE_GREEN, PALE_PURPLE, PURPLE, handshakes, timing


def build_request_extension():
    rows = [
        ("M0.ARVALID", [1, 0, 0, 0, 0], "bit", BLUE),
        ("M0.ARREADY", [1, 1, 1, 1, 1], "bit", GREEN),
        ("M0.ARID", ["11", "—", "—", "—", "—"], "bus", BLUE),
        ("M1.ARVALID", [0, 1, 0, 0, 0], "bit", BLUE),
        ("M1.ARREADY", [1, 1, 1, 1, 1], "bit", GREEN),
        ("M1.ARID", ["—", "11", "—", "—", "—"], "bus", BLUE),
        ("S.ARVALID", [0, 1, 1, 0, 0], "bit", BLUE),
        ("S.ARREADY", [1, 1, 1, 1, 1], "bit", GREEN),
        ("S.ARID", ["—", "011", "111", "—", "—"], "bus", BLUE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "M0.AR") == [1]
    assert handshakes(data, "M1.AR") == [2]
    assert handshakes(data, "S.AR") == [2, 3]
    assert data["M0.ARID"][0] == data["M1.ARID"][1] == "11"
    assert [data["S.ARID"][i - 1] for i in handshakes(data, "S.AR")] == ["011", "111"]

    timing(
        "a5-2-3-interconnect-id-extension",
        "互连扩展 ID：相同本地 ID 变为不同下游 ID",
        "读地址通道示例｜M0、M1 的 ID 为 2 位，下游从设备接口的 ID 为 3 位",
        rows,
        [
            ("T1：M0 发送 ARID=11\n互连为 M0 使用来源位 0", PALE_BLUE, BLUE),
            ("T2：M1 也发送 ARID=11\n互连为 M1 使用来源位 1", PALE_BLUE, BLUE),
            ("T2～T3：下游依次看到\n011={0,11}，111={1,11}", PALE_GREEN, GREEN),
        ],
        "M0、M1 可以使用相同的本地 ID；互连附加各端口唯一的来源位，使下游 ID 011 与 111 保持唯一。",
        "主设备接口的原 ID 为 2 位，下游从设备接口的扩展 ID 为 3 位。同样的方法适用于 AWID，以及 AXI3 的 WID。",
        "教学重绘；来源位画在高位仅为示例，不规定实际位布局或固定转发延迟。所有 READY 均为 1。",
    )


def build_read_response_routing():
    rows = [
        ("S.RVALID", [1, 1, 0, 0, 0], "bit", PURPLE),
        ("S.RREADY", [1, 1, 1, 1, 1], "bit", BLUE),
        ("S.RID", ["111", "011", "—", "—", "—"], "bus", PURPLE),
        ("M0.RVALID", [0, 0, 1, 0, 0], "bit", PURPLE),
        ("M0.RREADY", [1, 1, 1, 1, 1], "bit", BLUE),
        ("M0.RID", ["—", "—", "11", "—", "—"], "bus", PURPLE),
        ("M1.RVALID", [0, 1, 0, 0, 0], "bit", PURPLE),
        ("M1.RREADY", [1, 1, 1, 1, 1], "bit", BLUE),
        ("M1.RID", ["—", "11", "—", "—", "—"], "bus", PURPLE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "S.R") == [1, 2]
    assert handshakes(data, "M1.R") == [2]
    assert handshakes(data, "M0.R") == [3]
    assert data["S.RID"][0:2] == ["111", "011"]
    assert data["M1.RID"][1] == data["M0.RID"][2] == "11"

    timing(
        "a5-2-3-read-response-routing",
        "RID 返回路径：按来源位选择端口并恢复本地 ID",
        "S 表示互连的从设备侧接口｜M0、M1 表示两个主设备侧接口",
        rows,
        [
            ("T1：收到 RID=111\n来源位 1 指向 M1", PALE_PURPLE, PURPLE),
            ("T2：M1 收到 RID=11\n同时下游收到 RID=011", PALE_PURPLE, PURPLE),
            ("T3：来源位 0 指向 M0\nM0 收到 RID=11", PALE_GREEN, GREEN),
        ],
        "互连读取扩展 RID 的来源位：111 路由到 M1，011 路由到 M0。",
        "向目标主设备转发前，互连去掉来源位；因此 M0、M1 在各自接口上都重新看到本地 RID=11。",
        "教学重绘；所有 RREADY 均为 1，RDATA/RRESP/RLAST 省略；一拍转发延迟仅为示例，不是协议要求。",
    )


def build_write_response_routing():
    rows = [
        ("S.BVALID", [1, 1, 0, 0, 0], "bit", PURPLE),
        ("S.BREADY", [1, 1, 1, 1, 1], "bit", BLUE),
        ("S.BID", ["011", "111", "—", "—", "—"], "bus", PURPLE),
        ("M0.BVALID", [0, 1, 0, 0, 0], "bit", PURPLE),
        ("M0.BREADY", [1, 1, 1, 1, 1], "bit", BLUE),
        ("M0.BID", ["—", "11", "—", "—", "—"], "bus", PURPLE),
        ("M1.BVALID", [0, 0, 1, 0, 0], "bit", PURPLE),
        ("M1.BREADY", [1, 1, 1, 1, 1], "bit", BLUE),
        ("M1.BID", ["—", "—", "11", "—", "—"], "bus", PURPLE),
    ]
    data = {label: values for label, values, _kind, _color in rows}
    assert handshakes(data, "S.B") == [1, 2]
    assert handshakes(data, "M0.B") == [2]
    assert handshakes(data, "M1.B") == [3]
    assert data["S.BID"][0:2] == ["011", "111"]
    assert data["M0.BID"][1] == data["M1.BID"][2] == "11"

    timing(
        "a5-2-3-write-response-routing",
        "BID 返回路径：按来源位选择端口并恢复本地 ID",
        "S 表示互连的从设备侧接口｜M0、M1 表示两个主设备侧接口",
        rows,
        [
            ("T1：收到 BID=011\n来源位 0 指向 M0", PALE_PURPLE, PURPLE),
            ("T2：M0 收到 BID=11\n同时下游收到 BID=111", PALE_PURPLE, PURPLE),
            ("T3：来源位 1 指向 M1\nM1 收到 BID=11", PALE_GREEN, GREEN),
        ],
        "互连读取扩展 BID 的来源位：011 路由到 M0，111 路由到 M1。",
        "向目标主设备转发前，互连去掉来源位；因此 M0、M1 在各自接口上都重新看到本地 BID=11。",
        "教学重绘；所有 BREADY 均为 1，BRESP 省略；一拍转发延迟仅为示例，不是协议要求。",
    )


def main():
    build_request_extension()
    build_read_response_routing()
    build_write_response_routing()


if __name__ == "__main__":
    main()
