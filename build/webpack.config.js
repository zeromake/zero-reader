const webpack = require('webpack');
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
// const ExtractTextPlugin = require("extract-text-webpack-plugin")
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const HardSourceWebpackPlugin = require('hard-source-webpack-plugin');

const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
// const CssNano = require('cssnano')
// const AutoDllPlugin = require("autodll-webpack-plugin");

const pkg = require("../package.json");

const isProd = process.env.NODE_ENV === 'production';
// console.log(process.env.platform)
const isCordova = process.env.platform === "cordova";
const resolve = file => path.resolve(__dirname, file);
const assetsPath = "assets";
const isWebpackNext = true

function buildCss(use) {
    if (isWebpackNext && isProd) {
        return [
            MiniCssExtractPlugin.loader,
            ...use
        ]
    }
    return [
        {
            loader: "style-loader"
        },
        ...use
    ]
}

const fullZero = function(date, funName) {
    let res = date[funName]()
    if ('getMonth' === funName) {
        res += 1
    }
    if (res < 10) {
        res = '0' + res
    }
    return res
};

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

const serverIp = '0.0.0.0'
const serverPort = 8090

const outPath = isCordova ? resolve('../www') : resolve('../dist');
const zreactAlias = {
    'react': 'zreact',
    'react-dom': 'zreact',
    'prop-types': 'zreact/prop-types.js',
    'preact': 'zreact',
    'module-react': resolve('../src/import/module-zreact.ts'),
    'react-import': resolve('../src/import/zreact-import.ts'),
    'preact-animate': 'preact-animate/dist/zreact-animate-esm.js',
    // 'zreact-router': 'zreact-router/dist/zreact-router-esm.js',
}
const reactAlias = {
    'zreact/devtools': resolve('../src/import/devtools.ts'),
    'zreact': resolve('../src/import/module-react.ts'),
    'preact': resolve('../src/import/module-react.ts'),
    'module-react': resolve('../src/import/module-react.ts'),
    'react-import': resolve('../src/import/react-import.ts'),
    'preact-animate': 'preact-animate/dist/react-animate-esm.js',
    'zreact-router': 'zreact-router/dist/react-router-esm.js',
}

const sZreactAlias = {
    'react': '@zeromake/zreact',
    'react-dom': '@zeromake/zreact',
    'zreact': '@zeromake/zreact',
    'zreact/devtools': '@zeromake/zreact/lib/devtools.js', 
    'preact': resolve('../src/import/module-szreact.ts'),
    'module-react': resolve('../src/import/module-szreact.ts'),
    'react-import': resolve('../src/import/react-import.ts'),
    'preact-animate': 'preact-animate/dist/react-animate-esm.js',
    'zreact-router': 'zreact-router/dist/react-router-esm.js',
}
const preactAlias = {
    'react': 'preact',
    'react-dom': 'preact',
    'zreact': 'preact',
    'zreact/devtools': resolve('../src/import/devtools.ts'),
    'module-react': resolve('../src/import/module-preact.ts'),
    'react-import': resolve('../src/import/preact-import.ts'),
    'zreact-router': 'zreact-router/dist/preact-router-esm.js',
}

const basePlugin = [
    new HardSourceWebpackPlugin(),
    new webpack.DefinePlugin({
        'process.env': {
            NODE_ENV: isProd ? '"production"' : '"development"',
            platform: JSON.stringify(process.env.platform)
        }
    })
]
if (isProd) {
    basePlugin.push(new MiniCssExtractPlugin({
        filename: "css/common.[chunkhash].css",
    }))
}
if (!isWebpackNext) {
    const ModuleConcatenationPlugin = require('webpack/lib/optimize/ModuleConcatenationPlugin');
    basePlugin.push(new ModuleConcatenationPlugin())
    if (isProd) {
        basePlugin.push(new webpack.optimize.UglifyJsPlugin({
            // 最紧凑的输出
            beautify: false,
            // 删除所有的注释
            comments: false,
            mangle: {
                safari10: true
            },
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
        }));
    }
}

// if (isProd) {
//     const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
//     basePlugin.push(
//         new BundleAnalyzerPlugin({
//             analyzerPort: 9999
//         })
//     )
// }
        

