const mongoose = require("mongoose");

const remediationStepSchema = new mongoose.Schema({
  description: {
    type: String,
    required: [true, "Remediation step description is required"],
    minlength: [10, "Description must be at least 10 characters"],
  },
  commands: {
    type: [String],
    validate: {
      validator: function (v) {
        return v.length <= 20;
      },
      message: "Exceeded maximum of 20 commands per step",
    },
  },
  notes: {
    type: String,
    default: "No additional notes",
  },
});

const vulnerabilitySchema = new mongoose.Schema({
  vulnerability_id: {
    type: Number,
    required: [true, "Vulnerability ID is required"],
    min: [1, "Invalid vulnerability ID"],
  },
  type: {
    type: String,
    required: [true, "Vulnerability type is required"],
    enum: {
      values: [
        "Weak Passwords",
        "Outdated Software",
        "SQL Injection",
        "XSS",
        "Insecure Configuration",
        "Unauthorized Access",
        "Sensitive Data Exposure",
        "Unsecured SSH Access",
        "Insufficient Logging",
        "Open Ports",
        "Misconfigured Firewall",
        "Weak Password Policy",
        "Unauthenticated Access",
        "Sensitive Data Access",
        "Other",
      ],
      message: "Invalid vulnerability type: {VALUE}",
    },
    default: "Other",
  },
  description: {
    type: String,
    required: [true, "Description is required"],
    minlength: [20, "Description must be at least 20 characters"],
    maxlength: [1500, "Description exceeds 1500 character limit"],
  },
  severity: {
    type: String,
    required: true,
    enum: {
      values: ["Critical", "High", "Medium", "Low"],
      message: "Invalid severity level: {VALUE}",
    },
    default: "Medium",
  },
  location: {
    type: String,
    default: "System-wide",
  },
  log_entry: {
    type: String,
    default: "No log entries available",
  },
  remediation: {
    steps: {
      type: [remediationStepSchema],
      validate: {
        validator: function (v) {
          return v.length > 0;
        },
        message: "At least one remediation step is required",
      },
    },
    references: [
      {
        type: String,
        match: [
          /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/,
          "Invalid URL format",
        ],
      },
    ],
  },
  timestamp: {
    type: Date,
    default: Date.now,
  },
});

const reportSchema = new mongoose.Schema({
  report_id: {
    type: String,
    unique: true,
    required: true,
    index: true,
    match: [/^REPORT-\d{13}$/, "Invalid report ID format"],
  },
  system_info: {
    os: {
      type: String,
      required: true,
      default: "Linux",
    },
    version: {
      type: String,
      required: true,
      default: "Unknown",
    },
    architecture: {
      type: String,
      required: true,
      default: "x86_64",
    },
  },
  vulnerabilities: {
    type: [vulnerabilitySchema],
    validate: {
      validator: function (v) {
        return v.length > 0;
      },
      message: "At least one vulnerability must be reported",
    },
  },
  summary: {
    total_vulnerabilities: {
      type: Number,
      min: [0, "Vulnerability count cannot be negative"],
    },
    critical_count: Number,
    high_count: Number,
    medium_count: Number,
    low_count: Number,
  },
  generated_at: {
    type: Date,
    default: Date.now,
  },
});

reportSchema.pre("validate", function (next) {
  this.summary = {
    total_vulnerabilities: this.vulnerabilities.length,
    critical_count: this.vulnerabilities.filter(
      (v) => v.severity === "Critical"
    ).length,
    high_count: this.vulnerabilities.filter((v) => v.severity === "High")
      .length,
    medium_count: this.vulnerabilities.filter((v) => v.severity === "Medium")
      .length,
    low_count: this.vulnerabilities.filter((v) => v.severity === "Low").length,
  };
  next();
});

module.exports = mongoose.model("Report", reportSchema);
