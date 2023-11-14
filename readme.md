# clash2sing-box

配置转换

# usage

从yaml文件，或者url中获取节点，与模板合并，生成singbox配置。

```bash
$ python ./clash2singbox.py 
usage: clash2singbox.py [-h] [-f FILE] [-u URL] [-o OUTPUT]

options:
  -h, --help                    show this help message and exit
  -f FILE, --file FILE          订阅文件
  -u URL, --url URL             订阅地址
  -o OUTPUT, --output OUTPUT    输出文件
```

使用
```python clash2singbox.py --url https://domain/subscibe?token=abc```

可以在模板outputs/template.json中设置额外的选项，outputs目录下的所有*.json文件都会参与配置合并。比如rule1.json,custom_outbound.json.