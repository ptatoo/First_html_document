const fs = require('fs');
const csv = require('csv-parser');
const express = require('express');
const cors = require('cors');

const csvFilePath = './server/section_data/MATH.csv';
const app = express();
const PORT = 3000;

const records = []

fs.createReadStream(csvFilePath)
    .pipe(csv())
    .on("data", data => records.push(data))
    .on("end", () => {
        console.log("CSV file successfully processed");
    });

app.use(
    cors({
        origin: ['http://localhost:5173']
    })
);

app.get("/", (req, res) => {
    res.json(records);
})

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
