//imports
const path = require('path');
const fs = require('fs');
const csv = require('csv-parser');
const express = require('express');
const cors = require('cors');
const spawn = require("child_process").spawn;

const pythonProcess = spawn('python',["SoC_Scraper.py"]);

const csvFilePath = path.join(__dirname, '/section_data/MATH.csv');
const app = express();
const PORT = 3000;

const records = []

pythonProcess.stdout.on('data', (data) => {
 console.log(data)
});

fs.createReadStream(csvFilePath)
    .pipe(csv())
    .on("data", data => records.push(data))
    .on("end", () => {
        console.log("CSV file successfully processed");
    });


app.use(
    cors()
);

app.get("/", (req, res) => {
    res.json(records);
})

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
