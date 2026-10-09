# btsnoop 时间线（省略 HR/PMD 数据通知与续传分片；t=0 为首个 Connection Complete）

## H10原始日志/rootE_P_r1.btsnoop

HR 通知 104、PMD 数据包 711、首个 PMD 在 t=4.385161

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac24270000002a0000
    0.021  CMD 0x2016 LE Read Remote Features 4000
    0.022  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.187  EVT LE Read Remote Features 0040002500000000000000
    0.187  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.333  EVT LE Data Length Change 4000ec00d007ec00d007
    0.382  RX H10→Pi ATT Exchange MTU Rsp e800
    0.382  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.528  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.528  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    0.724  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    0.724  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    0.821  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    0.821  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    0.918  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    0.918  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0128
    1.016  RX H10→Pi ATT Error Rsp 对 Read By Group Type Req 句柄 0x0001 错误 0x0a
    1.016  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0228
    1.113  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.113  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0328
    1.212  RX H10→Pi ATT Read By Type Rsp 070200020300002a0400020500012a0600020700042a0800020900a62a0b00200c00052a0f00101000372a1200021300382a1500021600292a1700021800242a1900021a00252a1b00021c00272a1d00021e00262a1f00022000282a2100022200232a2400122500192a
    1.212  TX Pi→H10 ATT Read By Type Req【请求】 2500ffff0328
    1.310  RX H10→Pi ATT Read By Type Rsp 1528000229002d8e7086d93a8013fbb1ecc84cff17622a00242b00f3a1a8bdd37c2a7ed091bb914dff17622e002a2f00c8f08d2dcd8aad1c87f3e702815c00fb3100103200c8f08d2dcd8aad1c87f3e702825c00fb35001c3600c8f08d2dcd8aad1c87f3e702515c00fb3800103900c8f08d2dcd8aad1c87f3e702525c00fb3b000c3c00c8f08d2dcd8aad1c87f3e702535c00fb
    1.310  TX Pi→H10 ATT Read By Type Req【请求】 3c00ffff0328
    1.405  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x003c 错误 0x0a
    1.406  TX Pi→H10 ATT Find Info Req【请求】 3d00ffff
    1.503  RX H10→Pi ATT Error Rsp 对 Find Info Req 句柄 0x003d 错误 0x0a
    1.519  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.600  RX H10→Pi ATT Write Rsp 
    1.601  TX Pi→H10 ATT Read Req【请求】 0300
    1.698  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.699  TX Pi→H10 ATT Read Req【请求】 0500
    1.795  RX H10→Pi ATT Read Rsp 4103
    1.795  TX Pi→H10 ATT Read Req【请求】 2500
    1.893  RX H10→Pi ATT Read Rsp 64
    1.893  TX Pi→H10 ATT Read Req【请求】 2f00
    1.990  RX H10→Pi ATT Error Rsp 对 Read Req 句柄 0x002f 错误 0x05
    1.990  TX Pi→H10 SMP Pairing Req 01002d100d0f
    1.991  RX H10→Pi SMP Security Req 09
    2.088  RX H10→Pi SMP Pairing Rsp 030009100103
    2.089  TX Pi→H10 SMP Pairing Public Key cf6ab3acf00ba21f9593fc2718c07ea90a62ea8e1cc1a2360f396899f81ca8a41bf05aeb3cbfb68ac9eacb21168de8260407c9ab4e4f2b0737a611c531e04928
    2.235  RX H10→Pi SMP Pairing Public Key 9eea5a187d321e2c6f6b1767ada4787a6a44ad263cdcd1ca05b992fb5f633b1adfd13350ec0735dc8af64a6076598d4ec521f1b0fff1bdd7a0854376681878e5
    2.235  RX H10→Pi SMP Pairing Confirm 7ff1bf8f32544aa873219542484516cb
    2.235  TX Pi→H10 SMP Pairing Random a6dde4132acab947352db20a38297163
    2.332  RX H10→Pi SMP Pairing Random 2c6a4c60006323d2853b060fb81c0b4f
    2.332  TX Pi→H10 SMP DHKey Check 2a0ff566e969a52216dcc51df7fbdb26
    2.527  RX H10→Pi SMP DHKey Check 01e7d0e0cdcc7ad67d9d7caf3bc6bdb4
    2.527  CMD 0x2019 LE Start Encryption 400000000000000000000000e3191b66fc716180aa8537c3c5d3b081
    2.527  EVT Command Status 0x2019 LE Start Encryption 状态 00
    2.819  EVT Encryption Change 00400001
    2.819  CMD 0x0c7c  4000b80b
    2.819  TX Pi→H10 ATT Read Req【请求】 2f00
    2.819  EVT Command Complete 0x0c7c  状态 00
    2.868  RX H10→Pi SMP Identity Info ac0b2efde582b3253f1808d526020e1f
    2.916  RX H10→Pi SMP Identity Addr Info 00d4cc11acac24
    3.014  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    3.015  TX Pi→H10 ATT Write Req【请求】 26000100
    3.111  RX H10→Pi ATT Write Rsp 
    3.111  TX Pi→H10 ATT Write Req【请求】 30000200
    3.306  RX H10→Pi ATT Write Rsp 
    3.307  TX Pi→H10 ATT Write Req【请求】 33000100
    3.404  RX H10→Pi ATT Write Rsp 
    3.405  TX Pi→H10 ATT Write Req【请求】 11000100
    3.501  RX H10→Pi ATT Write Rsp 
    3.502  TX Pi→H10 ATT Write Req【请求】 2f000100
    3.599  RX H10→Pi ATT Write Rsp 
    3.599  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    3.600  TX Pi→H10 ATT Confirm 
    3.600  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    3.696  RX H10→Pi ATT Write Rsp 
    3.697  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    3.697  TX Pi→H10 ATT Confirm 
    3.698  TX Pi→H10 ATT Write Req【请求】 2f000102
    3.698  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    3.698  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    3.698  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    3.698  EVT Command Status 0x2013 LE Conn Update 状态 00
    3.892  RX H10→Pi ATT Write Rsp 
    3.893  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    3.893  TX Pi→H10 ATT Confirm 
    3.894  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    3.989  RX H10→Pi ATT Write Rsp 
    3.989  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    3.989  TX Pi→H10 ATT Confirm 
    4.042  EVT LE Conn Update Complete 004000270000005802
    4.385  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 1 个）
   48.991  TX Pi→H10 ATT Write Req【请求】 2f000300
   49.078  RX H10→Pi ATT Write Rsp 
   49.079  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   49.079  TX Pi→H10 ATT Confirm 
   49.079  TX Pi→H10 ATT Write Req【请求】 2f000302
   49.224  RX H10→Pi ATT Write Rsp 
   49.225  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   49.225  TX Pi→H10 ATT Confirm 
   54.226  TX Pi→H10 ATT Write Req【请求】 2f000100
   54.293  RX H10→Pi ATT Write Rsp 
   54.294  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   54.294  TX Pi→H10 ATT Confirm 
   54.295  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   54.391  RX H10→Pi ATT Write Rsp 
   54.391  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   54.392  TX Pi→H10 ATT Confirm 
   54.392  TX Pi→H10 ATT Write Req【请求】 2f000102
   54.488  RX H10→Pi ATT Write Rsp 
   54.489  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   54.490  TX Pi→H10 ATT Confirm 
   54.491  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   54.634  RX H10→Pi ATT Write Rsp 
   54.635  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   54.635  TX Pi→H10 ATT Confirm 
  104.641  TX Pi→H10 ATT Write Req【请求】 2f000300
  104.705  RX H10→Pi ATT Write Rsp 
  104.754  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  104.754  TX Pi→H10 ATT Confirm 
  104.755  TX Pi→H10 ATT Write Req【请求】 2f000302
  104.900  RX H10→Pi ATT Write Rsp 
  104.901  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  104.901  TX Pi→H10 ATT Confirm 
  107.306  CMD 0x0406 Disconnect 400013
  107.307  EVT Command Status 0x0406 Disconnect 状态 00
  107.338  EVT Disconnection Complete 00400016
