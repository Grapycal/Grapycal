const path = require('path');
const webpack = require('webpack');
module.exports = {
    entry: "./src/app.ts",
    plugins: [
        new webpack.DefinePlugin({
            __BUILD_CONFIG__: JSON.stringify({
                isService: true,
                wsPort: null, // will be set by the service
            }),
        }),
    ],
    module: { rules: [] },
    resolve: { extensions: [".ts", ".js"] },
    mode: "development",
    module: {
        rules: [
            {
                test: /\.ts$/i,
                //use: ["ts-loader",MiniCssExtractPlugin.loader, 'css-loader'],
                // to use MiniCssExtractPlugin.loader, 'css-loader' on css files only, use this:
                use: [
                    {
                        loader: 'ts-loader',
                        options: { allowTsInNodeModules: true }
                    }
                ],
            },
        ]
    },
    watchOptions: {
        ignored: [
            '**/svg/',
        ]
    },
    devServer: {
        static: {
            directory: path.join(__dirname, 'dist'),
        },
        compress: true,
        port: 9001,
    },
};