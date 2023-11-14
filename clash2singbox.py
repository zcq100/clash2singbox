import os
import json
import sys
import base64
import argparse
import urllib.request

try:
    import yaml
except ImportError:
    os.system("pip install pyyaml")
    import yaml

output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)


def decode_if_base64(s: str):
    try:
        return base64.b64decode(s).decode()
    except Exception:
        return s


def load_subscribe(filename: str = None, url: str = None):
    data = None
    if filename:
        with open(filename, "r", encoding="utf-8") as fp:
            data = fp.read()
    elif url:
        with urllib.request.urlopen(url) as resp:
            print(f"[+] fetch {url} success.")
            data = resp.read().decode("utf-8")
    try:
        data = decode_if_base64(data)
        if data.startswith("ss"):
            # TODO
            raise NotImplementedError("protrol type unsupport now.")
        obj = yaml.load(data, Loader=yaml.FullLoader)
        return obj
    except yaml.YAMLError as err:
        print(err)
        sys.exit(1)


def shadowsocks(node: dict):
    info = {
        "tag": node.get("name"),
        "type": "shadowsocks",
        "server": node.get("server"),
        "server_port": node.get("port"),
        "method": node.get("cipher"),
        "password": node.get("password"),
    }
    # if node.get("udp"):
    #     info["network"] = "udp"
    return info


# TODO
def torjan(node: dict):
    ...


def parse(data):
    servers = {"outbounds": []}

    select = {
        "tag": "select",
        "type": "selector",
        "default": "urltest",
        "outbounds": ["urltest"],
    }
    urltest = {"tag": "urltest", "type": "urltest", "outbounds": []}
    global_ = {"tag": "GLOBAL", "type": "selector", "outbounds": ["select"]}

    for node in data["proxies"]:
        if node["type"] == "ss":
            sb_node = shadowsocks(node)
            servers["outbounds"].append(sb_node)
            urltest["outbounds"].append(sb_node.get("tag"))

    select["outbounds"].extend(urltest["outbounds"])
    global_["outbounds"].extend(urltest["outbounds"])

    servers["outbounds"].insert(0, select)
    servers["outbounds"].insert(1, urltest)
    return servers


def write(data: dict, filename="output.json"):
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4, sort_keys=True)


def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            merged[key].extend(value)
        elif (
            key in merged and isinstance(merged[key], dict) and isinstance(value, dict)
        ):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def merge_file(data: dict):
    for f in os.listdir(output_dir):
        if f.endswith(".json"):
            with open(os.path.join(output_dir, f), "r", encoding="utf-8") as fp:
                _j = json.load(fp)
                data = merge_dicts(data, _j)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="订阅文件")
    parser.add_argument("-u", "--url", help="订阅地址")
    parser.add_argument("-o", "--output", default="config.json", help="输出文件")
    args = parser.parse_args()
    if not args.file and not args.url:
        parser.print_help()
        sys.exit(1)

    # 加载订阅
    if args.file:
        subsribe = load_subscribe(filename=args.file)
    elif args.url:
        subsribe = load_subscribe(url=args.url)
    else:
        subsribe = load_subscribe("clash.yaml")

    # 解析节点
    outbounds = parse(subsribe)
    # 生成配置
    config = merge_file(outbounds)
    # 写入配置
    write(config, args.output)
    print("[+] sucess.")
