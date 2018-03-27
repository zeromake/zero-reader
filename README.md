# zero-reader
web reader

## Todo
- [x] pdf转换html(使用pdf2htmlEX)
- [x] pdf转换后的脚本处理
- [x] epub转换到html，json
- [x] preact-animate轮子
+ [x] preact-router改造轮子(src/assets/router)
    - [x] 动画切换支持
    - [x] 子路由支持
- [x] peract的pdf前端阅读器
- [x] epub前端阅读器
- [x] 按键支持翻页
- [x] epub改造为翻页滚动
- [x] react，react-dom支持
- [x] 阅读器内部链接跳转
- [x] 阅读器外部链接新标签打开
+ [ ] 用户认证
    - [x] 登陆注册
    - [ ] 邮箱验证
    - [ ] 找回秘密
    - [ ] 社交账号绑定
+ [ ] 更多的全按键操作支持
    - [ ] 书库按键支持
    - [ ] 目录dialog按键支持
+ [ ] model api化
    - [x] model create api化
    - [x] model delete api化
    - [x] model update api化
    - [x] model get api化
    - [x] model post api化
    - [x] model delete api化
    - [ ] model put api化
    - [x] model to openapi-ui
+ [ ] 书库及筛选
    - [ ] 书名模糊搜索
    - [ ] 作者及译者模糊搜索
    - [ ] tag精确选择过滤
+ [ ] 书架
    - [ ] 分类
    - [ ] 自动根据最近阅读排序
+ [ ] 阅读器设置
    - [ ] epub字体大小
    - [ ] epub字体间距
    - [ ] epub分列数
    - [ ] pdf滚动模式设置切换(原生/better-scroll)
    - [ ] pdf缩放设置
    - [ ] 背景色设置
    - [ ] 同步设置
+ [ ] 阅读记录
    - [ ] 离线阅读记录
    - [ ] 阅读记录同步
    - [ ] 阅读记录冲突选择
+ [ ] 上传书籍
    - [ ] 进度显示
    - [ ] opf文件支持
    - [ ] 豆瓣号支持
    - [ ] 豆瓣书名搜索支持
+ [ ] 更多书籍格式支持
    - [ ] mobi 支持
    - [ ] gitbook 支持
+ [ ] 安装引导
    - [ ] 服务设置
    - [ ] 数据库设置
    - [ ] 管理员设置
    - [ ] 升级引导
+ [ ] 管理员后台
    - [ ] 邀请码管理
    - [ ] 用户管理
    - [ ] 书籍管理
    - [ ] 仪表盘
        - [ ] 系统占用图表
        - [ ] 用户增长图表
        - [ ] 书籍增长图表
    - [ ] 导入数据
    - [ ] 备份数据

## use open project
1. [preact](https://github.com/developit/preact): mini react like library(MIT)
2. [zreact](https://github.com/zeromake/zreact): copy preact(MIT)
3. [preact-animate](https://github.com/zeromake/preact-animate): fork by rc-animate(MIT)
4. [animate.css](https://github.com/daneden/animate.css): css animate(MIT)
5. [preact-router](https://github.com/developit/preact-router): preact router copy to src/assets/router add animate, react support(MIT)
6. [better-scroll](https://github.com/ustbhuangyi/better-scroll): mobile scroll(MIT)
7. [history](https://github.com/ReactTraining/history): hash router support(MIT)
8. [lozad](https://github.com/ApoorvSaxena/lozad.js): img lazy(MIT)
9. [cordova](http://cordova.apache.org/): android and ios package(Apache2.0)
---
1. [lxml](https://github.com/lxml/lxml): xml tools(BSD)
2. [requests](https://github.com/requests/requests): http client request(Apache2.0)
3. [argparse](https://github.com/ThomasWaldmann/argparse/): cmd parse(Python-License)
4. [pypdf2](https://github.com/mstamy2/PyPDF2): read pdf meta
5. [sanic](https://github.com/channelcat/sanic): aio http server(MIT)
6. [aiosqlite3](https://github.com/zeromake/aiosqlite3): aio sqlite support(MIT)
7. [sqlalchemy](https://github.com/zzzeek/sqlalchemy): database orm(MIT)
8. [pdf2htmlEX](https://github.com/coolwanglu/pdf2htmlEX): pdf to html(GPLv3)

## develop use tools

1. webpack + webpack-dev-server: make package
2. svg-sprite-loader: import svg icon
3. webpack-bundle-analyzer: module rely
4. stylus: css pre processor
5. typescript: script pre processor

## webpack4.0 support
- [x] extract-text-webpack-plugin v4.0.0-beta.0
- [x] html-webpack-plugin v3.1.0
- [x] hard-source-webpack-plugin v0.6.4
- [x] svg-sprite-loader v3.6.3
