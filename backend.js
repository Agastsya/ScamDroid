const mongoose = require("mongoose");
const fs = require("fs");
const path = require("path");
require("dotenv").config();
const Report = require("./models/Report");

// 1. Connect to MongoDB
async function connectDB() {
  try {
    await mongoose.connect(
      `mongodb+srv://${process.env.MONGO_USER}:${process.env.MONGO_PASS}@${process.env.MONGO_CLUSTER}/scamdroidcontent`,
      {
        serverSelectionTimeoutMS: 5000,
        dbName: "scamdroid",
      }
    );
    console.log("🔥 MongoDB Connected!");
  } catch (err) {
    console.error(`💥 Connection Failed: ${err.message}`);
    process.exit(1);
  }
}

// 2. Upload JSON
async function uploadJSON() {
  try {
    // Read file
    const filePath = path.join(__dirname, "aiReport", "ai_report.txt");
    const rawData = fs.readFileSync(filePath, "utf-8");
    const jsonData = JSON.parse(rawData);

    // Create document
    const newReport = new Report({
      reportData: jsonData,
    });

    // Save to DB
    const savedReport = await newReport.save();

    // Output results
    console.log("🚀 Upload Successful!");
    console.log("Document ID:", savedReport._id);
    console.log("Report ID:", savedReport.reportData.report_id);
    console.log(
      "Vulnerabilities:",
      savedReport.reportData.vulnerabilities.length
    );
  } catch (err) {
    console.error(`💣 ERROR: ${err.message}`);
  } finally {
    await mongoose.disconnect();
    process.exit();
  }
}

// 3. Run
(async () => {
  await connectDB();
  await uploadJSON();
})();
