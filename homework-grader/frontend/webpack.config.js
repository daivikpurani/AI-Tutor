const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.[contenthash].js',
    clean: true,
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js'],
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: {
          loader: 'ts-loader',
          options: { transpileOnly: true },
        },
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
  devServer: {
    static: path.join(__dirname, 'public'),
    // Port 3001 — AI-Tutor frontend occupies 3000.
    port: 3001,
    hot: true,
    // Allow the page to be embedded in the AI-Tutor frontend iframe.
    headers: { 'X-Frame-Options': 'SAMEORIGIN' },
    proxy: {
      // Forward all /grading requests to the unified backend.
      '/grading': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
};
