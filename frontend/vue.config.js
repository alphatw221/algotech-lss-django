const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
   publicPath: "http://127.0.0.1:8081/static", // for development,  ip should 127.0.0.1, django server as well
    // publicPath: "/static", // for production
    // outputDir: "./dist/",
    outputDir: "../static/",
    chainWebpack: config => {
        config.optimization.splitChunks(false)

        config.plugin('BundleTracker').use(BundleTracker, [
            {
                filename: './webpack-stats.json'
            }
        ])

        config.resolve.alias.set('__STATIC__', 'static')

        config.devServer
            .host('0.0.0.0')
            .port(8081)
            .hot(true)
            .https(false)
            .headers({'Access-Control-Allow-Origin': ['\*']})
    }
};