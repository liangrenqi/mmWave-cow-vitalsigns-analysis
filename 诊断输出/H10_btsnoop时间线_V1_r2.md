# btsnoop 时间线（省略 HR/PMD 数据通知与续传分片；t=0 为首个 Connection Complete）

## H10原始日志/V1_r2.btsnoop

HR 通知 303、PMD 数据包 2247、首个 PMD 在 t=4.528242

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac24270000002a0000
    0.017  CMD 0x2016 LE Read Remote Features 4000
    0.017  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.103  EVT LE Read Remote Features 0040002500000000000000
    0.104  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.250  EVT LE Data Length Change 4000ec00d007ec00d007
    0.298  RX H10→Pi ATT Exchange MTU Rsp e800
    0.298  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.444  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.444  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    0.543  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    0.543  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    0.640  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    0.640  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    0.786  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    0.786  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0128
    0.883  RX H10→Pi ATT Error Rsp 对 Read By Group Type Req 句柄 0x0001 错误 0x0a
    0.883  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0228
    1.029  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.029  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0328
    1.177  RX H10→Pi ATT Read By Type Rsp 070200020300002a0400020500012a0600020700042a0800020900a62a0b00200c00052a0f00101000372a1200021300382a1500021600292a1700021800242a1900021a00252a1b00021c00272a1d00021e00262a1f00022000282a2100022200232a2400122500192a
    1.177  TX Pi→H10 ATT Read By Type Req【请求】 2500ffff0328
    1.275  RX H10→Pi ATT Read By Type Rsp 1528000229002d8e7086d93a8013fbb1ecc84cff17622a00242b00f3a1a8bdd37c2a7ed091bb914dff17622e002a2f00c8f08d2dcd8aad1c87f3e702815c00fb3100103200c8f08d2dcd8aad1c87f3e702825c00fb35001c3600c8f08d2dcd8aad1c87f3e702515c00fb3800103900c8f08d2dcd8aad1c87f3e702525c00fb3b000c3c00c8f08d2dcd8aad1c87f3e702535c00fb
    1.275  TX Pi→H10 ATT Read By Type Req【请求】 3c00ffff0328
    1.419  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x003c 错误 0x0a
    1.419  TX Pi→H10 ATT Find Info Req【请求】 3d00ffff
    1.517  RX H10→Pi ATT Error Rsp 对 Find Info Req 句柄 0x003d 错误 0x0a
    1.530  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.664  RX H10→Pi ATT Write Rsp 
    1.664  TX Pi→H10 ATT Read Req【请求】 0300
    1.859  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.859  TX Pi→H10 ATT Read Req【请求】 0500
    1.956  RX H10→Pi ATT Read Rsp 4103
    1.956  TX Pi→H10 ATT Read Req【请求】 2500
    2.004  RX H10→Pi SMP Security Req 09
    2.004  TX Pi→H10 SMP Pairing Req 010009100d0f
    2.102  RX H10→Pi ATT Read Rsp 64
    2.102  TX Pi→H10 ATT Read Req【请求】 2f00
    2.151  RX H10→Pi SMP Pairing Rsp 030009100103
    2.152  TX Pi→H10 SMP Pairing Public Key 30e02482152904893385e45923d3943b03bee32703b4c0eb26214ce28f2b035e09d020e7cd835b57c660e03e2dbccb2b5153bd8459fb11c5a8c7d6ff32adb46a
    2.249  RX H10→Pi ATT Error Rsp 对 Read Req 句柄 0x002f 错误 0x05
    2.346  RX H10→Pi SMP Pairing Public Key 7a58365faed94a30c019f5edfd9c98072245e6de013ccc4106659f5a51c509bf95e7b3d50e56595f3ee65a5326e2d9fcc9eb9118c64df0ddc495778d406d6771
    2.347  RX H10→Pi SMP Pairing Confirm 4d272fe9cdc79de857c7cfe16dc26f21
    2.347  TX Pi→H10 SMP Pairing Random d87874f8d5314cd32bf689660fbaee70
    2.492  RX H10→Pi SMP Pairing Random 03d8b1160eb9baefb0d1ba4e393aae42
    2.492  TX Pi→H10 SMP DHKey Check 49279c65b56c2650bb271aea246914fe
    2.638  RX H10→Pi SMP DHKey Check bcb9602446391ea6a29fe609f78d9950
    2.638  CMD 0x2019 LE Start Encryption 40000000000000000000000065d3e6efa43ddaee8abc3995d4929360
    2.639  EVT Command Status 0x2019 LE Start Encryption 状态 00
    2.931  EVT Encryption Change 00400001
    2.931  CMD 0x0c7c  4000b80b
    2.931  TX Pi→H10 ATT Read Req【请求】 2f00
    2.931  EVT Command Complete 0x0c7c  状态 00
    2.979  RX H10→Pi SMP Identity Info ac0b2efde582b3253f1808d526020e1f
    3.028  RX H10→Pi SMP Identity Addr Info 00d4cc11acac24
    3.126  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    3.126  TX Pi→H10 ATT Write Req【请求】 26000100
    3.369  RX H10→Pi ATT Write Rsp 
    3.369  TX Pi→H10 ATT Write Req【请求】 30000200
    3.467  RX H10→Pi ATT Write Rsp 
    3.468  TX Pi→H10 ATT Write Req【请求】 33000100
    3.564  RX H10→Pi ATT Write Rsp 
    3.565  TX Pi→H10 ATT Write Req【请求】 11000100
    3.662  RX H10→Pi ATT Write Rsp 
    3.663  TX Pi→H10 ATT Write Req【请求】 2f000100
    3.759  RX H10→Pi ATT Write Rsp 
    3.760  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    3.760  TX Pi→H10 ATT Confirm 
    3.761  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    3.857  RX H10→Pi ATT Write Rsp 
    3.857  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    3.858  TX Pi→H10 ATT Confirm 
    3.858  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    3.858  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    3.858  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    3.859  EVT Command Status 0x2013 LE Conn Update 状态 00
    3.870  TX Pi→H10 ATT Write Req【请求】 2f000102
    4.052  RX H10→Pi ATT Write Rsp 
    4.053  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    4.053  TX Pi→H10 ATT Confirm 
    4.054  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    4.233  RX H10→Pi ATT Write Rsp 
    4.234  EVT LE Conn Update Complete 004000270000005802
    4.282  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    4.282  TX Pi→H10 ATT Confirm 
    4.528  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 1 个）
  304.310  TX Pi→H10 ATT Write Req【请求】 2f000300
  304.373  RX H10→Pi ATT Write Rsp 
  304.374  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  304.374  TX Pi→H10 ATT Confirm 
  304.375  TX Pi→H10 ATT Write Req【请求】 2f000302
  304.471  RX H10→Pi ATT Write Rsp 
  304.471  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  304.472  TX Pi→H10 ATT Confirm 
  306.902  CMD 0x0406 Disconnect 400013
  306.902  EVT Command Status 0x0406 Disconnect 状态 00
  306.909  EVT Disconnection Complete 00400016
```
