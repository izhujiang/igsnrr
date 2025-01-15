const http = require("http");
const fs = require("fs");
const path = require("path");

/**
 * Sends a POST request and saves the response to a dynamically named file.
 *
 * @param {string} areaCode - The area code to include in the request.
 * @param {string} type - The type of data (e.g., WIND).
 * @param {string} dataTime - The date and time in the format 'yyyy-MM-dd hh:mm'.
 */
function fetchAndSaveData(areaCode, type, dataTime) {
  // directory: ./data/{yyyy}/{type}/
  const directoryPath = path.join(
    __dirname,
    "data",
    dataTime.slice(0, 4),
    type,
  );
  ensureDirectoryExists(directoryPath);

  // Encode the request data
  const postData = `areaCode=${areaCode}&type=${type}&dataTime=${encodeURIComponent(dataTime)}`;

  const formattedDate = dataTime
    .replace(/[-:]/g, "")
    .replace(/[ ]/g, "-")
    .slice(0, 13); // yyyyMMddhhmm
  const filename = path.join(directoryPath, `${type}_${formattedDate}.json`);

  console.log(filename);
  if (fs.existsSync(filename)) {
    console.log("File exists, skip fetching data again.");
    return;
  }
  // else {
  // console.log("File does not exist");
  // return;
  // }

  console.log(`make request: ${type}  ${dataTime}`);

  // Configure the HTTP request
  const options = {
    hostname: "nm.weweather.net",
    port: 80,
    path: "/wewap/Live/GetSurfFormData",
    method: "POST",
    headers: {
      Connection: "keep-alive",
      "Content-Length": Buffer.byteLength(postData),
      Accept: "*/*",
      "X-Requested-With": "XMLHttpRequest",
      "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090c1f) XWEB/11581 Flue",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      Origin: "http://nm.weweather.net",
      Referer: `http://nm.weweather.net/wewap/Live/SurfForm?stationNum=${areaCode}&m=${areaCode}`,
      "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "zh-CN,zh;q=0.9",
    },
  };

  // Make the HTTP request
  const req = http.request(options, (res) => {
    let data = "";

    // console.log(`Status Code: ${res.statusCode}`);
    // console.log('Headers:', res.headers);

    res.on("data", (chunk) => {
      data += chunk;
    });

    res.on("end", () => {
      console.log(`Response received, saving to ${filename}`);
      // Save the response to the file
      fs.writeFile(filename, data, (err) => {
        if (err) {
          console.error("Error writing to file:", err);
        } else {
          console.log(`Response saved to ${filename}`);
        }
      });
    });
  });

  req.on("error", (e) => {
    console.error(`Problem with request: ${e.message}`);
  });

  // Write the data and end the request
  req.write(postData);
  req.end();
}

/**
 * Checks if a directory exists, and creates it if it doesn't.
 *
 * @param {string} dirPath - The path of the directory to check or create.
 */
function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    // Directory doesn't exist, create it
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`Directory created: ${dirPath}`);
  }
}

// Example usage

// Example usage
// fetchAndSaveData('52267', 'TEMP', '2025-01-07 16:00');
// fetchAndSaveData('52267', 'Press', '2025-01-07 16:00');
// fetchAndSaveData('52267', 'RAIN', '2025-01-07 16:00');
// fetchAndSaveData('52267', 'WIND', '2025-01-07 16:00');
// fetchAndSaveData('52267', 'RH', '2025-01-07 16:00');
// fetchAndSaveData('52267', 'VIS', '2025-01-07 16:00');

function randomSleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchAndSaveDataRange(startTime, endTime) {
  const start = Date.parse(startTime.concat("+00:00").replace(" ", "T")); // Replace space with 'T' to make it ISO 8601 compatible
  const end = Date.parse(endTime.concat("+00:00").replace(" ", "T"));

  if (start >= end) {
    console.log("Start time must be before end time.");
    return;
  }

  let currentTime = new Date(start);

  // Sleep for a random duration between 0 and max_interval seconds
  console.log("Start fetching.");
  const max_interval = 10;
  while (currentTime <= end) {
    const formattedTime = currentTime
      .toISOString()
      .replace("T", " ")
      .substring(0, 16);

    var randomSeconds = Math.floor(1 + Math.random() * max_interval);
    console.log(`Sleeping for ${randomSeconds} seconds...`);
    await randomSleep(randomSeconds * 1000);
    fetchAndSaveData("52267", "TEMP", formattedTime);

    randomSeconds = Math.floor(1 + Math.random() * max_interval);
    console.log(`Sleeping for ${randomSeconds} seconds...`);
    await randomSleep(randomSeconds * 1000);
    fetchAndSaveData("52267", "RAIN", formattedTime);

    randomSeconds = Math.floor(1 + Math.random() * max_interval);
    console.log(`Sleeping for ${randomSeconds} seconds...`);
    await randomSleep(randomSeconds * 1000);
    fetchAndSaveData("52267", "WIND", formattedTime);

    randomSeconds = Math.floor(1 + Math.random() * max_interval);
    console.log(`Sleeping for ${randomSeconds} seconds...`);
    await randomSleep(randomSeconds * 1000);
    fetchAndSaveData("52267", "Press", formattedTime);

    randomSeconds = Math.floor(1 + Math.random() * max_interval);
    console.log(`Sleeping for ${randomSeconds} seconds...`);
    await randomSleep(randomSeconds * 1000);
    fetchAndSaveData("52267", "RH", formattedTime);

    randomSeconds = Math.floor(1 + Math.random() * max_interval);
    console.log(`Sleeping for ${randomSeconds} seconds...`);
    await randomSleep(randomSeconds * 1000);
    fetchAndSaveData("52267", "VIS", formattedTime);

    console.log(`Current time: ${formattedTime}`);
    currentTime.setHours(currentTime.getHours() + 1);
  }

  console.log("Finished over the time range.");
}

// Example usage:
// dataTime format must be: "YYYY-MM-DD HH:mm" like "2025-01-12 00:00"
// fetchAndSaveDataRange("2025-01-14 00:00", "2025-01-15 01:00");
//
//

// main entry
// --------------------------------------------------------
//
// Access command-line arguments
const args = process.argv;

// The first two arguments are the Node.js binary and the script name.
// The third argument is the first user-supplied argument.
// node fetch.js auto
const inputArg = args[2];

if (inputArg == "auto") {
  const now = new Date();
  // Get yesterday's date
  const yesterday = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate() - 1,
    now.getHours(),
  );
  const startOfYesterday = `${yesterday.toISOString().slice(0, 10)} 00:00`;
  const endOfYesterday = `${yesterday.toISOString().slice(0, 10)} 23:00`;

  // console.log(startOfYesterday, endOfYesterday);
  fetchAndSaveDataRange(startOfYesterday, endOfYesterday);
} else {
  // modify range and run manually
  // dataTime format must be: "YYYY-MM-DD HH:mm" like "2025-01-12 00:00"
  data_range_start = "2025-01-14 00:00";
  data_range_end = "2025-01-15 01:00";
  fetchAndSaveDataRange(data_range_start, data_range_end);
}