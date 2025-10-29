const fs = require('fs');
const express = require('express');

app.get('/data', (req, res) => {
    const results = [];
    fstatSync.createReadStream('./section_data/MATH.csv')
        .pipe(csv())
        .on('data', (row) => results.push(row))
        .on('end', () => res.json(results));
})

app.listen(3000, () => console.log('Server running on port 3000'))