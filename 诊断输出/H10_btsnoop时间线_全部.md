# btsnoop 时间线（省略 HR/PMD 数据通知与续传分片；t=0 为首个 Connection Complete）

## H10原始日志/r2_wifi_off.btsnoop

HR 通知 24、PMD 数据包 151、首个 PMD 在 t=5.163982

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac24270000002a0000
    0.020  CMD 0x2016 LE Read Remote Features 4000
    0.020  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.111  EVT LE Read Remote Features 0040002500000000000000
    0.112  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.258  EVT LE Data Length Change 4000ec00d007ec00d007
    0.306  RX H10→Pi ATT Exchange MTU Rsp e800
    0.306  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.502  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.502  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    0.697  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    0.697  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    0.941  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    0.941  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.038  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.038  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0128
    1.184  RX H10→Pi ATT Error Rsp 对 Read By Group Type Req 句柄 0x0001 错误 0x0a
    1.184  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0228
    1.282  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.282  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff0328
    1.381  RX H10→Pi ATT Read By Type Rsp 070200020300002a0400020500012a0600020700042a0800020900a62a0b00200c00052a0f00101000372a1200021300382a1500021600292a1700021800242a1900021a00252a1b00021c00272a1d00021e00262a1f00022000282a2100022200232a2400122500192a
    1.381  TX Pi→H10 ATT Read By Type Req【请求】 2500ffff0328
    1.527  RX H10→Pi ATT Read By Type Rsp 1528000229002d8e7086d93a8013fbb1ecc84cff17622a00242b00f3a1a8bdd37c2a7ed091bb914dff17622e002a2f00c8f08d2dcd8aad1c87f3e702815c00fb3100103200c8f08d2dcd8aad1c87f3e702825c00fb35001c3600c8f08d2dcd8aad1c87f3e702515c00fb3800103900c8f08d2dcd8aad1c87f3e702525c00fb3b000c3c00c8f08d2dcd8aad1c87f3e702535c00fb
    1.527  TX Pi→H10 ATT Read By Type Req【请求】 3c00ffff0328
    1.623  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x003c 错误 0x0a
    1.623  TX Pi→H10 ATT Find Info Req【请求】 3d00ffff
    1.769  RX H10→Pi ATT Error Rsp 对 Find Info Req 句柄 0x003d 错误 0x0a
    1.772  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.866  RX H10→Pi ATT Write Rsp 
    1.866  TX Pi→H10 ATT Read Req【请求】 0300
    1.964  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.965  TX Pi→H10 ATT Read Req【请求】 0500
    2.061  RX H10→Pi SMP Security Req 09
    2.061  TX Pi→H10 SMP Pairing Req 010009100d0f
    2.062  RX H10→Pi ATT Read Rsp 4103
    2.062  TX Pi→H10 ATT Read Req【请求】 2500
    2.208  RX H10→Pi SMP Pairing Rsp 030009100103
    2.305  RX H10→Pi ATT Read Rsp 64
    2.308  TX Pi→H10 SMP Pairing Public Key 89f510be9a4300fafa77b43c333f360f067fd30012a80e36d42012c715e9e17f99cbb16a96919efacc45df61caf42238b49164efc5f1f2380435989fa9a31b7e
    2.308  TX Pi→H10 ATT Read Req【请求】 2f00
    2.502  RX H10→Pi SMP Pairing Public Key fdbcfe958b00e1e06b43f7bd04328b6f920bd86bfd36eab29012e8f402c687e8f40d063f0e6b00b51aeec60409ba6801ca0c903a3a88f4923c1e66887a389e97
    2.502  RX H10→Pi SMP Pairing Confirm fe598aca6937b3bdebd42264b4ad83d3
    2.502  TX Pi→H10 SMP Pairing Random ee0c87169f15536efd5c849622c4cd09
    2.503  RX H10→Pi ATT Error Rsp 对 Read Req 句柄 0x002f 错误 0x05
    2.744  RX H10→Pi SMP Pairing Random 4e9195102c62a9463fa484c84deee0d3
    2.744  TX Pi→H10 SMP DHKey Check ccbf8b401feb52654294b7ec3f3f2633
    2.841  RX H10→Pi SMP DHKey Check 99e3d5e133516bfff0acadfe67700a43
    2.841  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    2.842  EVT Command Status 0x2019 LE Start Encryption 状态 00
    3.329  EVT Encryption Change 00400001
    3.329  CMD 0x0c7c  4000b80b
    3.329  TX Pi→H10 ATT Read Req【请求】 2f00
    3.329  EVT Command Complete 0x0c7c  状态 00
    3.426  RX H10→Pi SMP Identity Info ac0b2efde582b3253f1808d526020e1f
    3.524  RX H10→Pi SMP Identity Addr Info 00d4cc11acac24
    3.622  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    3.622  TX Pi→H10 ATT Write Req【请求】 26000100
    3.865  RX H10→Pi ATT Write Rsp 
    3.865  TX Pi→H10 ATT Write Req【请求】 30000200
    3.962  RX H10→Pi ATT Write Rsp 
    3.964  TX Pi→H10 ATT Write Req【请求】 33000100
    4.060  RX H10→Pi ATT Write Rsp 
    4.061  TX Pi→H10 ATT Write Req【请求】 11000100
    4.206  RX H10→Pi ATT Write Rsp 
    4.207  TX Pi→H10 ATT Write Req【请求】 2f000100
    4.304  RX H10→Pi ATT Write Rsp 
    4.305  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    4.305  TX Pi→H10 ATT Confirm 
    4.306  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    4.450  RX H10→Pi ATT Write Rsp 
    4.547  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    4.548  TX Pi→H10 ATT Confirm 
    4.549  TX Pi→H10 ATT Write Req【请求】 2f000102
    4.549  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    4.549  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    4.549  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    4.550  EVT Command Status 0x2013 LE Conn Update 状态 00
    4.646  RX H10→Pi ATT Write Rsp 
    4.694  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    4.694  TX Pi→H10 ATT Confirm 
    4.696  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    4.840  RX H10→Pi ATT Write Rsp 
    4.841  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    4.841  TX Pi→H10 ATT Confirm 
    5.164  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 1 个）
    5.164  EVT LE Conn Update Complete 004000270000005802
    8.989  CMD 0x2005  588775d08a0a
    8.989  EVT Command Complete 0x2005  状态 00
    8.989  CMD 0x200b  01120012000100
    8.989  EVT Command Complete 0x200b  状态 00
   14.345  CMD 0x0401  338b9e0400
   14.346  EVT Command Status 0x0401  状态 00
   19.469  EVT 0x01 00
   19.989  CMD 0x2005  63b5a5e10e27
   19.989  EVT Command Complete 0x2005  状态 00
   19.989  CMD 0x200b  01120012000100
   19.989  EVT Command Complete 0x200b  状态 00
   24.844  TX Pi→H10 ATT Write Req【请求】 2f000300
   25.002  RX H10→Pi ATT Write Rsp 
   25.002  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   25.003  TX Pi→H10 ATT Confirm 
   25.004  TX Pi→H10 ATT Write Req【请求】 2f000302
   25.351  RX H10→Pi ATT Write Rsp 
   25.354  CMD 0x0401  338b9e0400
   25.354  EVT Command Status 0x0401  状态 00
   25.441  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   25.441  TX Pi→H10 ATT Confirm 
   27.989  CMD 0x0406 Disconnect 400013
   27.990  EVT Command Status 0x0406 Disconnect 状态 00
   30.477  EVT 0x01 00
   33.972  EVT Disconnection Complete 00400022
