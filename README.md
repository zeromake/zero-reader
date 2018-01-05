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
+ [ ] 更多的全按键操作支持
    - [ ] 书库按键支持
    - [ ] 目录dialog按键支持
+ [ ] 书库及筛选
    - [ ] 书名模糊搜索
    - [ ] 作者及译者模糊搜索
    - [ ] tag精确选择过滤
+ [ ] 书架
    - [ ] 分类
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

## use open project
1. [preact](https://github.com/developit/preact): mini react like library
2. [zreact](https://github.com/zeromake/zreact): copy preact
3. [preact-animate](https://github.com/zeromake/preact-animate): fork by rc-animate
4. [animate.css](https://github.com/daneden/animate.css): css animate
5. [preact-router](https://github.com/developit/preact-router): preact router copy to src/assets/router add animate, react support
6. [better-scroll](https://github.com/ustbhuangyi/better-scroll): mobile scroll
7. [history](https://github.com/ReactTraining/history): hash router support
8. [lozad](https://github.com/ApoorvSaxena/lozad.js): img lazy
9. [cordova](http://cordova.apache.org/): android and ios package
---
1. [lxml](https://github.com/lxml/lxml): xml tools
2. [requests](https://github.com/requests/requests): http client request
3. [argparse](https://github.com/ThomasWaldmann/argparse/): cmd parse
4. [pypdf2](https://github.com/mstamy2/PyPDF2): read pdf meta
5. [sanic](https://github.com/channelcat/sanic): aio http server
6. [aiosqlite3](https://github.com/zeromake/aiosqlite3): aio sqlite support
7. [sqlalchemy](https://github.com/zzzeek/sqlalchemy): database orm
8. [pdf2htmlEX](https://github.com/coolwanglu/pdf2htmlEX): pdf to html

## develop use tools

1. webpack + webpack-dev-server: make package
2. svg-sprite-loader: import svg icon
3. webpack-bundle-analyzer: module rely
4. stylus: css pre processor
5. typescript: script pre processor
