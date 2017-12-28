const webpack = require('webpack')
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const ExtractTextPlugin = require("extract-text-webpack-plugin")
const ModuleConcatenationPlugin = require('webpack/lib/optimize/ModuleConcatenationPlugin');

const pkg = require("../package.json")

const isProd = process.env.NODE_ENV === 'production'
const isCordova = process.env.platform === "cordova"
const resolve = file => path.resolve(__dirname, file)

const fullZero= function(date, funName) {
    let res = date[funName]()
    if ('getMonth' === funName) {
        res += 1
    }
    if (res < 10) {
        res = '0' + res
    }
    return res
}

const strftime = function(date) {
    let offset = date.getTimezoneOffset() / 60
    let join = ''
    if (offset > 0) {
        join = '-'
    } else {
        join = '+'
        offset = -(offset)
    }
    if (offset < 10) {
        offset = '0' + offset
    }
    let date_str = [
        [
            fullZero(date, 'getFullYear'),
            fullZero(date, 'getMonth'),
            fullZero(date, 'getDate')
        ].join('-'),
        [
            fullZero(date, 'getHours'),
            fullZero(date, 'getMinutes'),
            fullZero(date, 'getSeconds')
        ].join(':')
    ].join(' ')
    if (offset !== '00') {
        date_str += join + offset + ':00'
    }
    return date_str
}

const serverIp = '127.0.0.1'
const serverPort = 8089

const outPath = isCordova ? resolve('../www') : resolve('../dist');
const zreactAlias = {
    'preact': 'zreact',
    'module-react': resolve('../src/import/module-zreact.ts'),
    'react-import': resolve('../src/import/zreact-import.ts'),
}
const reactAlias = {
    'zreact': resolve('../src/import/module-react.ts'),
    'preact': resolve('../src/import/module-react.ts'),
    'module-react': resolve('../src/import/module-react.ts'),
    'react-import': resolve('../src/import/react-import.ts'),
    'preact-animate': 'preact-animate/dist/react-animate',
}
const preactAlias = {
    'zreact': 'preact',
    'module-react': resolve('../src/import/module-preact.ts'),
    'react-import': resolve('../src/import/preact-import.ts'),
}
const config = {
    devtool: isProd ? false : "#source-map",
    entry: {
        "main": resolve('../src/main.tsx')
    },
    output: {
        path: outPath,
        publicPath: isCordova ? '' : '/',
        filename: '[name]-[hash].js'
    },
    resolve: {
        mainFields: ['jsnext:main', 'main'],
        // 只使用当前项目下的node_modules
        modules: [path.resolve(__dirname, '../node_modules')],
        // 只采用 main 字段作为入口文件描述字段，以减少搜索步骤
        alias: Object.assign({
            'zreact/devtools': isProd ? resolve('../src/import/devtools.ts') : 'zreact/devtools',
            'history/createHashHistory': resolve(isCordova ? '../src/import/hash-history.ts': '../src/import/history.ts'),
            '@': resolve('../src')
        }, reactAlias),
        extensions: ['.js', '.ts', '.tsx']
    },
    plugins: [
        new ModuleConcatenationPlugin(),
        new HtmlWebpackPlugin({
            version: pkg.version,
            buildTime: strftime(new Date()),
            isProd,
            filename: 'index.html',
            template: 'src/index.ejs',
            inject: true
        }),
        new ExtractTextPlugin("css/common.[chunkhash].css"),
        // new webpack.HotModuleReplacementPlugin(),
        // new es3ifyPlugin()
    ],
    devServer: {
        contentBase: outPath,
        host: serverIp,
        port: serverPort,
        inline: true,
        // hot: true,
        historyApiFallback: true
    },
    module: {
        rules: [
            {
                test: /\.svg$/,
                include: resolve('../src/assets/icons'),
                use: {
                    loader: 'svg-sprite-loader',
                    options: {
                        symbolId: 'icon-[name]'
                    }
                }
            },
            {

                test: /\.tsx?$/,
                use: 'ts-loader',
            },
            {
                test: /.styl$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: [
                        {
                            loader: "css-loader",
                            options: {
                                sourceMap: !isProd,
                                modules: true,
                            }
                        },
                        {
                            loader: 'postcss-loader',
                            options: {
                                sourceMap: !isProd
                            }
                        },
                        {
                            loader: 'stylus-loader',
                            options: {
                                sourceMap: !isProd
                            }
                        }
                    ],
                    publicPath: '../'
                })
            },
            {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: [
                        {
                            loader: "css-loader",
                            options: {
                                sourceMap: !isProd,
                            }
                        },
                        {
                            loader: 'postcss-loader',
                            options: {
                                sourceMap: !isProd
                            }
                        }
                    ],
                    publicPath: '../'
                })
            },
            {
                test: /\.(png|jpe?g|gif)(\?.*)?$/,
                use: {
                    loader: 'url-loader',
                    options: {
                        limit: 10000,
                        name: 'img/[name].[hash:7].[ext]'
                    }
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf|svg)(\?.*)?$/,
                exclude: resolve('../src/assets/icons'),
                use: {
                    loader: 'url-loader',
                    options: {
                        limit: 10000,
                        name: 'fonts/[name].[hash:7].[ext]'
                    }
                }
            }
        ]
    }
}
if (isProd) {
    config.plugins.push(
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"production"',
                platform: JSON.stringify(process.env.platform)
            }
        })
    )
    config.plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            // 最紧凑的输出
            beautify: false,
            // 删除所有的注释
            comments: false,
            compress: {
                // 在UglifyJs删除没有用到的代码时不输出警告
                warnings: false,
                // 删除所有的 `console` 语句，可以兼容ie浏览器
                drop_console: true,
                // 内嵌定义了但是只用到一次的变量
                collapse_vars: true,
                // 提取出出现多次但是没有定义成变量去引用的静态值
                reduce_vars: true,
                // warnings: false,
            }
        })
    )
    // const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
    // config.plugins.push(
    //     new BundleAnalyzerPlugin({
    //         analyzerPort: 9999
    //     })
    // )
} else {
    config.plugins.push(
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"dev"',
                platform: JSON.stringify(process.env.platform)
            }
        })
    )
}
module.exports = config;