```

## H10原始日志/g5_r1.btsnoop

HR 通知 24、PMD 数据包 0、首个 PMD 在 t=None

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.013  CMD 0x2016 LE Read Remote Features 4000
    0.013  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.131  EVT LE Read Remote Features 0040002500000000000000
    0.131  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    0.132  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.326  EVT LE Data Length Change 4000ec00d007ec00d007
    0.668  EVT Encryption Change 00400001
    0.668  CMD 0x0c7c  4000b80b
    0.668  EVT Command Complete 0x0c7c  状态 00
    0.668  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.814  RX H10→Pi ATT Exchange MTU Rsp e800
    0.814  TX Pi→H10 ATT Read Req【请求】 2500
    0.911  RX H10→Pi ATT Read Rsp 64
    0.911  TX Pi→H10 ATT Read Req【请求】 0300
    1.058  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.058  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.155  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.155  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.302  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.302  TX Pi→H10 ATT Write Req【请求】 26000100
    1.399  RX H10→Pi ATT Write Rsp 
    1.399  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.497  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.497  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.594  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.619  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.691  RX H10→Pi ATT Write Rsp 
    1.691  TX Pi→H10 ATT Read Req【请求】 2f00
    1.790  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.792  TX Pi→H10 ATT Write Req【请求】 30000200
    1.886  RX H10→Pi ATT Write Rsp 
    1.887  TX Pi→H10 ATT Write Req【请求】 33000100
    1.984  RX H10→Pi ATT Write Rsp 
    1.984  TX Pi→H10 ATT Write Req【请求】 11000100
    2.130  RX H10→Pi ATT Write Rsp 
    2.131  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.227  RX H10→Pi ATT Write Rsp 
    2.228  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.228  TX Pi→H10 ATT Confirm 
    2.229  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.374  RX H10→Pi ATT Write Rsp 
    2.374  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.374  TX Pi→H10 ATT Confirm 
    2.375  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.375  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.375  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.375  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.375  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.521  RX H10→Pi ATT Write Rsp 
    2.522  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.522  TX Pi→H10 ATT Confirm 
    2.523  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.617  RX H10→Pi ATT Write Rsp 
    2.618  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.618  TX Pi→H10 ATT Confirm 
    2.749  EVT LE Conn Update Complete 004000270000005802
   22.622  TX Pi→H10 ATT Write Req【请求】 2f000300
   22.735  RX H10→Pi ATT Write Rsp 
   22.736  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   22.736  TX Pi→H10 ATT Confirm 
   22.737  TX Pi→H10 ATT Write Req【请求】 2f000302
   22.833  RX H10→Pi ATT Write Rsp 
   22.833  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   22.833  TX Pi→H10 ATT Confirm 
   24.726  CMD 0x0406 Disconnect 400013
   24.726  EVT Command Status 0x0406 Disconnect 状态 00
   24.734  EVT Disconnection Complete 00400016
```