```

## H10原始日志/rootE_P_r2.btsnoop

HR 通知 104、PMD 数据包 711、首个 PMD 在 t=4.531211

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac24270000002a0000
    0.019  CMD 0x2016 LE Read Remote Features 4000
    0.019  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.124  EVT LE Read Remote Features 0040002500000000000000
    0.124  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.270  EVT LE Data Length Change 4000ec00d007ec00d007
    0.319  RX H10→Pi ATT Exchange MTU Rsp e800
    0.319  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.416  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.416  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    0.514  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    0.514  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    0.661  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    0.661  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    0.758  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    0.758  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0128
    0.855  RX H10→Pi ATT Error Rsp 对 Read By Group Type Req 句柄 0x0001 错误 0x0a
    0.855  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0228
    0.952  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.952  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0328
    1.052  RX H10→Pi ATT Read By Type Rsp 070200020300002a0400020500012a0600020700042a0800020900a62a0b00200c00052a0f00101000372a1200021300382a1500021600292a1700021800242a1900021a00252a1b00021c00272a1d00021e00262a1f00022000282a2100022200232a2400122500192a
    1.052  TX Pi→H10 ATT Read By Type Req【请求】 2500ffff0328
    1.149  RX H10→Pi ATT Read By Type Rsp 1528000229002d8e7086d93a8013fbb1ecc84cff17622a00242b00f3a1a8bdd37c2a7ed091bb914dff17622e002a2f00c8f08d2dcd8aad1c87f3e702815c00fb3100103200c8f08d2dcd8aad1c87f3e702825c00fb35001c3600c8f08d2dcd8aad1c87f3e702515c00fb3800103900c8f08d2dcd8aad1c87f3e702525c00fb3b000c3c00c8f08d2dcd8aad1c87f3e702535c00fb
    1.149  TX Pi→H10 ATT Read By Type Req【请求】 3c00ffff0328
    1.245  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x003c 错误 0x0a
    1.245  TX Pi→H10 ATT Find Info Req【请求】 3d00ffff
    1.342  RX H10→Pi ATT Error Rsp 对 Find Info Req 句柄 0x003d 错误 0x0a
    1.359  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.440  RX H10→Pi ATT Write Rsp 
    1.440  TX Pi→H10 ATT Read Req【请求】 0300
    1.538  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.538  TX Pi→H10 ATT Read Req【请求】 0500
    1.635  RX H10→Pi ATT Read Rsp 4103
    1.635  TX Pi→H10 ATT Read Req【请求】 2500
    1.732  RX H10→Pi ATT Read Rsp 64
    1.732  TX Pi→H10 ATT Read Req【请求】 2f00
    1.830  RX H10→Pi ATT Error Rsp 对 Read Req 句柄 0x002f 错误 0x05
    1.830  TX Pi→H10 SMP Pairing Req 01002d100d0f
    1.927  RX H10→Pi SMP Pairing Rsp 030009100103
    1.929  TX Pi→H10 SMP Pairing Public Key 2f4161f4ab6b1a59e9b35035c4ae5a0d7db155b71e80a3f0a8f6847ecc730a6922fae23310d0225003e509378c610581e7e33333880db69df711ed343847b9b4
    2.026  RX H10→Pi SMP Pairing Public Key 9eea5a187d321e2c6f6b1767ada4787a6a44ad263cdcd1ca05b992fb5f633b1adfd13350ec0735dc8af64a6076598d4ec521f1b0fff1bdd7a0854376681878e5
    2.026  RX H10→Pi SMP Pairing Confirm ce776694f93888ad82fb613fcdefa035
    2.026  TX Pi→H10 SMP Pairing Random c8324f97c1fc237575ad68280ea76210
    2.123  RX H10→Pi SMP Pairing Random 187d9fc600927e4f162e067e9abc05e5
    2.123  TX Pi→H10 SMP DHKey Check 5d4056e5387399e02a0e434d2eb3783a
    2.366  RX H10→Pi SMP DHKey Check ed1161d9429b4cc50d93afcc2d66cd9d
    2.366  CMD 0x2019 LE Start Encryption 400000000000000000000000f3c18af4c391d002114962520ef2a7cd
    2.367  EVT Command Status 0x2019 LE Start Encryption 状态 00
    2.707  EVT Encryption Change 00400001
    2.707  CMD 0x0c7c  4000b80b
    2.708  TX Pi→H10 ATT Read Req【请求】 2f00
    2.708  EVT Command Complete 0x0c7c  状态 00
    2.805  RX H10→Pi SMP Identity Info ac0b2efde582b3253f1808d526020e1f
    2.854  RX H10→Pi SMP Identity Addr Info 00d4cc11acac24
    2.952  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    2.952  TX Pi→H10 ATT Write Req【请求】 26000100
    3.195  RX H10→Pi ATT Write Rsp 
    3.195  TX Pi→H10 ATT Write Req【请求】 30000200
    3.341  RX H10→Pi ATT Write Rsp 
    3.342  TX Pi→H10 ATT Write Req【请求】 33000100
    3.536  RX H10→Pi ATT Write Rsp 
    3.537  TX Pi→H10 ATT Write Req【请求】 11000100
    3.633  RX H10→Pi ATT Write Rsp 
    3.635  TX Pi→H10 ATT Write Req【请求】 2f000100
    3.780  RX H10→Pi ATT Write Rsp 
    3.780  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    3.781  TX Pi→H10 ATT Confirm 
    3.781  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    3.877  RX H10→Pi ATT Write Rsp 
    3.878  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    3.878  TX Pi→H10 ATT Confirm 
    3.878  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    3.878  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    3.879  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    3.879  EVT Command Status 0x2013 LE Conn Update 状态 00
    3.891  TX Pi→H10 ATT Write Req【请求】 2f000102
    4.072  RX H10→Pi ATT Write Rsp 
    4.073  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    4.073  TX Pi→H10 ATT Confirm 
    4.074  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    4.170  RX H10→Pi ATT Write Rsp 
    4.170  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    4.170  TX Pi→H10 ATT Confirm 
    4.334  EVT LE Conn Update Complete 004000270000005802
    4.531  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 1 个）
   49.172  TX Pi→H10 ATT Write Req【请求】 2f000300
   49.277  RX H10→Pi ATT Write Rsp 
   49.277  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   49.277  TX Pi→H10 ATT Confirm 
   49.278  TX Pi→H10 ATT Write Req【请求】 2f000302
   49.374  RX H10→Pi ATT Write Rsp 
   49.375  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   49.375  TX Pi→H10 ATT Confirm 
   54.376  TX Pi→H10 ATT Write Req【请求】 2f000100
   54.444  RX H10→Pi ATT Write Rsp 
   54.444  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   54.445  TX Pi→H10 ATT Confirm 
   54.445  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   54.541  RX H10→Pi ATT Write Rsp 
   54.542  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   54.542  TX Pi→H10 ATT Confirm 
   54.543  TX Pi→H10 ATT Write Req【请求】 2f000102
   54.639  RX H10→Pi ATT Write Rsp 
   54.640  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   54.640  TX Pi→H10 ATT Confirm 
   54.641  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   54.736  RX H10→Pi ATT Write Rsp 
   54.737  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   54.737  TX Pi→H10 ATT Confirm 
  104.742  TX Pi→H10 ATT Write Req【请求】 2f000300
  104.797  RX H10→Pi ATT Write Rsp 
  104.797  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  104.797  TX Pi→H10 ATT Confirm 
  104.798  TX Pi→H10 ATT Write Req【请求】 2f000302
  104.894  RX H10→Pi ATT Write Rsp 
  104.895  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  104.895  TX Pi→H10 ATT Confirm 
  107.424  CMD 0x0406 Disconnect 400013
  107.424  EVT Command Status 0x0406 Disconnect 状态 00
  107.429  EVT Disconnection Complete 00400016
```

