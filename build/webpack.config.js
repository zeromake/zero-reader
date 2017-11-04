const webpack = require('webpack')
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const ExtractTextPlugin = require("extract-text-webpack-plugin")

const isProd = process.env.NODE_ENV === 'production'
const resolve = file => path.resolve(__dirname, file)

const outPath = resolve('../dist');
const config = {
    devtool: isProd ? false : "#source-map",
    entry: {
        "main": resolve('../src/main.tsx')
    },
    output: {
        path: outPath,
        publicPath: "/",
        filename: '[name]-[hash].js'
    },
    resolve: {
        alias: {
            'zreact': resolve('../node_modules/zreact/dist/zreact.ie8.js'),
            'preact': 'zreact',
            '@': resolve('../src')
        },
        extensions: ['.js', '.ts', '.tsx']
    },
    plugins: [
        new HtmlWebpackPlugin({
            isProd,
            filename: 'index.html',
            template: 'src/index.ejs',
            inject: true
        }),
        new ExtractTextPlugin("css/common.[chunkhash].css")
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
                    use: ["css-loader?modules", 'stylus-loader']
                })
            },
            {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: ["css-loader"]
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