## H10原始日志/g5_r2.btsnoop

HR 通知 24、PMD 数据包 0、首个 PMD 在 t=None

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.020  CMD 0x2016 LE Read Remote Features 4000
    0.020  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.126  EVT LE Read Remote Features 0040002500000000000000
    0.126  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    0.126  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.272  EVT LE Data Length Change 4000ec00d007ec00d007
    0.565  EVT Encryption Change 00400001
    0.565  CMD 0x0c7c  4000b80b
    0.565  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.565  EVT Command Complete 0x0c7c  状态 00
    0.662  RX H10→Pi ATT Exchange MTU Rsp e800
    0.662  TX Pi→H10 ATT Read Req【请求】 2500
    0.808  RX H10→Pi ATT Read Rsp 64
    0.808  TX Pi→H10 ATT Read Req【请求】 0300
    0.906  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.906  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.052  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.052  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.150  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.150  TX Pi→H10 ATT Write Req【请求】 26000100
    1.296  RX H10→Pi ATT Write Rsp 
    1.296  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.394  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.394  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.491  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.519  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.588  RX H10→Pi ATT Write Rsp 
    1.588  TX Pi→H10 ATT Read Req【请求】 2f00
    1.686  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.687  TX Pi→H10 ATT Write Req【请求】 30000200
    1.783  RX H10→Pi ATT Write Rsp 
    1.784  TX Pi→H10 ATT Write Req【请求】 33000100
    1.881  RX H10→Pi ATT Write Rsp 
    1.881  TX Pi→H10 ATT Write Req【请求】 11000100
    1.978  RX H10→Pi ATT Write Rsp 
    1.979  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.076  RX H10→Pi ATT Write Rsp 
    2.076  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.076  TX Pi→H10 ATT Confirm 
    2.077  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.173  RX H10→Pi ATT Write Rsp 
    2.174  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.174  TX Pi→H10 ATT Confirm 
    2.174  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.174  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.174  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.174  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.175  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.466  RX H10→Pi ATT Write Rsp 
    2.467  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.467  TX Pi→H10 ATT Confirm 
    2.468  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.563  RX H10→Pi ATT Write Rsp 
    2.564  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.564  TX Pi→H10 ATT Confirm 
    2.624  EVT LE Conn Update Complete 004000270000005802
   22.567  TX Pi→H10 ATT Write Req【请求】 2f000300
   22.660  RX H10→Pi ATT Write Rsp 
   22.660  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   22.660  TX Pi→H10 ATT Confirm 
   22.661  TX Pi→H10 ATT Write Req【请求】 2f000302
   22.757  RX H10→Pi ATT Write Rsp 
   22.758  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   22.758  TX Pi→H10 ATT Confirm 
   24.805  CMD 0x0406 Disconnect 400013
   24.805  EVT Command Status 0x0406 Disconnect 状态 00
   24.855  EVT Disconnection Complete 00400016
