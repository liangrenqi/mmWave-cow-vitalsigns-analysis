# btsnoop 时间线（省略 HR/PMD 数据通知与续传分片；t=0 为首个 Connection Complete）

## H10原始日志/V1_r1.btsnoop

HR 通知 303、PMD 数据包 2246、首个 PMD 在 t=4.598356

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac24270000002a0000
    0.019  CMD 0x2016 LE Read Remote Features 4000
    0.019  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.145  EVT LE Read Remote Features 0040002500000000000000
    0.145  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.340  EVT LE Data Length Change 4000ec00d007ec00d007
    0.388  RX H10→Pi ATT Exchange MTU Rsp e800
    0.388  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.486  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.486  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    0.584  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    0.584  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    0.681  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    0.681  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    0.778  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    0.778  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0128
    0.924  RX H10→Pi ATT Error Rsp 对 Read By Group Type Req 句柄 0x0001 错误 0x0a
    0.924  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0228
    1.022  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.022  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0328
    1.218  RX H10→Pi ATT Read By Type Rsp 070200020300002a0400020500012a0600020700042a0800020900a62a0b00200c00052a0f00101000372a1200021300382a1500021600292a1700021800242a1900021a00252a1b00021c00272a1d00021e00262a1f00022000282a2100022200232a2400122500192a
    1.218  TX Pi→H10 ATT Read By Type Req【请求】 2500ffff0328
    1.365  RX H10→Pi ATT Read By Type Rsp 1528000229002d8e7086d93a8013fbb1ecc84cff17622a00242b00f3a1a8bdd37c2a7ed091bb914dff17622e002a2f00c8f08d2dcd8aad1c87f3e702815c00fb3100103200c8f08d2dcd8aad1c87f3e702825c00fb35001c3600c8f08d2dcd8aad1c87f3e702515c00fb3800103900c8f08d2dcd8aad1c87f3e702525c00fb3b000c3c00c8f08d2dcd8aad1c87f3e702535c00fb
    1.365  TX Pi→H10 ATT Read By Type Req【请求】 3c00ffff0328
    1.461  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x003c 错误 0x0a
    1.461  TX Pi→H10 ATT Find Info Req【请求】 3d00ffff
    1.607  RX H10→Pi ATT Error Rsp 对 Find Info Req 句柄 0x003d 错误 0x0a
    1.624  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.705  RX H10→Pi ATT Write Rsp 
    1.705  TX Pi→H10 ATT Read Req【请求】 0300
    1.802  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.803  TX Pi→H10 ATT Read Req【请求】 0500
    1.899  RX H10→Pi ATT Read Rsp 4103
    1.899  TX Pi→H10 ATT Read Req【请求】 2500
    1.997  RX H10→Pi ATT Read Rsp 64
    1.997  TX Pi→H10 ATT Read Req【请求】 2f00
    1.997  RX H10→Pi SMP Security Req 09
    1.997  TX Pi→H10 SMP Pairing Req 010009100d0f
    2.046  RX H10→Pi ATT Error Rsp 对 Read Req 句柄 0x002f 错误 0x05
    2.094  RX H10→Pi SMP Pairing Rsp 030009100103
    2.096  TX Pi→H10 SMP Pairing Public Key b32ccf4804e82e9a74e98907bf7f4df308b91e9c806d6b16ed5c43e49e4684235cc65a865c5e4bdad1a042e03c0fa59027bb03393bdc5caabf74051c24d41a6f
    2.192  RX H10→Pi SMP Pairing Public Key 7a58365faed94a30c019f5edfd9c98072245e6de013ccc4106659f5a51c509bf95e7b3d50e56595f3ee65a5326e2d9fcc9eb9118c64df0ddc495778d406d6771
    2.193  RX H10→Pi SMP Pairing Confirm 212929027c3bcca3fae739b46ef368ae
    2.193  TX Pi→H10 SMP Pairing Random ec33c75a0ab28a37d3e979b952853653
    2.289  RX H10→Pi SMP Pairing Random da14900278fd66588167e18036757a14
    2.290  TX Pi→H10 SMP DHKey Check 3516b24c706efd77ac021b18c0f7dac7
    2.533  RX H10→Pi SMP DHKey Check 9fe9d8e0067199b245a3f40bca72bab2
    2.533  CMD 0x2019 LE Start Encryption 4000000000000000000000000b37858edd1d50987b0463a8f2cacdc1
    2.534  EVT Command Status 0x2019 LE Start Encryption 状态 00
    2.874  EVT Encryption Change 00400001
    2.874  CMD 0x0c7c  4000b80b
    2.875  TX Pi→H10 ATT Read Req【请求】 2f00
    2.875  EVT Command Complete 0x0c7c  状态 00
    2.923  RX H10→Pi SMP Identity Info ac0b2efde582b3253f1808d526020e1f
    2.972  RX H10→Pi SMP Identity Addr Info 00d4cc11acac24
    3.070  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    3.070  TX Pi→H10 ATT Write Req【请求】 26000100
    3.167  RX H10→Pi ATT Write Rsp 
    3.167  TX Pi→H10 ATT Write Req【请求】 30000200
    3.362  RX H10→Pi ATT Write Rsp 
    3.363  TX Pi→H10 ATT Write Req【请求】 33000100
    3.459  RX H10→Pi ATT Write Rsp 
    3.460  TX Pi→H10 ATT Write Req【请求】 11000100
    3.557  RX H10→Pi ATT Write Rsp 
    3.558  TX Pi→H10 ATT Write Req【请求】 2f000100
    3.654  RX H10→Pi ATT Write Rsp 
    3.655  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    3.655  TX Pi→H10 ATT Confirm 
    3.656  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    3.801  RX H10→Pi ATT Write Rsp 
    3.801  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    3.801  TX Pi→H10 ATT Confirm 
    3.802  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    3.802  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    3.802  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    3.803  EVT Command Status 0x2013 LE Conn Update 状态 00
    3.813  TX Pi→H10 ATT Write Req【请求】 2f000102
    4.044  RX H10→Pi ATT Write Rsp 
    4.046  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    4.046  TX Pi→H10 ATT Confirm 
    4.047  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    4.157  EVT LE Conn Update Complete 004000270000005802
    4.254  RX H10→Pi ATT Write Rsp 
    4.255  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    4.255  TX Pi→H10 ATT Confirm 
    4.598  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 1 个）
  304.285  TX Pi→H10 ATT Write Req【请求】 2f000300
  304.350  RX H10→Pi ATT Write Rsp 
  304.351  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  304.351  TX Pi→H10 ATT Confirm 
  304.352  TX Pi→H10 ATT Write Req【请求】 2f000302
  304.448  RX H10→Pi ATT Write Rsp 
  304.448  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  304.448  TX Pi→H10 ATT Confirm 
  306.676  CMD 0x0406 Disconnect 400013
  306.676  EVT Command Status 0x0406 Disconnect 状态 00
  306.691  EVT Disconnection Complete 00400016
```
