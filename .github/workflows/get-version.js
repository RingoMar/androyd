let fs = require('fs')
console.log(JSON.parse(fs.readFileSync('./version.json', 'utf8')).version)