```

## H10原始日志/g5_r3.btsnoop

HR 通知 24、PMD 数据包 0、首个 PMD 在 t=None

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.025  CMD 0x2016 LE Read Remote Features 4000
    0.025  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.106  EVT LE Read Remote Features 0040002500000000000000
    0.106  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    0.107  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.253  EVT LE Data Length Change 4000ec00d007ec00d007
    0.691  EVT Encryption Change 00400001
    0.691  CMD 0x0c7c  4000b80b
    0.692  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.692  EVT Command Complete 0x0c7c  状态 00
    0.789  RX H10→Pi ATT Exchange MTU Rsp e800
    0.789  TX Pi→H10 ATT Read Req【请求】 2500
    0.935  RX H10→Pi ATT Read Rsp 64
    0.935  TX Pi→H10 ATT Read Req【请求】 0300
    1.033  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.033  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.179  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.179  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.277  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.277  TX Pi→H10 ATT Write Req【请求】 26000100
    1.422  RX H10→Pi ATT Write Rsp 
    1.423  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.521  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.521  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.618  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.637  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.715  RX H10→Pi ATT Write Rsp 
    1.715  TX Pi→H10 ATT Read Req【请求】 2f00
    1.813  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.814  TX Pi→H10 ATT Write Req【请求】 30000200
    1.910  RX H10→Pi ATT Write Rsp 
    1.911  TX Pi→H10 ATT Write Req【请求】 33000100
    2.007  RX H10→Pi ATT Write Rsp 
    2.008  TX Pi→H10 ATT Write Req【请求】 11000100
    2.105  RX H10→Pi ATT Write Rsp 
    2.106  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.202  RX H10→Pi ATT Write Rsp 
    2.203  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.203  TX Pi→H10 ATT Confirm 
    2.204  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.300  RX H10→Pi ATT Write Rsp 
    2.301  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.301  TX Pi→H10 ATT Confirm 
    2.301  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.301  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.301  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.301  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.302  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.495  RX H10→Pi ATT Write Rsp 
    2.496  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.496  TX Pi→H10 ATT Confirm 
    2.497  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.592  RX H10→Pi ATT Write Rsp 
    2.593  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.593  TX Pi→H10 ATT Confirm 
    2.825  EVT LE Conn Update Complete 004000270000005802
   22.596  TX Pi→H10 ATT Write Req【请求】 2f000300
   22.666  RX H10→Pi ATT Write Rsp 
   22.666  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   22.667  TX Pi→H10 ATT Confirm 
   22.667  TX Pi→H10 ATT Write Req【请求】 2f000302
   22.763  RX H10→Pi ATT Write Rsp 
   22.764  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   22.764  TX Pi→H10 ATT Confirm 
   25.218  CMD 0x0406 Disconnect 400013
   25.219  EVT Command Status 0x0406 Disconnect 状态 00
   25.250  EVT Disconnection Complete 00400016
```