## H10原始日志/rootE_P_r3.btsnoop

HR 通知 104、PMD 数据包 710、首个 PMD 在 t=4.435996

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac24270000002a0000
    0.016  CMD 0x2016 LE Read Remote Features 4000
    0.017  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.115  EVT LE Read Remote Features 0040002500000000000000
    0.115  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.262  EVT LE Data Length Change 4000ec00d007ec00d007
    0.310  RX H10→Pi ATT Exchange MTU Rsp e800
    0.310  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.407  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.408  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    0.506  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    0.506  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    0.652  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    0.652  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    0.749  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    0.749  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0128
    0.895  RX H10→Pi ATT Error Rsp 对 Read By Group Type Req 句柄 0x0001 错误 0x0a
    0.895  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0228
    1.041  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.041  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0328
    1.140  RX H10→Pi ATT Read By Type Rsp 070200020300002a0400020500012a0600020700042a0800020900a62a0b00200c00052a0f00101000372a1200021300382a1500021600292a1700021800242a1900021a00252a1b00021c00272a1d00021e00262a1f00022000282a2100022200232a2400122500192a
    1.140  TX Pi→H10 ATT Read By Type Req【请求】 2500ffff0328
    1.238  RX H10→Pi ATT Read By Type Rsp 1528000229002d8e7086d93a8013fbb1ecc84cff17622a00242b00f3a1a8bdd37c2a7ed091bb914dff17622e002a2f00c8f08d2dcd8aad1c87f3e702815c00fb3100103200c8f08d2dcd8aad1c87f3e702825c00fb35001c3600c8f08d2dcd8aad1c87f3e702515c00fb3800103900c8f08d2dcd8aad1c87f3e702525c00fb3b000c3c00c8f08d2dcd8aad1c87f3e702535c00fb
    1.238  TX Pi→H10 ATT Read By Type Req【请求】 3c00ffff0328
    1.334  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x003c 错误 0x0a
    1.334  TX Pi→H10 ATT Find Info Req【请求】 3d00ffff
    1.431  RX H10→Pi ATT Error Rsp 对 Find Info Req 句柄 0x003d 错误 0x0a
    1.445  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.529  RX H10→Pi ATT Write Rsp 
    1.529  TX Pi→H10 ATT Read Req【请求】 0300
    1.627  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.627  TX Pi→H10 ATT Read Req【请求】 0500
    1.724  RX H10→Pi ATT Read Rsp 4103
    1.724  TX Pi→H10 ATT Read Req【请求】 2500
    1.870  RX H10→Pi ATT Read Rsp 64
    1.870  TX Pi→H10 ATT Read Req【请求】 2f00
    1.967  RX H10→Pi ATT Error Rsp 对 Read Req 句柄 0x002f 错误 0x05
    1.967  TX Pi→H10 SMP Pairing Req 01002d100d0f
    2.016  RX H10→Pi SMP Security Req 09
    2.065  RX H10→Pi SMP Pairing Rsp 030009100103
    2.066  TX Pi→H10 SMP Pairing Public Key c3318ab8ba7836b162d9d6dc4d47fa277e00e25a16d04d5de0a3e829ca0631e7024c7b7f98af6ed6532a963c4571bb054a624d40b3b8ef075e041815c96d401c
    2.163  RX H10→Pi SMP Pairing Public Key 9eea5a187d321e2c6f6b1767ada4787a6a44ad263cdcd1ca05b992fb5f633b1adfd13350ec0735dc8af64a6076598d4ec521f1b0fff1bdd7a0854376681878e5
    2.163  RX H10→Pi SMP Pairing Confirm 9ce8c520fba6bddbe1e25ee16055c0b6
    2.164  TX Pi→H10 SMP Pairing Random 6505859834acd0a0cd00b4a19a53be8f
    2.260  RX H10→Pi SMP Pairing Random d0366d60003126bc360250dc1c6580d4
    2.260  TX Pi→H10 SMP DHKey Check e47d3364831c8b5e7c5b7e07c5525fc6
    2.504  RX H10→Pi SMP DHKey Check 2714f932e390b3ed2257e8d570aaf086
    2.504  CMD 0x2019 LE Start Encryption 400000000000000000000000328ff63e6218b6d690da13150aa34d6a
    2.504  EVT Command Status 0x2019 LE Start Encryption 状态 00
    2.845  EVT Encryption Change 00400001
    2.845  CMD 0x0c7c  4000b80b
    2.845  TX Pi→H10 ATT Read Req【请求】 2f00
    2.845  EVT Command Complete 0x0c7c  状态 00
    2.894  RX H10→Pi SMP Identity Info ac0b2efde582b3253f1808d526020e1f
    2.942  RX H10→Pi SMP Identity Addr Info 00d4cc11acac24
    3.040  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    3.040  TX Pi→H10 ATT Write Req【请求】 26000100
    3.235  RX H10→Pi ATT Write Rsp 
    3.235  TX Pi→H10 ATT Write Req【请求】 30000200
    3.332  RX H10→Pi ATT Write Rsp 
    3.333  TX Pi→H10 ATT Write Req【请求】 33000100
    3.430  RX H10→Pi ATT Write Rsp 
    3.431  TX Pi→H10 ATT Write Req【请求】 11000100
    3.527  RX H10→Pi ATT Write Rsp 
    3.529  TX Pi→H10 ATT Write Req【请求】 2f000100
    3.625  RX H10→Pi ATT Write Rsp 
    3.625  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    3.625  TX Pi→H10 ATT Confirm 
    3.626  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    3.771  RX H10→Pi ATT Write Rsp 
    3.771  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    3.771  TX Pi→H10 ATT Confirm 
    3.772  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    3.772  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    3.772  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    3.773  EVT Command Status 0x2013 LE Conn Update 状态 00
    3.788  TX Pi→H10 ATT Write Req【请求】 2f000102
    4.014  RX H10→Pi ATT Write Rsp 
    4.016  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    4.016  TX Pi→H10 ATT Confirm 
    4.017  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    4.112  RX H10→Pi ATT Write Rsp 
    4.113  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    4.113  TX Pi→H10 ATT Confirm 
    4.190  EVT LE Conn Update Complete 004000270000005802
    4.436  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 1 个）
   49.114  TX Pi→H10 ATT Write Req【请求】 2f000300
   49.180  RX H10→Pi ATT Write Rsp 
   49.180  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   49.181  TX Pi→H10 ATT Confirm 
   49.181  TX Pi→H10 ATT Write Req【请求】 2f000302
   49.326  RX H10→Pi ATT Write Rsp 
   49.326  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   49.327  TX Pi→H10 ATT Confirm 
   54.329  TX Pi→H10 ATT Write Req【请求】 2f000100
   54.395  RX H10→Pi ATT Write Rsp 
   54.396  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   54.396  TX Pi→H10 ATT Confirm 
   54.397  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   54.541  RX H10→Pi ATT Write Rsp 
   54.542  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   54.542  TX Pi→H10 ATT Confirm 
   54.543  TX Pi→H10 ATT Write Req【请求】 2f000102
   54.639  RX H10→Pi ATT Write Rsp 
   54.640  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   54.640  TX Pi→H10 ATT Confirm 
   54.641  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   54.834  RX H10→Pi ATT Write Rsp 
   54.834  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   54.835  TX Pi→H10 ATT Confirm 
  104.840  TX Pi→H10 ATT Write Req【请求】 2f000300
  104.893  RX H10→Pi ATT Write Rsp 
  104.894  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  104.894  TX Pi→H10 ATT Confirm 
  104.895  TX Pi→H10 ATT Write Req【请求】 2f000302
  104.942  RX H10→Pi ATT Write Rsp 
  104.942  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  104.942  TX Pi→H10 ATT Confirm 
  106.905  CMD 0x0406 Disconnect 400013
  106.905  EVT Command Status 0x0406 Disconnect 状态 00
  106.941  EVT Disconnection Complete 00400016
