# my-clash-sub 自动更新版

这是一个“免费公开节点聚合 + 自动更新”的 Clash/Mihomo 项目。

## 固定订阅地址

上传到 `herryli340-tech/my-clash-sub` 的 `main` 分支后：

`https://raw.githubusercontent.com/herryli340-tech/my-clash-sub/main/clash.yaml`

Clash Verge Rev / Mihomo 直接添加这个地址即可。

## 自动更新

GitHub Actions 每天北京时间 08:17 和 20:17 自动运行，也可以在 Actions 页面手动运行。

流程：
1. 抓取多个公开 Clash YAML
2. 解析并去重
3. 清理非法节点
4. 最多保留 60 个节点
5. 生成 `clash.yaml`
6. GitHub Actions 自动提交更新

## 自动选最快

配置里已经内置：
- 🚀 自动选择：url-test，每 5 分钟测速
- 🔄 故障转移：fallback
- 🎯 手动选择

注意：免费公开节点稳定性不可保证。节点源可能随时失效，因此这个项目的目标是“自动换新”，不是保证长期稳定。