## H10原始日志/s1_300s.btsnoop

HR 通知 305、PMD 数据包 2027、首个 PMD 在 t=32.654334

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.020  CMD 0x2016 LE Read Remote Features 4000
    0.020  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.130  EVT LE Read Remote Features 0040002500000000000000
    0.130  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    0.131  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.276  EVT LE Data Length Change 4000ec00d007ec00d007
    0.569  EVT Encryption Change 00400001
    0.569  CMD 0x0c7c  4000b80b
    0.569  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.569  EVT Command Complete 0x0c7c  状态 00
    0.666  RX H10→Pi ATT Exchange MTU Rsp e800
    0.667  TX Pi→H10 ATT Read Req【请求】 2500
    0.764  RX H10→Pi ATT Read Rsp 64
    0.764  TX Pi→H10 ATT Read Req【请求】 0300
    0.862  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.862  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.959  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.959  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.057  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.057  TX Pi→H10 ATT Write Req【请求】 26000100
    1.203  RX H10→Pi ATT Write Rsp 
    1.203  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.349  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.350  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.544  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.589  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.641  RX H10→Pi ATT Write Rsp 
    1.641  TX Pi→H10 ATT Read Req【请求】 2f00
    1.788  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.789  TX Pi→H10 ATT Write Req【请求】 30000200
    1.885  RX H10→Pi ATT Write Rsp 
    1.886  TX Pi→H10 ATT Write Req【请求】 33000100
    2.031  RX H10→Pi ATT Write Rsp 
    2.032  TX Pi→H10 ATT Write Req【请求】 11000100
    2.129  RX H10→Pi ATT Write Rsp 
    2.129  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.275  RX H10→Pi ATT Write Rsp 
    2.276  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.276  TX Pi→H10 ATT Confirm 
    2.276  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.373  RX H10→Pi ATT Write Rsp 
    2.373  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.373  TX Pi→H10 ATT Confirm 
    2.374  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.374  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.374  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.374  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.385  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.616  RX H10→Pi ATT Write Rsp 
    2.618  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.618  TX Pi→H10 ATT Confirm 
    2.618  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.714  RX H10→Pi ATT Write Rsp 
    2.714  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.714  TX Pi→H10 ATT Confirm 
    2.768  EVT LE Conn Update Complete 004000270000005802
   32.654  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 32 个）
  302.743  TX Pi→H10 ATT Write Req【请求】 2f000300
  302.795  RX H10→Pi ATT Write Rsp 
  302.796  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
  302.796  TX Pi→H10 ATT Confirm 
  302.797  TX Pi→H10 ATT Write Req【请求】 2f000302
  302.893  RX H10→Pi ATT Write Rsp 
  302.893  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
  302.893  TX Pi→H10 ATT Confirm 
  305.441  CMD 0x0406 Disconnect 400013
  305.442  EVT Command Status 0x0406 Disconnect 状态 00
  305.476  EVT Disconnection Complete 00400016
