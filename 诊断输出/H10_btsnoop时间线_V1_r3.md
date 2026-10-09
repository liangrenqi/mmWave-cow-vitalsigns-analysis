# btsnoop 时间线（省略 HR/PMD 数据通知与续传分片；t=0 为首个 Connection Complete）

## H10原始日志/V1_r3.btsnoop

HR 通知 303、PMD 数据包 2247、首个 PMD 在 t=4.514464

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac24270000002a0000
    0.022  CMD 0x2016 LE Read Remote Features 4000
    0.023  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.136  EVT LE Read Remote Features 0040002500000000000000
    0.136  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.380  EVT LE Data Length Change 4000ec00d007ec00d007
    0.380  RX H10→Pi ATT Exchange MTU Rsp e800
    0.380  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.526  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.526  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    0.624  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    0.624  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    0.770  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    0.770  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    0.867  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    0.867  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0128
    0.964  RX H10→Pi ATT Error Rsp 对 Read By Group Type Req 句柄 0x0001 错误 0x0a
    0.964  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0228
    1.062  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.062  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0328
    1.161  RX H10→Pi ATT Read By Type Rsp 070200020300002a0400020500012a0600020700042a0800020900a62a0b00200c00052a0f00101000372a1200021300382a1500021600292a1700021800242a1900021a00252a1b00021c00272a1d00021e00262a1f00022000282a2100022200232a2400122500192a
    1.161  TX Pi→H10 ATT Read By Type Req【请求】 2500ffff0328
    1.356  RX H10→Pi ATT Read By Type Rsp 1528000229002d8e7086d93a8013fbb1ecc84cff17622a00242b00f3a1a8bdd37c2a7ed091bb914dff17622e002a2f00c8f08d2dcd8aad1c87f3e702815c00fb3100103200c8f08d2dcd8aad1c87f3e702825c00fb35001c3600c8f08d2dcd8aad1c87f3e702515c00fb3800103900c8f08d2dcd8aad1c87f3e702525c00fb3b000c3c00c8f08d2dcd8aad1c87f3e702535c00fb
    1.356  TX Pi→H10 ATT Read By Type Req【请求】 3c00ffff0328
    1.452  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x003c 错误 0x0a
    1.452  TX Pi→H10 ATT Find Info Req【请求】 3d00ffff
    1.647  RX H10→Pi ATT Error Rsp 对 Find Info Req 句柄 0x003d 错误 0x0a
    1.661  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.744  RX H10→Pi ATT Write Rsp 
    1.745  TX Pi→H10 ATT Read Req【请求】 0300
    1.891  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.891  TX Pi→H10 ATT Read Req【请求】 0500
    1.988  RX H10→Pi SMP Security Req 09
    1.988  TX Pi→H10 SMP Pairing Req 010009100d0f
    2.037  RX H10→Pi ATT Read Rsp 4103
    2.037  TX Pi→H10 ATT Read Req【请求】 2500
    2.086  RX H10→Pi SMP Pairing Rsp 030009100103
    2.087  TX Pi→H10 SMP Pairing Public Key 1d80f9f463b64b76b7fd90b19f1c137962ddf6716c5ba287d8c058709335db9bb7813fb9d63ce2ca9c98b2a1a41950c29169323d39bd9612b00f26b2f8d24fa9
    2.135  RX H10→Pi ATT Read Rsp 64
    2.135  TX Pi→H10 ATT Read Req【请求】 2f00
    2.233  RX H10→Pi SMP Pairing Public Key 7a58365faed94a30c019f5edfd9c98072245e6de013ccc4106659f5a51c509bf95e7b3d50e56595f3ee65a5326e2d9fcc9eb9118c64df0ddc495778d406d6771
    2.281  RX H10→Pi SMP Pairing Confirm 568e0aee6765d9f6bfcfbe0ecd492fbc
    2.281  TX Pi→H10 SMP Pairing Random 4eae58d7978769f57841e323576f68e8
    2.281  RX H10→Pi ATT Error Rsp 对 Read Req 句柄 0x002f 错误 0x05
    2.378  RX H10→Pi SMP Pairing Random c141dad471d5201a90a7f4912e74ccfc
    2.378  TX Pi→H10 SMP DHKey Check 699a2ddde3bf4f2c0e2922b32be43f90
    2.524  RX H10→Pi SMP DHKey Check 560bf6dd548aae5e49e704ad7b46e7ae
    2.524  CMD 0x2019 LE Start Encryption 40000000000000000000000064ad9cd9910e2a90a90459f52decc43e
    2.525  EVT Command Status 0x2019 LE Start Encryption 状态 00
    2.914  EVT Encryption Change 00400001
    2.914  CMD 0x0c7c  4000b80b
    2.915  TX Pi→H10 ATT Read Req【请求】 2f00
    2.915  EVT Command Complete 0x0c7c  状态 00
    2.963  RX H10→Pi SMP Identity Info ac0b2efde582b3253f1808d526020e1f
    3.012  RX H10→Pi SMP Identity Addr Info 00d4cc11acac24
    3.159  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    3.159  TX Pi→H10 ATT Write Req【请求】 26000100
    3.353  RX H10→Pi ATT Write Rsp 
    3.353  TX Pi→H10 ATT Write Req【请求】 30000200
    3.451  RX H10→Pi ATT Write Rsp 
    3.452  TX Pi→H10 ATT Write Req【请求】 33000100
    3.548  RX H10→Pi ATT Write Rsp 
    3.549  TX Pi→H10 ATT Write Req【请求】 11000100
    3.645  RX H10→Pi ATT Write Rsp 
    3.646  TX Pi→H10 ATT Write Req【请求】 2f000100
    3.743  RX H10→Pi ATT Write Rsp 
    3.744  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    3.744  TX Pi→H10 ATT Confirm 
    3.745  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    3.889  RX H10→Pi ATT Write Rsp 
    3.890  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    3.890  TX Pi→H10 ATT Confirm 
    3.891  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    3.891  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    3.891  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    3.891  EVT Command Status 0x2013 LE Conn Update 状态 00
    3.903  TX Pi→H10 ATT Write Req【请求】 2f000102
    4.084  RX H10→Pi ATT Write Rsp 
    4.085  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    4.086  TX Pi→H10 ATT Confirm 
    4.086  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    4.182  RX H10→Pi ATT Write Rsp 
    4.182  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    4.182  TX Pi→H10 ATT Confirm 
    4.317  EVT LE Conn Update Complete 004000270000005802
    4.514  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 1 个）
  304.206  TX Pi→H10 ATT Write Req【请求】 2f000300
  304.268  RX H10→Pi ATT Write Rsp 
  304.268  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  304.268  TX Pi→H10 ATT Confirm 
  304.269  TX Pi→H10 ATT Write Req【请求】 2f000302
  304.414  RX H10→Pi ATT Write Rsp 
  304.415  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  304.415  TX Pi→H10 ATT Confirm 
  306.383  CMD 0x0406 Disconnect 400013
  306.383  EVT Command Status 0x0406 Disconnect 状态 00
  306.413  EVT Disconnection Complete 00400016
```