```

## H10原始日志/rootE_B_r1.btsnoop

HR 通知 106、PMD 数据包 489、首个 PMD 在 t=32.314483

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.015  CMD 0x2016 LE Read Remote Features 4000
    0.015  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.105  EVT LE Read Remote Features 0040002500000000000000
    0.105  CMD 0x2019 LE Start Encryption 400000000000000000000000328ff63e6218b6d690da13150aa34d6a
    0.105  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.251  EVT LE Data Length Change 4000ec00d007ec00d007
    0.543  EVT Encryption Change 00400001
    0.543  CMD 0x0c7c  4000b80b
    0.543  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.544  EVT Command Complete 0x0c7c  状态 00
    0.641  RX H10→Pi ATT Exchange MTU Rsp e800
    0.641  TX Pi→H10 ATT Read Req【请求】 0300
    0.739  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.739  TX Pi→H10 ATT Read Req【请求】 2500
    0.836  RX H10→Pi ATT Read Rsp 64
    0.836  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.933  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.933  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.031  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.031  TX Pi→H10 ATT Write Req【请求】 26000100
    1.128  RX H10→Pi ATT Write Rsp 
    1.128  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.226  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.226  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.323  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.353  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.420  RX H10→Pi ATT Write Rsp 
    1.420  TX Pi→H10 ATT Read Req【请求】 2f00
    1.519  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.520  TX Pi→H10 ATT Write Req【请求】 30000200
    1.615  RX H10→Pi ATT Write Rsp 
    1.616  TX Pi→H10 ATT Write Req【请求】 33000100
    1.713  RX H10→Pi ATT Write Rsp 
    1.714  TX Pi→H10 ATT Write Req【请求】 11000100
    1.810  RX H10→Pi ATT Write Rsp 
    1.811  TX Pi→H10 ATT Write Req【请求】 2f000100
    1.908  RX H10→Pi ATT Write Rsp 
    1.909  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    1.909  TX Pi→H10 ATT Confirm 
    1.909  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.005  RX H10→Pi ATT Write Rsp 
    2.006  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.006  TX Pi→H10 ATT Confirm 
    2.007  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.007  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.007  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.007  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.021  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.249  RX H10→Pi ATT Write Rsp 
    2.250  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.250  TX Pi→H10 ATT Confirm 
    2.251  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.373  RX H10→Pi ATT Write Rsp 
    2.373  EVT LE Conn Update Complete 004000270000005802
    2.422  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.422  TX Pi→H10 ATT Confirm 
   32.314  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 32 个）
   47.424  TX Pi→H10 ATT Write Req【请求】 2f000300
   47.478  RX H10→Pi ATT Write Rsp 
   47.479  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   47.479  TX Pi→H10 ATT Confirm 
   47.480  TX Pi→H10 ATT Write Req【请求】 2f000302
   47.576  RX H10→Pi ATT Write Rsp 
   47.576  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   47.577  TX Pi→H10 ATT Confirm 
   52.578  TX Pi→H10 ATT Write Req【请求】 2f000100
   52.647  RX H10→Pi ATT Write Rsp 
   52.648  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   52.648  TX Pi→H10 ATT Confirm 
   52.649  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   52.745  RX H10→Pi ATT Write Rsp 
   52.746  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   52.746  TX Pi→H10 ATT Confirm 
   52.747  TX Pi→H10 ATT Write Req【请求】 2f000102
   52.843  RX H10→Pi ATT Write Rsp 
   52.844  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   52.844  TX Pi→H10 ATT Confirm 
   52.845  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   52.940  RX H10→Pi ATT Write Rsp 
   52.941  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   52.941  TX Pi→H10 ATT Confirm 
  102.946  TX Pi→H10 ATT Write Req【请求】 2f000300
  103.019  RX H10→Pi ATT Write Rsp 
  103.019  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  103.019  TX Pi→H10 ATT Confirm 
  103.020  TX Pi→H10 ATT Write Req【请求】 2f000302
  103.116  RX H10→Pi ATT Write Rsp 
  103.117  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  103.117  TX Pi→H10 ATT Confirm 
  105.799  CMD 0x0406 Disconnect 400013
  105.800  EVT Command Status 0x0406 Disconnect 状态 00
  105.847  EVT Disconnection Complete 00400016
```