```

## H10原始日志/lat1_r1.btsnoop

HR 通知 65、PMD 数据包 227、首个 PMD 在 t=32.79355

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.031  CMD 0x2016 LE Read Remote Features 4000
    0.031  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.175  EVT LE Read Remote Features 0040002500000000000000
    0.175  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    0.175  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.370  EVT LE Data Length Change 4000ec00d007ec00d007
    0.760  EVT Encryption Change 00400001
    0.760  CMD 0x0c7c  4000b80b
    0.760  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.760  EVT Command Complete 0x0c7c  状态 00
    0.857  RX H10→Pi ATT Exchange MTU Rsp e800
    0.857  TX Pi→H10 ATT Read Req【请求】 2500
    0.954  RX H10→Pi ATT Read Rsp 64
    0.955  TX Pi→H10 ATT Read Req【请求】 0300
    1.053  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    1.053  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.150  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.150  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.248  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.248  TX Pi→H10 ATT Write Req【请求】 26000100
    1.345  RX H10→Pi ATT Write Rsp 
    1.345  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.443  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.443  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.540  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.570  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.686  RX H10→Pi ATT Write Rsp 
    1.686  TX Pi→H10 ATT Read Req【请求】 2f00
    1.784  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.785  TX Pi→H10 ATT Write Req【请求】 30000200
    1.930  RX H10→Pi ATT Write Rsp 
    1.930  TX Pi→H10 ATT Write Req【请求】 33000100
    2.125  RX H10→Pi ATT Write Rsp 
    2.125  TX Pi→H10 ATT Write Req【请求】 11000100
    2.222  RX H10→Pi ATT Write Rsp 
    2.223  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.368  RX H10→Pi ATT Write Rsp 
    2.369  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.369  TX Pi→H10 ATT Confirm 
    2.370  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.466  RX H10→Pi ATT Write Rsp 
    2.515  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.515  TX Pi→H10 ATT Confirm 
    2.515  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.515  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.515  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.516  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.527  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.807  RX H10→Pi ATT Write Rsp 
    2.808  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.808  TX Pi→H10 ATT Confirm 
    2.809  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.905  RX H10→Pi ATT Write Rsp 
    2.905  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.905  TX Pi→H10 ATT Confirm 
    3.100  EVT LE Conn Update Complete 004000270000005802
   32.794  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 33 个）
   62.913  TX Pi→H10 ATT Write Req【请求】 2f000300
   62.968  RX H10→Pi ATT Write Rsp 
   62.969  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   62.969  TX Pi→H10 ATT Confirm 
   62.970  TX Pi→H10 ATT Write Req【请求】 2f000302
   63.066  RX H10→Pi ATT Write Rsp 
   63.066  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   63.067  TX Pi→H10 ATT Confirm 
   65.461  CMD 0x0406 Disconnect 400013
   65.461  EVT Command Status 0x0406 Disconnect 状态 00
   65.504  EVT Disconnection Complete 00400016
```

## H10原始日志/lat1_r2.btsnoop

