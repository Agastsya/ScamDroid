const mongoose = require("mongoose");
const fs = require("fs");
const path = require("path");
require("dotenv").config();
const Report = require("./models/Report");

// MongoDB Connection
async function connectDB() {
  const username = process.env.MONGO_USER || "agastsya";
  const password = process.env.MONGO_PASS || process.env.DB_PASSWORD;
  const cluster =
    process.env.MONGO_CLUSTER || "scamdroidcontent.atxdi0k.mongodb.net";

  const uri = `mongodb+srv://${username}:${password}@${cluster}/scamdroidcontent?retryWrites=true&w=majority`;

  try {
    await mongoose.connect(uri, {
      serverSelectionTimeoutMS: 5000,
    });
    console.log("✅ Connected to MongoDB with Mongoose!");
  } catch (err) {
    console.error(`❌ Connection failed: ${err.message}`);
    process.exit(1);
  }
}

// Enhanced Data Parsing Functions
function parseAIData(content) {
  const chunks = content.split(/(?=--- Chunk \d+ Analysis ---)/gim);
  const reportData = {
    report_id: `REPORT-${Date.now()}`,
    system_info: detectSystemInfo(content),
    vulnerabilities: [],
    summary: {
      total_vulnerabilities: 0,
      critical_count: 0,
      high_count: 0,
      medium_count: 0,
      low_count: 0,
    },
  };

  const typeMapping = {
    "Weak Password Policy": "Weak Passwords",
    "Unauthenticated Access to Sensitive Data": "Unauthenticated Access",
    "Sensitive Data Exposure": "Sensitive Data Access",
    "Outdated SSH Protocol": "Outdated Software",
    "Insecure Network Configuration": "Insecure Configuration",
    "Misconfigured Firewall": "Misconfigured Firewall",
  };

  chunks.forEach((chunk, index) => {
    try {
      let rawType =
        extractValue(
          chunk,
          /Vulnerability\s+[\d:]+\s*[:-]\s*\*{0,2}(.+?)\*{0,2}(\n|$)/i
        ) ||
        extractJsonValue(chunk, /"type":\s*"(.+?)"/i) ||
        "Other";

      // Normalize vulnerability type
      const vulnType = typeMapping[rawType] || rawType;

      let description =
        extractValue(
          chunk,
          /\*\*Description[:\*]*\*\*\s*([\s\S]+?)(?=\n\*\*)/i
        ) ||
        extractJsonValue(chunk, /"description":\s*"(.+?)"/i) ||
        "Security vulnerability requiring attention";

      // Ensure minimum description length
      if (description.length < 20) {
        description +=
          ". This issue requires immediate remediation to prevent potential security breaches.";
      }

      const vuln = {
        vulnerability_id: index + 1,
        type: vulnType,
        description: description,
        severity: extractSeverity(chunk),
        location:
          extractValue(chunk, /\*\*Location:\*\*\s*(.+)/i) ||
          extractJsonValue(chunk, /"location":\s*"(.+?)"/i) ||
          "System-wide",
        log_entry:
          extractValue(chunk, /\*\*Log entry:\*\*\s*(.+)/i) ||
          extractJsonValue(chunk, /"log_entry":\s*"(.+?)"/i) ||
          "No log entries available",
        remediation: {
          steps: extractRemediationSteps(chunk),
          references: extractReferences(chunk),
        },
        timestamp: extractTimestamp(chunk),
      };

      if (vuln.description && vuln.severity) {
        reportData.vulnerabilities.push(vuln);
        updateSummary(reportData.summary, vuln.severity);
      }
    } catch (err) {
      console.warn(`⚠️ Error processing chunk ${index + 1}: ${err.message}`);
    }
  });

  return reportData;
}

function detectSystemInfo(content) {
  return {
    os: extractValue(content, /OS:\s*(.+)/i) || "Linux",
    version: extractValue(content, /OS Version:\s*(.+)/i) || "Unknown",
    architecture: extractValue(content, /Architecture:\s*(.+)/i) || "x86_64",
  };
}

