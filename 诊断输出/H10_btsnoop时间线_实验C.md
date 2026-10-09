# btsnoop 时间线（省略 HR/PMD 数据通知与续传分片；t=0 为首个 Connection Complete）

## H10原始日志/rootC_r1.btsnoop

HR 通知 88、PMD 数据包 258、首个 PMD 在 t=52.501161

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.016  CMD 0x2016 LE Read Remote Features 4000
    0.017  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.136  EVT LE Read Remote Features 0040002500000000000000
    0.136  CMD 0x2019 LE Start Encryption 400000000000000000000000df373d780fae0b5ff71f2d9d2da90b5e
    0.137  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.283  EVT LE Data Length Change 4000ec00d007ec00d007
    0.575  EVT Encryption Change 00400001
    0.575  CMD 0x0c7c  4000b80b
    0.575  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.576  EVT Command Complete 0x0c7c  状态 00
    0.721  RX H10→Pi ATT Exchange MTU Rsp e800
    0.721  TX Pi→H10 ATT Read Req【请求】 0300
    0.819  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.819  TX Pi→H10 ATT Read Req【请求】 2500
    0.916  RX H10→Pi ATT Read Rsp 64
    0.916  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.014  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.014  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.112  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.112  TX Pi→H10 ATT Write Req【请求】 26000100
    1.209  RX H10→Pi ATT Write Rsp 
    1.209  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.307  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.307  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.404  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.429  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.501  RX H10→Pi ATT Write Rsp 
    1.501  TX Pi→H10 ATT Read Req【请求】 2f00
    1.599  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.600  TX Pi→H10 ATT Write Req【请求】 30000200
    1.696  RX H10→Pi ATT Write Rsp 
    1.697  TX Pi→H10 ATT Write Req【请求】 33000100
    1.793  RX H10→Pi ATT Write Rsp 
    1.794  TX Pi→H10 ATT Write Req【请求】 11000100
    1.891  RX H10→Pi ATT Write Rsp 
   21.893  TX Pi→H10 ATT Write Req【请求】 2f000100
   21.972  RX H10→Pi ATT Write Rsp 
   21.973  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   21.973  TX Pi→H10 ATT Confirm 
   21.974  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   22.118  RX H10→Pi ATT Write Rsp 
   22.119  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   22.119  TX Pi→H10 ATT Confirm 
   22.120  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
   22.120  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
   22.120  CMD 0x2013 LE Conn Update 4000100028000000580200000000
   22.120  EVT Command Status 0x2013 LE Conn Update 状态 00
   22.130  TX Pi→H10 ATT Write Req【请求】 2f000102
   22.473  RX H10→Pi ATT Write Rsp 
   22.474  EVT LE Conn Update Complete 004000270000005802
   22.523  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   22.523  TX Pi→H10 ATT Confirm 
   22.524  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   22.620  RX H10→Pi ATT Write Rsp 
   22.620  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   22.620  TX Pi→H10 ATT Confirm 
   52.501  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 52 个）
   86.711  TX Pi→H10 ATT Write Req【请求】 2f000300
   86.763  RX H10→Pi ATT Write Rsp 
   86.763  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   86.763  TX Pi→H10 ATT Confirm 
   86.764  TX Pi→H10 ATT Write Req【请求】 2f000302
   86.860  RX H10→Pi ATT Write Rsp 
   86.861  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   86.861  TX Pi→H10 ATT Confirm 
   88.978  CMD 0x0406 Disconnect 400013
   88.978  EVT Command Status 0x0406 Disconnect 状态 00
   89.005  EVT Disconnection Complete 00400016
