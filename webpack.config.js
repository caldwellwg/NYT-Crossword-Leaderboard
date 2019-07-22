const path = require('path');

module.exports = {
  entry: path.join(__dirname, "extract_source.js"),
  output: {
    filename: 'extract.js',
    path: path.resolve(__dirname)
  }
};