HR 通知 81、PMD 数据包 226、首个 PMD 在 t=32.392636

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.016  CMD 0x2016 LE Read Remote Features 4000
    0.016  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.144  EVT LE Read Remote Features 0040002500000000000000
    0.144  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    0.144  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.290  EVT LE Data Length Change 4000ec00d007ec00d007
    0.583  EVT Encryption Change 00400001
    0.583  CMD 0x0c7c  4000b80b
    0.583  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.583  EVT Command Complete 0x0c7c  状态 00
    0.680  RX H10→Pi ATT Exchange MTU Rsp e800
    0.680  TX Pi→H10 ATT Read Req【请求】 2500
    0.778  RX H10→Pi ATT Read Rsp 64
    0.778  TX Pi→H10 ATT Read Req【请求】 0300
    0.876  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.876  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.973  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.973  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.071  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.071  TX Pi→H10 ATT Write Req【请求】 26000100
    1.167  RX H10→Pi ATT Write Rsp 
    1.168  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.266  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.266  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.363  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.386  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.460  RX H10→Pi ATT Write Rsp 
    1.460  TX Pi→H10 ATT Read Req【请求】 2f00
    1.558  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.559  TX Pi→H10 ATT Write Req【请求】 30000200
    1.655  RX H10→Pi ATT Write Rsp 
    1.656  TX Pi→H10 ATT Write Req【请求】 33000100
    1.752  RX H10→Pi ATT Write Rsp 
    1.753  TX Pi→H10 ATT Write Req【请求】 11000100
    1.850  RX H10→Pi ATT Write Rsp 
    1.851  TX Pi→H10 ATT Write Req【请求】 2f000100
    1.947  RX H10→Pi ATT Write Rsp 
    1.948  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    1.948  TX Pi→H10 ATT Confirm 
    1.949  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.045  RX H10→Pi ATT Write Rsp 
    2.045  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.046  TX Pi→H10 ATT Confirm 
    2.046  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.046  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.046  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.046  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.047  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.192  RX H10→Pi ATT Write Rsp 
    2.193  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.193  TX Pi→H10 ATT Confirm 
    2.194  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.289  RX H10→Pi ATT Write Rsp 
    2.289  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.289  TX Pi→H10 ATT Confirm 
    2.410  EVT LE Conn Update Complete 004000270000005802
   32.393  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 32 个）
   62.297  TX Pi→H10 ATT Write Req【请求】 2f000300
   62.418  RX H10→Pi ATT Write Rsp 
   62.419  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   62.419  TX Pi→H10 ATT Confirm 
   62.420  TX Pi→H10 ATT Write Req【请求】 2f000302
   62.565  RX H10→Pi ATT Write Rsp 
   62.565  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   62.565  TX Pi→H10 ATT Confirm 
   64.861  CMD 0x0406 Disconnect 400013
   64.861  EVT Command Status 0x0406 Disconnect 状态 00
   64.905  EVT Disconnection Complete 00400016
  101.557  CMD 0x2005  baa7910c1b17
  101.558  EVT Command Complete 0x2005  状态 00
  101.558  CMD 0x200b  01120012000100
  101.558  EVT Command Complete 0x200b  状态 00
  101.770  CMD 0x2005  a99b9204223e
  101.771  EVT Command Complete 0x2005  状态 00
  101.771  CMD 0x200b  01120012000100
  101.771  EVT Command Complete 0x200b  状态 00
  103.001  CMD 0x200b  00600060000000
  103.001  EVT Command Complete 0x200b  状态 00
  103.484  CMD 0x200d LE Create Connection 600060000000d4cc11acac2400100028000000580200000000
  103.485  EVT Command Status 0x200d LE Create Connection 状态 00
  103.985  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
  104.012  CMD 0x2016 LE Read Remote Features 4000
  104.012  EVT Command Status 0x2016 LE Read Remote Features 状态 00
  104.107  EVT LE Read Remote Features 0040002500000000000000
  104.107  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
  104.108  EVT Command Status 0x2019 LE Start Encryption 状态 00
  104.254  EVT LE Data Length Change 4000ec00d007ec00d007
  104.546  EVT Encryption Change 00400001
  104.546  CMD 0x0c7c  4000b80b
  104.546  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
  104.547  EVT Command Complete 0x0c7c  状态 00
  104.644  RX H10→Pi ATT Exchange MTU Rsp e800
  104.644  TX Pi→H10 ATT Read Req【请求】 2500
  104.790  RX H10→Pi ATT Read Rsp 64
  104.790  TX Pi→H10 ATT Read Req【请求】 0300
  104.887  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
  104.887  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
  104.985  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
  104.985  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
  105.083  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
  105.083  TX Pi→H10 ATT Write Req【请求】 26000100
  105.180  RX H10→Pi ATT Write Rsp 
  105.180  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
  105.278  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
  105.278  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
  105.375  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
  105.400  TX Pi→H10 ATT Write Req【请求】 0d000200
  105.472  RX H10→Pi ATT Write Rsp 
  105.472  TX Pi→H10 ATT Read Req【请求】 2f00
  105.570  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
  105.571  TX Pi→H10 ATT Write Req【请求】 30000200
  105.667  RX H10→Pi ATT Write Rsp 
  105.668  TX Pi→H10 ATT Write Req【请求】 33000100
  105.765  RX H10→Pi ATT Write Rsp 
  105.765  TX Pi→H10 ATT Write Req【请求】 11000100
  105.862  RX H10→Pi ATT Write Rsp 
  105.863  TX Pi→H10 ATT Write Req【请求】 2f000100
  106.008  RX H10→Pi ATT Write Rsp 
  106.009  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
  106.009  TX Pi→H10 ATT Confirm 
  106.010  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
  106.155  RX H10→Pi ATT Write Rsp 
  106.155  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
  106.155  TX Pi→H10 ATT Confirm 
  106.156  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
  106.156  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
  106.156  CMD 0x2013 LE Conn Update 4000100028000000580200000000
  106.157  EVT Command Status 0x2013 LE Conn Update 状态 00
  106.169  TX Pi→H10 ATT Write Req【请求】 2f000102
  106.398  RX H10→Pi ATT Write Rsp 
  106.400  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
  106.400  TX Pi→H10 ATT Confirm 
  106.400  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
  106.513  EVT LE Conn Update Complete 004000270000005802
  106.610  RX H10→Pi ATT Write Rsp 
  106.610  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
  106.610  TX Pi→H10 ATT Confirm 
