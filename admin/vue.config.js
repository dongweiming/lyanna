const debug = process.env.NODE_ENV !== 'production'

module.exports = {
    indexPath: 'admin.html',
    productionSourceMap: false,
    configureWebpack: (config) => {
        if (debug) {
            config.devtool = 'eval-source-map'
        } else {
            config.devtool = false
        }
        config.output.filename = 'static/js/admin/[name].js'
        config.output.chunkFilename = 'static/js/admin/[name].js'
        config.externals = {
            'vue': 'Vue',
            'element-ui': 'ELEMENT'
        }
        config.optimization = {
            splitChunks: false
        }
    },
    css: {
        extract: {
            filename: 'static/css/admin/[name].css',
            chunkFilename: 'static/css/admin/[name].css'
        }
    },
    chainWebpack: config => {
        config.resolve.alias
            .set('#', resolve('../common/src'))

        config.module
            .rule('svg')
            .exclude.add(resolve('src/icons'))
            .end()

        config.module
            .rule('icons')
            .test(/\.svg$/)
            .include.add(resolve('src/icons'))
            .end()
            .use('svg-sprite-loader')
            .loader('svg-sprite-loader')
            .options({
                symbolId: 'icon-[name]'
            })
    },
    devServer: {
        proxy: {
            ...['/auth', '/api', '/static'].reduce(
                (acc, ctx) => ({
                    ...acc,
                    [ctx]: { target: 'http://127.0.0.1:8000',
                             changeOrigin: true },
                }),
                {}
            ),
        }
    }
}

var path = require('path')

function resolve(dir) {
    return path.join(__dirname, './', dir)
}
