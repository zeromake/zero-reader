const webpack = require('webpack')
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const ExtractTextPlugin = require("extract-text-webpack-plugin")

const isProd = process.env.NODE_ENV === 'production'
const resolve = file => path.resolve(__dirname, file)

const outPath = resolve('../dist');
module.exports = {
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
            'preact': resolve('../node_modules/zreact/dist/zreact.esm.js'),
            '@': resolve('../src')
        },
        extensions: ['.js', '.ts', '.tsx']
    },
    plugins: [
        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'src/index.html',
            inject: true
        }),
        new ExtractTextPlugin("css/common.[chunkhash].css")
    ],
    devServer: {
        contentBase: outPath,
        host: '127.0.0.1',
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
                // use: [
                //     {
                //         loader: 'style-loader'
                //     },
                //     {
                //         loader: 'css-loader',
                //         options: {
                //             modules: true
                //         }
                //     },
                //     {
                //         loader: 'stylus-loader'
                //     }
                // ]
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
            }
        ]
    }
}