```

## H10原始日志/lat1_r3.btsnoop

HR 通知 64、PMD 数据包 227、首个 PMD 在 t=32.558425

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.027  CMD 0x2016 LE Read Remote Features 4000
    0.028  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.123  EVT LE Read Remote Features 0040002500000000000000
    0.123  CMD 0x2019 LE Start Encryption 400000000000000000000000fb4e87d2deb0e2ad300c56d4e4a29dbd
    0.123  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.269  EVT LE Data Length Change 4000ec00d007ec00d007
    0.561  EVT Encryption Change 00400001
    0.561  CMD 0x0c7c  4000b80b
    0.562  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.562  EVT Command Complete 0x0c7c  状态 00
    0.659  RX H10→Pi ATT Exchange MTU Rsp e800
    0.659  TX Pi→H10 ATT Read Req【请求】 2500
    0.805  RX H10→Pi ATT Read Rsp 64
    0.805  TX Pi→H10 ATT Read Req【请求】 0300
    0.903  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.903  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.000  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.000  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.098  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.098  TX Pi→H10 ATT Write Req【请求】 26000100
    1.195  RX H10→Pi ATT Write Rsp 
    1.195  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.293  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.293  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.390  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.415  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.487  RX H10→Pi ATT Write Rsp 
    1.488  TX Pi→H10 ATT Read Req【请求】 2f00
    1.586  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.587  TX Pi→H10 ATT Write Req【请求】 30000200
    1.682  RX H10→Pi ATT Write Rsp 
    1.683  TX Pi→H10 ATT Write Req【请求】 33000100
    1.780  RX H10→Pi ATT Write Rsp 
    1.781  TX Pi→H10 ATT Write Req【请求】 11000100
    1.877  RX H10→Pi ATT Write Rsp 
    1.878  TX Pi→H10 ATT Write Req【请求】 2f000100
    2.024  RX H10→Pi ATT Write Rsp 
    2.024  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
    2.024  TX Pi→H10 ATT Confirm 
    2.025  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
    2.170  RX H10→Pi ATT Write Rsp 
    2.170  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
    2.171  TX Pi→H10 ATT Confirm 
    2.171  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
    2.171  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
    2.171  CMD 0x2013 LE Conn Update 4000100028000000580200000000
    2.172  EVT Command Status 0x2013 LE Conn Update 状态 00
    2.184  TX Pi→H10 ATT Write Req【请求】 2f000102
    2.414  RX H10→Pi ATT Write Rsp 
    2.415  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
    2.415  TX Pi→H10 ATT Confirm 
    2.416  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
    2.528  EVT LE Conn Update Complete 004000270000005802
    2.625  RX H10→Pi ATT Write Rsp 
    2.625  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
    2.626  TX Pi→H10 ATT Confirm 
   32.558  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 32 个）
   62.634  TX Pi→H10 ATT Write Req【请求】 2f000300
   62.684  RX H10→Pi ATT Write Rsp 
   62.685  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   62.685  TX Pi→H10 ATT Confirm 
   62.686  TX Pi→H10 ATT Write Req【请求】 2f000302
   62.779  RX H10→Pi ATT Write Rsp 
   62.779  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   62.779  TX Pi→H10 ATT Confirm 
   64.876  CMD 0x0406 Disconnect 400013
   64.876  EVT Command Status 0x0406 Disconnect 状态 00
   64.924  EVT Disconnection Complete 00400016
```