## H10原始日志/rootE_B_r2.btsnoop

HR 通知 105、PMD 数据包 488、首个 PMD 在 t=32.645169

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.014  CMD 0x2016 LE Read Remote Features 4000
    0.014  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.133  EVT LE Read Remote Features 0040002500000000000000
    0.133  CMD 0x2019 LE Start Encryption 400000000000000000000000328ff63e6218b6d690da13150aa34d6a
    0.134  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.328  EVT LE Data Length Change 4000ec00d007ec00d007
    0.621  EVT Encryption Change 00400001
    0.621  CMD 0x0c7c  4000b80b
    0.621  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.621  EVT Command Complete 0x0c7c  状态 00
    0.767  RX H10→Pi ATT Exchange MTU Rsp e800
    0.767  TX Pi→H10 ATT Read Req【请求】 0300
    0.865  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.865  TX Pi→H10 ATT Read Req【请求】 2500
    0.962  RX H10→Pi ATT Read Rsp 64
    0.962  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.108  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.108  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.206  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.206  TX Pi→H10 ATT Write Req【请求】 26000100
    1.303  RX H10→Pi ATT Write Rsp 
    1.303  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.402  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.402  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.547  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.567  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.645  RX H10→Pi ATT Write Rsp 
    1.645  TX Pi→H10 ATT Read Req【请求】 2f00
    1.791  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.793  TX Pi→H10 ATT Write Req【请求】 30000200
    1.888  RX H10→Pi ATT Write Rsp 
    1.889  TX Pi→H10 ATT Write Req【请求】 33000100
    1.986  RX H10→Pi ATT Write Rsp 
    1.987  TX Pi→H10 ATT Write Req【请求】 11000100
    2.083  RX H10→Pi ATT Write Rsp 
    2.084  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.181  RX H10→Pi ATT Write Rsp 
    2.182  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.182  TX Pi→H10 ATT Confirm 
    2.182  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.278  RX H10→Pi ATT Write Rsp 
    2.279  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.279  TX Pi→H10 ATT Confirm 
    2.280  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.280  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.280  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.280  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.291  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.522  RX H10→Pi ATT Write Rsp 
    2.523  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.524  TX Pi→H10 ATT Confirm 
    2.524  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.659  EVT LE Conn Update Complete 004000270000005802
    2.707  RX H10→Pi ATT Write Rsp 
    2.708  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.708  TX Pi→H10 ATT Confirm 
   32.645  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 32 个）
   47.710  TX Pi→H10 ATT Write Req【请求】 2f000300
   47.805  RX H10→Pi ATT Write Rsp 
   47.805  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   47.805  TX Pi→H10 ATT Confirm 
   47.806  TX Pi→H10 ATT Write Req【请求】 2f000302
   47.902  RX H10→Pi ATT Write Rsp 
   47.903  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   47.903  TX Pi→H10 ATT Confirm 
   52.905  TX Pi→H10 ATT Write Req【请求】 2f000100
   52.972  RX H10→Pi ATT Write Rsp 
   52.973  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   52.973  TX Pi→H10 ATT Confirm 
   52.974  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   53.070  RX H10→Pi ATT Write Rsp 
   53.070  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   53.071  TX Pi→H10 ATT Confirm 
   53.071  TX Pi→H10 ATT Write Req【请求】 2f000102
   53.167  RX H10→Pi ATT Write Rsp 
   53.169  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   53.169  TX Pi→H10 ATT Confirm 
   53.170  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   53.265  RX H10→Pi ATT Write Rsp 
   53.265  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   53.266  TX Pi→H10 ATT Confirm 
  103.272  TX Pi→H10 ATT Write Req【请求】 2f000300
  103.332  RX H10→Pi ATT Write Rsp 
  103.333  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  103.333  TX Pi→H10 ATT Confirm 
  103.334  TX Pi→H10 ATT Write Req【请求】 2f000302
  103.381  RX H10→Pi ATT Write Rsp 
  103.382  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  103.382  TX Pi→H10 ATT Confirm 
  105.383  CMD 0x0406 Disconnect 400013
  105.383  EVT Command Status 0x0406 Disconnect 状态 00
  105.429  EVT Disconnection Complete 00400016
