const path = require('path');

module.exports = {
  entry: path.join(__dirname, "src", "extract.js"),
  output: {
    filename: 'extract.js',
    path: path.resolve(__dirname, 'dist')
  }
};