```

## H10原始日志/rootC_r2.btsnoop

HR 通知 85、PMD 数据包 227、首个 PMD 在 t=52.343552

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.016  CMD 0x2016 LE Read Remote Features 4000
    0.016  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.167  EVT LE Read Remote Features 0040002500000000000000
    0.167  CMD 0x2019 LE Start Encryption 400000000000000000000000df373d780fae0b5ff71f2d9d2da90b5e
    0.167  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.313  EVT LE Data Length Change 4000ec00d007ec00d007
    0.703  EVT Encryption Change 00400001
    0.703  CMD 0x0c7c  4000b80b
    0.703  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.704  EVT Command Complete 0x0c7c  状态 00
    0.801  RX H10→Pi ATT Exchange MTU Rsp e800
    0.801  TX Pi→H10 ATT Read Req【请求】 0300
    0.899  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.899  TX Pi→H10 ATT Read Req【请求】 2500
    0.995  RX H10→Pi ATT Read Rsp 64
    0.996  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    1.093  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    1.093  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.191  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.191  TX Pi→H10 ATT Write Req【请求】 26000100
    1.288  RX H10→Pi ATT Write Rsp 
    1.288  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.387  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.387  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.483  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.506  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.580  RX H10→Pi ATT Write Rsp 
    1.580  TX Pi→H10 ATT Read Req【请求】 2f00
    1.678  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.680  TX Pi→H10 ATT Write Req【请求】 30000200
    1.775  RX H10→Pi ATT Write Rsp 
    1.776  TX Pi→H10 ATT Write Req【请求】 33000100
    1.873  RX H10→Pi ATT Write Rsp 
    1.873  TX Pi→H10 ATT Write Req【请求】 11000100
    1.970  RX H10→Pi ATT Write Rsp 
   21.974  TX Pi→H10 ATT Write Req【请求】 2f000100
   22.051  RX H10→Pi ATT Write Rsp 
   22.052  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   22.052  TX Pi→H10 ATT Confirm 
   22.053  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   22.149  RX H10→Pi ATT Write Rsp 
   22.150  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   22.150  TX Pi→H10 ATT Confirm 
   22.150  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
   22.150  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
   22.150  CMD 0x2013 LE Conn Update 4000100028000000580200000000
   22.151  EVT Command Status 0x2013 LE Conn Update 状态 00
   22.162  TX Pi→H10 ATT Write Req【请求】 2f000102
   22.344  RX H10→Pi ATT Write Rsp 
   22.345  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   22.345  TX Pi→H10 ATT Confirm 
   22.346  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   22.441  RX H10→Pi ATT Write Rsp 
   22.442  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   22.442  TX Pi→H10 ATT Confirm 
   22.512  EVT LE Conn Update Complete 004000270000005802
   52.344  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 52 个）
   82.448  TX Pi→H10 ATT Write Req【请求】 2f000300
   82.511  RX H10→Pi ATT Write Rsp 
   82.512  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   82.512  TX Pi→H10 ATT Confirm 
   82.513  TX Pi→H10 ATT Write Req【请求】 2f000302
   82.658  RX H10→Pi ATT Write Rsp 
   82.658  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   82.658  TX Pi→H10 ATT Confirm 
   85.196  CMD 0x0406 Disconnect 400013
   85.197  EVT Command Status 0x0406 Disconnect 状态 00
   85.241  EVT Disconnection Complete 00400016
```

## H10原始日志/rootC_r3.btsnoop

HR 通知 85、PMD 数据包 226、首个 PMD 在 t=52.525394