```

## H10原始日志/rootE_B_r3.btsnoop

HR 通知 105、PMD 数据包 489、首个 PMD 在 t=33.24795

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.023  CMD 0x2016 LE Read Remote Features 4000
    0.023  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.137  EVT LE Read Remote Features 0040002500000000000000
    0.137  CMD 0x2019 LE Start Encryption 400000000000000000000000328ff63e6218b6d690da13150aa34d6a
    0.138  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.283  EVT LE Data Length Change 4000ec00d007ec00d007
    0.576  EVT Encryption Change 00400001
    0.576  CMD 0x0c7c  4000b80b
    0.576  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.576  EVT Command Complete 0x0c7c  状态 00
    0.673  RX H10→Pi ATT Exchange MTU Rsp e800
    0.673  TX Pi→H10 ATT Read Req【请求】 0300
    0.771  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.771  TX Pi→H10 ATT Read Req【请求】 2500
    0.868  RX H10→Pi ATT Read Rsp 64
    0.868  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.014  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.014  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.112  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.113  TX Pi→H10 ATT Write Req【请求】 26000100
    1.209  RX H10→Pi ATT Write Rsp 
    1.209  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.356  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.356  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.502  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.528  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.599  RX H10→Pi ATT Write Rsp 
    1.599  TX Pi→H10 ATT Read Req【请求】 2f00
    1.697  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.699  TX Pi→H10 ATT Write Req【请求】 30000200
    1.794  RX H10→Pi ATT Write Rsp 
    1.795  TX Pi→H10 ATT Write Req【请求】 33000100
    1.892  RX H10→Pi ATT Write Rsp 
    1.893  TX Pi→H10 ATT Write Req【请求】 11000100
    1.989  RX H10→Pi ATT Write Rsp 
    1.990  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.087  RX H10→Pi ATT Write Rsp 
    2.087  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.087  TX Pi→H10 ATT Confirm 
    2.088  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.233  RX H10→Pi ATT Write Rsp 
    2.234  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.234  TX Pi→H10 ATT Confirm 
    2.234  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.234  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.234  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.235  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.246  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.525  RX H10→Pi ATT Write Rsp 
    2.527  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.527  TX Pi→H10 ATT Confirm 
    2.528  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.672  RX H10→Pi ATT Write Rsp 
    2.672  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.673  TX Pi→H10 ATT Confirm 
    2.742  EVT LE Conn Update Complete 004000270000005802
   33.248  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 32 个）
   48.345  TX Pi→H10 ATT Write Req【请求】 2f000300
   48.454  RX H10→Pi ATT Write Rsp 
   48.454  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   48.455  TX Pi→H10 ATT Confirm 
   48.455  TX Pi→H10 ATT Write Req【请求】 2f000302
   48.551  RX H10→Pi ATT Write Rsp 
   48.552  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   48.552  TX Pi→H10 ATT Confirm 
   53.555  TX Pi→H10 ATT Write Req【请求】 2f000100
   53.621  RX H10→Pi ATT Write Rsp 
   53.622  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   53.622  TX Pi→H10 ATT Confirm 
   53.623  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   53.718  RX H10→Pi ATT Write Rsp 
   53.719  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   53.719  TX Pi→H10 ATT Confirm 
   53.720  TX Pi→H10 ATT Write Req【请求】 2f000102
   53.865  RX H10→Pi ATT Write Rsp 
   53.866  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   53.866  TX Pi→H10 ATT Confirm 
   53.867  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   53.962  RX H10→Pi ATT Write Rsp 
   53.963  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   53.963  TX Pi→H10 ATT Confirm 
  103.967  TX Pi→H10 ATT Write Req【请求】 2f000300
  104.026  RX H10→Pi ATT Write Rsp 
  104.026  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  104.026  TX Pi→H10 ATT Confirm 
  104.027  TX Pi→H10 ATT Write Req【请求】 2f000302
  104.123  RX H10→Pi ATT Write Rsp 
  104.124  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  104.124  TX Pi→H10 ATT Confirm 
  105.930  CMD 0x0406 Disconnect 400013
  105.931  EVT Command Status 0x0406 Disconnect 状态 00
  106.025  EVT Disconnection Complete 00400016
```