const config = {
    devtool: isProd ? false : "#source-map",
    entry: {
        "main": resolve('../src/main.tsx')
    },
    output: {
        path: path.join(outPath, assetsPath),
        publicPath: isProd ? (isCordova ? '' : '/') + assetsPath : (isCordova ? '' : '/'),
        filename: '[name]-[hash].js'
    },
    resolve: {
        // 只采用 main 字段作为入口文件描述字段，以减少搜索步骤
        mainFields: ['jsnext:main', 'module', 'main'],
        // 只使用当前项目下的node_modules
        modules: [path.resolve(__dirname, '../node_modules')],
        alias: Object.assign({
            'zreact/devtools': isProd || isCordova ? resolve('../src/import/devtools.ts') : 'zreact/devtools',
            'router-history': isCordova ? resolve('../src/import/hash-history.ts') : resolve('../src/import/history.ts'),
            // 'sweetalert2': 'sweetalert2/dist/sweetalert2.js',
            '~': resolve('../src')
        }, sZreactAlias),
        extensions: ['.js', '.ts', '.tsx']
    },
    plugins: [
        new HtmlWebpackPlugin({
            config: isProd && !isCordova ? "{{ config|safe }}" : isProd && isCordova ? false : "<script type=\"text/javascript\">\n    window.projectConfig=" + JSON.stringify({
                "sign_up": true,
                "sign_up_code": true
            }) + "\n    </script>",
            version: pkg.version,
            buildTime: strftime(new Date()),
            isProd,
            isCordova,
            filename: ((assetsPath === "" || !isProd) ? "" : "../") +'index.html',
            template: 'src/index.ejs',
            minify: isProd ? {
                collapseWhitespace: true
            }: false,
            inject: true
        }),
        // new AutoDllPlugin({
        //     inject: true, // will inject the DLL bundles to index.html
        //     filename: '[name]_[hash].js',
        //     plugins: basePlugin,
        //     entry: {
        //         vendor: [
        //             'zreact',
        //             'es6-promise',
        //             'hotkeys-js',
        //             'intersection-observer',
        //             'lodash.throttle',
        //             'preact-animate',
        //             'screenfull',
        //             'unfetch'
        //         ]
        //     }
        // }),
    ].concat(basePlugin),
    devServer: {
        contentBase: outPath,
        host: serverIp,
        port: serverPort,
        inline: true,
        // hot: true,
        historyApiFallback: true,
        proxy: {
            "/api": "http://127.0.0.1:8000"
        }
    },
    optimization: {
        minimizer: [
            new UglifyJsPlugin({
                cache: true,
                parallel: true,
                sourceMap: true,
                uglifyOptions: {
                    // 最紧凑的输出
                    beautify: false,
                    // 删除所有的注释
                    comments: false,
                    mangle: {
                        safari10: true
                    },
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
                }
            }),
            new OptimizeCSSAssetsPlugin({
                // cssProcessor: CssNano,
                cssProcessorOptions: { discardComments: { removeAll: true } },
            })
        ],
        runtimeChunk: {
            name: "manifest"
        },
        splitChunks: {
            cacheGroups: {
                styles: {
                    name: 'styles',
                    test: /\.(css|styl)$/,
                    chunks: 'all',
                    enforce: true
                },
                vendors: {
                    test: /[\\/]node_modules[\\/].+\.js$/,
                    chunks: "all",
                    name: "vendor"
                }
            }
        },
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
                use: buildCss([
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
                ])
            },
            {
                test: /.scss$/,
                use: buildCss([
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
                        loader: 'sass-loader',
                        options: {
                            sourceMap: !isProd
                        }
                    }
                ])
            },
            {
                test: /.less$/,
                use: buildCss([
                    {
                        loader: "css-loader",
                        options: {
                            sourceMap: !isProd,
                            modules: false,
                        }
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            sourceMap: !isProd
                        }
                    },
                    {
                        loader: 'less-loader',
                        options: {
                            sourceMap: !isProd
                        }
                    }
                ])
            },
            {
                test: /\.css$/,
                use: buildCss([
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
                ])
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
// if (isProd) {
//     config.plugins.push(
//         new webpack.optimize.UglifyJsPlugin({
//             // 最紧凑的输出
//             beautify: false,
//             // 删除所有的注释
//             comments: false,
//             compress: {
//                 // 在UglifyJs删除没有用到的代码时不输出警告
//                 warnings: false,
//                 // 删除所有的 `console` 语句，可以兼容ie浏览器
//                 drop_console: true,
//                 // 内嵌定义了但是只用到一次的变量
//                 collapse_vars: true,
//                 // 提取出出现多次但是没有定义成变量去引用的静态值
//                 reduce_vars: true,
//                 // warnings: false,
//             }
//         })
//     )
// }
module.exports = config;
