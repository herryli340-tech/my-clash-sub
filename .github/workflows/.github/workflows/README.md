# Clash/Mihomo 免费节点自动聚合器

每天自动抓取多个公开 Clash/Mihomo 订阅，合并、去重，并生成一个固定的 `dist/clash.yaml`。

## 已加入的公开源

- Au1rxx/free-vpn-subscriptions：公开源，Clash YAML，每小时刷新
- zhuhaiuk/free-nodes：公开源，Clash/Mihomo YAML，每小时刷新
- share-daily/node：公开节点，每日更新

这些公开节点的可用性和安全性无法保证，请不要通过免费节点传输敏感信息。

## 部署

1. 新建一个 GitHub 仓库，例如 `my-clash-sub`.
2. 把本项目所有文件上传到仓库。
3. Settings → Actions → General → Workflow permissions → Read and write permissions。
4. Actions → Update Clash Nodes → Run workflow。
5. 成功后，Clash/Mihomo 使用：

   `https://raw.githubusercontent.com/你的用户名/你的仓库/main/dist/clash.yaml`

6. GitHub Actions 会每天自动更新。

## 重要

GitHub Actions 的定时任务不是严格准点执行，可能有延迟。

## 筛选

当前版本做：
- 多源合并
- YAML 订阅解析
- Base64/VMess 基础解析
- 去重
- 删除缺少 server/port 的节点
- 节点数量上限 120
- URL-Test 自动测速
- ChatGPT / Google / YouTube 独立策略组
- 中国大陆 GEOIP 直连

如果你的 Clash 客户端是 Clash Meta/Mihomo，优先使用这个 YAML。