```
    0.000  EVT LE Connection Complete 0040000000d4cc11acac2427000000580200
    0.024  CMD 0x2016 LE Read Remote Features 4000
    0.024  EVT Command Status 0x2016 LE Read Remote Features 状态 00
    0.139  EVT LE Read Remote Features 0040002500000000000000
    0.139  CMD 0x2019 LE Start Encryption 400000000000000000000000df373d780fae0b5ff71f2d9d2da90b5e
    0.139  EVT Command Status 0x2019 LE Start Encryption 状态 00
    0.285  EVT LE Data Length Change 4000ec00d007ec00d007
    0.578  EVT Encryption Change 00400001
    0.578  CMD 0x0c7c  4000b80b
    0.578  TX Pi→H10 ATT Exchange MTU Req【请求】 0502
    0.578  EVT Command Complete 0x0c7c  状态 00
    0.675  RX H10→Pi ATT Exchange MTU Rsp e800
    0.675  TX Pi→H10 ATT Read Req【请求】 0300
    0.773  RX H10→Pi ATT Read Rsp 506f6c617220483130203131434344343338
    0.773  TX Pi→H10 ATT Read Req【请求】 2500
    0.870  RX H10→Pi ATT Read Rsp 64
    0.870  TX Pi→H10 ATT Read By Type Req【请求】 0100ffff3a2b
    0.967  RX H10→Pi ATT Error Rsp 对 Read By Type Req 句柄 0x0001 错误 0x0a
    0.967  TX Pi→H10 ATT Read By Group Type Req【请求】 0100ffff0028
    1.066  RX H10→Pi ATT Read By Group Type Rsp 060100090000180a000d0001180e0013000d18140022000a18230026000f18
    1.066  TX Pi→H10 ATT Write Req【请求】 26000100
    1.162  RX H10→Pi ATT Write Rsp 
    1.162  TX Pi→H10 ATT Read By Group Type Req【请求】 2700ffff0028
    1.309  RX H10→Pi ATT Read By Group Type Rsp 1427002c00f3ecd74555a45aad401131fb4bff17622d003300c8f08d2dcd8aad1c87f3e702805c00fb
    1.309  TX Pi→H10 ATT Read By Group Type Req【请求】 3400ffff0028
    1.455  RX H10→Pi ATT Read By Group Type Rsp 063400ffffeefe
    1.478  TX Pi→H10 ATT Write Req【请求】 0d000200
    1.552  RX H10→Pi ATT Write Rsp 
    1.552  TX Pi→H10 ATT Read Req【请求】 2f00
    1.699  RX H10→Pi ATT Read Rsp 0f05000000000000000000000000000000
    1.700  TX Pi→H10 ATT Write Req【请求】 30000200
    1.796  RX H10→Pi ATT Write Rsp 
    1.797  TX Pi→H10 ATT Write Req【请求】 33000100
    1.942  RX H10→Pi ATT Write Rsp 
    1.943  TX Pi→H10 ATT Write Req【请求】 11000100
    2.040  RX H10→Pi ATT Write Rsp 
   22.043  TX Pi→H10 ATT Write Req【请求】 2f000100
   22.121  RX H10→Pi ATT Write Rsp 
   22.122  RX H10→Pi ATT Indicate 句柄 0x002f f0010000000001820001010e00
   22.122  TX Pi→H10 ATT Confirm 
   22.123  TX Pi→H10 ATT Write Req【请求】 2f0002000001820001010e00
   22.316  RX H10→Pi ATT Write Rsp 
   22.316  RX H10→Pi ATT Indicate 句柄 0x002f f00200000000
   22.317  TX Pi→H10 ATT Confirm 
   22.317  RX H10→Pi L2CAP 信令 code 0x12 0308001000280000005802
   22.317  TX Pi→H10 L2CAP 信令 code 0x13 0302000000
   22.317  CMD 0x2013 LE Conn Update 4000100028000000580200000000
   22.318  EVT Command Status 0x2013 LE Conn Update 状态 00
   22.330  TX Pi→H10 ATT Write Req【请求】 2f000102
   22.511  RX H10→Pi ATT Write Rsp 
   22.512  RX H10→Pi ATT Indicate 句柄 0x002f f0010200000004190032006400c800010110000203020004000800
   22.512  TX Pi→H10 ATT Confirm 
   22.513  TX Pi→H10 ATT Write Req【请求】 2f0002020001c8000101100002010800
   22.608  RX H10→Pi ATT Write Rsp 
   22.609  RX H10→Pi ATT Indicate 句柄 0x002f f00202000001
   22.609  TX Pi→H10 ATT Confirm 
   22.694  EVT LE Conn Update Complete 004000270000005802
   52.525  **首个 PMD 数据包** RX H10→Pi PMD 数据 类型 02 L2CAP 长 229（此前 HR 通知 52 个）
   82.616  TX Pi→H10 ATT Write Req【请求】 2f000300
   82.693  RX H10→Pi ATT Write Rsp 
   82.694  RX H10→Pi ATT Indicate 句柄 0x002f f003000000
   82.694  TX Pi→H10 ATT Confirm 
   82.695  TX Pi→H10 ATT Write Req【请求】 2f000302
   82.791  RX H10→Pi ATT Write Rsp 
   82.791  RX H10→Pi ATT Indicate 句柄 0x002f f003020000
   82.791  TX Pi→H10 ATT Confirm 
   85.269  CMD 0x0406 Disconnect 400013
   85.269  EVT Command Status 0x0406 Disconnect 状态 00
   85.277  EVT Disconnection Complete 00400016
```
