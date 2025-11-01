const fs = require('fs');
const express = require('express');
const csv = require('csv-parser');
const app = express();

app.get('/data', (req, res) => {
    const results = [];
    fs.createReadStream('./section_data/MATH.csv')
        .pipe(csv())
        .on('data', (row) => results.push(row))
        .on('end', () => res.json(results));
})

app.listen(5500, () => console.log('Server running on port 5500'))