function extractValue(text, regex) {
  const match = text.match(regex);
  return match ? match[1].trim().replace(/\*\*/g, "") : null;
}

function extractJsonValue(text, regex) {
  const match = text.match(regex);
  return match ? match[1].trim().replace(/"/g, "") : null;
}

function extractSeverity(text) {
  const severityMatch = text.match(
    /(?:"severity":\s*"|Severity:\s*\**\s*)(Critical|High|Medium|Low)/i
  );
  return severityMatch
    ? severityMatch[1].charAt(0).toUpperCase() +
        severityMatch[1].slice(1).toLowerCase()
    : "Medium";
}

function extractRemediationSteps(text) {
  const steps = [];

  // Try to extract from JSON blocks
  const jsonRegex = /```json\s*([\s\S]+?)\s*```/g;
  const jsonMatches = text.matchAll(jsonRegex);

  for (const match of jsonMatches) {
    try {
      const jsonData = JSON.parse(match[1]);
      if (jsonData.steps || jsonData.recommendations) {
        const stepsArray = jsonData.steps || jsonData.recommendations;
        stepsArray.forEach((step) => {
          const stepDesc =
            step.description || step.action || "Security remediation step";
          steps.push({
            description:
              stepDesc.length < 10 ? `${stepDesc} (security update)` : stepDesc,
            commands: step.commands || [step.command].filter((c) => c) || [],
            notes: step.notes || "No additional notes",
          });
        });
        break;
      }
    } catch (e) {
      console.warn("⚠️ Error parsing JSON steps:", e.message);
    }
  }

  // Fallback to command list extraction
  if (steps.length === 0) {
    const commandMatches = text.matchAll(/\*\s*`(.+?)`/g);
    for (const match of commandMatches) {
      steps.push({
        description: "Security remediation command",
        commands: [match[1]],
        notes: "Automatically extracted from report",
      });
    }
  }

  return steps.length > 0
    ? steps
    : [
        {
          description: "Standard security remediation procedure",
          commands: [],
          notes: "Consult security documentation for details",
        },
      ];
}

function extractReferences(chunk) {
  const refs = [];
  const refMatches = chunk.matchAll(/(https?:\/\/[^\s]+)/g);
  for (const match of refMatches) {
    refs.push(match[0]);
  }
  return refs;
}

function extractTimestamp(chunk) {
  const dateMatch = chunk.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/);
  return dateMatch ? new Date(dateMatch[0]) : new Date();
}

function updateSummary(summary, severity) {
  summary.total_vulnerabilities++;
  switch (severity.toLowerCase()) {
    case "critical":
      summary.critical_count++;
      break;
    case "high":
      summary.high_count++;
      break;
    case "medium":
      summary.medium_count++;
      break;
    case "low":
      summary.low_count++;
      break;
  }
}

// Main Upload Function
async function uploadStructuredReport() {
  try {
    await connectDB();

    const reportPath = path.join(__dirname, "aiReport", "ai_report.txt");
    if (!fs.existsSync(reportPath)) {
      throw new Error("AI report file not found at " + reportPath);
    }

    const rawContent = fs.readFileSync(reportPath, "utf-8");
    const structuredData = parseAIData(rawContent);

    console.log(
      "Parsed vulnerabilities:",
      structuredData.vulnerabilities.length
    );
    console.log(
      "Sample vulnerability:",
      JSON.stringify(structuredData.vulnerabilities[0], null, 2)
    );

    const newReport = new Report(structuredData);
    const savedReport = await newReport.save();

    console.log(`✅ Successfully stored report ID: ${savedReport.report_id}`);
    console.log("Summary:", savedReport.summary);
    return savedReport;
  } catch (err) {
    console.error("💥 Error details:", err);
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  uploadStructuredReport();
}
