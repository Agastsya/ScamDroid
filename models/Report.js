const mongoose = require("mongoose");

const reportSchema = new mongoose.Schema(
  {
    reportData: mongoose.Schema.Types.Mixed,
  },
  { strict: false }
);

module.exports = mongoose.model("Report", reportSchema);
