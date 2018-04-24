const path = require("path");
const webpack = require("webpack");
const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const DashboardPlugin = require("webpack-dashboard/plugin");

module.exports = {
  entry: {
    app: [
      "react-hot-loader/patch",
      "webpack-dev-server/client?http://192.168.86.238:8080",
      "webpack/hot/only-dev-server",
      "./app/index.js"
    ]
  },
  output: {
    path: path.resolve(__dirname, "../static/ui-assets/"),
    filename: "[name].js"
  },
  devServer: {
    historyApiFallback: true,
    contentBase: "./public",
    hot: true
  },
  plugins: [
    new webpack.NamedModulesPlugin(),
    new webpack.HotModuleReplacementPlugin(),
    new ProgressBarPlugin(),
    new DashboardPlugin(),
    new HtmlWebpackPlugin({
      title: "Development",
      template: path.resolve(__dirname, "public/index.html"),
      inject: true
    })
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: "babel-loader"
      },
      {
        test: /\.png$/,
        use: "file-loader"
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      }
    ]
  },
  resolve: {
    modules: ["./", "./app", "node_modules"],
    extensions: [".js", ".json", ".css"]
  }
};
