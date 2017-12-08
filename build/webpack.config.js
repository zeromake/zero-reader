const webpack = require('webpack')
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const ExtractTextPlugin = require("extract-text-webpack-plugin")
const es3ifyPlugin = require('es3ify-webpack-plugin');
const pkg = require("../package.json")

const isProd = process.env.NODE_ENV === 'production'
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

const outPath = resolve('../dist');
const config = {
    devtool: isProd ? false : "#source-map",
    entry: {
        "main": resolve('../src/main.tsx')
    },
    output: {
        path: outPath,
        publicPath: '/',
        filename: '[name]-[hash].js'
    },
    resolve: {
        alias: {
            // 'zreact': resolve('../node_modules/zreact/dist/zreact.esm.js'),
            'preact': 'zreact',
            'react-import': resolve('../src/import/zreact-import.ts'),
            '@': resolve('../src')
        },
        extensions: ['.js', '.ts', '.tsx']
    },
    plugins: [
        new HtmlWebpackPlugin({
            version: pkg.version,
            buildTime: strftime(new Date()),
            isProd,
            filename: 'index.html',
            template: 'src/index.ejs',
            inject: true
        }),
        new ExtractTextPlugin("css/common.[chunkhash].css"),
        // new es3ifyPlugin()
    ],
    devServer: {
        contentBase: outPath,
        host: '0.0.0.0',
        port: 8089,
        inline: true,
        historyApiFallback: true
    },
    module: {
        rules: [
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
                                sourceMap: true,
                                modules: !isProd,
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
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                use: {
                    loader: 'url-loader',
                    options: {
                        limit: 10000,
                        name: 'img/[name].[hash:7].[ext]'
                    }
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
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
                NODE_ENV: '"production"'
            }
        })
    )
    config.plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false
            }
        })
    )
    // const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
    // config.plugins.push(
    //     new BundleAnalyzerPlugin({
    //         analyzerPort: 9999
    //     })
    // )
}
module.exports = config;