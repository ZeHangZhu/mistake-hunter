
<div align="center">
  <img src="doc/img/icon512px.png" width="128"/>
</div>

<div align="center">
    <h1>错题猎手</h1>
</div>

---

这是我的比赛项目,使用Django框架,数据库使用SQLite3,前端使用Bootstrap;我们的电子错题本包含传统电子错题本不包含的特性:
1. 支持使用AI助手,识别错题中的公式并生成相似题目,还可以和AI对话,并记录对话历史。
2. AI生成题目,可以根据用户的需求,调整难度和类型;题目灵活,不易重复。
3. 积分系统,用户可以通过完成错题,获得积分,并可以在积分系统中查看自己的积分。
4. 支持用户上传错题图片,并自动识别错题中的公式。
5. 电脑端移动端同步,B/S架构,用户可以在电脑端和移动端之间同步数据。

## 启动服务器
### 1.配置pip镜像源(可选)
配置pip清华镜像源
```bash
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```
#### 其他国内镜像源

- 清华大学TUNA镜像源： `https://pypi.tuna.tsinghua.edu.cn/simple`
- 阿里云镜像源： `http://mirrors.aliyun.com/pypi/simple/`
- 中国科学技术大学镜像源： `https://mirrors.ustc.edu.cn/pypi/simple/`
- 华为云镜像源： `https://repo.huaweicloud.com/repository/pypi/simple/`
- 腾讯云镜像源：`https://mirrors.cloud.tencent.com/pypi/simple/`

### 2. 配置虚拟环境
使用Python 3.3及以上版本内置的`venv`模块
Windows:
```bash
cd mistake-hunter
python -m venv .venv
```
Linux:
```bash
cd mistake-hunter
python3 -m venv .venv
```

### 3.使用启动脚本启动服务器
首次启动,应使用`-r`安装依赖库和运行数据库迁移,随后服务器会自动启动
```bash
script\run -r
```


## 文档
|文档|
|---|
|[错题猎手 - 文档文件夹](./doc)|
|[错题猎手 - 开发手册(后端API文档)](./doc/index.html)|
|[错题猎手 - 部署与初始化文档](./doc/project.md)|
|[错题猎手 - 配置文件文档](./doc/config.md)|
|[Mathjax - 开放源代码许可](./doc/Mathjax/LICENSE)|
|[Mathjax - README.MD](./doc/Mathjax/README.md)|
|[Bootstrap - 开放源代码许可](./doc/Bootstrap/LICENSE)|
|[Bootstrap - README.MD](./doc/Bootstrap/README.md)|

## 免责声明

1. 本项目为开源学习作品，仅供教育及科研交流使用。  
2. 平台所展示的 AI 生成内容（含题目、解析、对话记录等）均由算法自动生成，未经人工逐一校验，可能存在错误、偏差或不适之处，请用户自行甄别并谨慎使用。  
3. 用户上传的图片、文本等资料仅用于错题识别与个性化学习，我们不会主动分享或泄露给第三方，但请确保上传内容不包含侵犯他人版权、隐私或其他合法权益的信息；若有违规，后果由上传者自行承担。  
4. 积分为系统内部激励数值，不具备任何现实货币价值，不可兑换现金或其他有形资产，平台有权根据运营需求调整积分规则。  
5. 使用本服务即视为您已阅读并同意本声明；若因使用本系统而产生的任何直接或间接损失，开发团队及平台方不承担法律责任。  
6. 若您未满 18 周岁，请在监护人陪同下使用本系统。  
7. 本声明最终解释权归“错题猎手”项目团队所有，并保留随时更新条款的权利，更新后的条款自公布之日起生效。