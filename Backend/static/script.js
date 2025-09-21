document.addEventListener("DOMContentLoaded", () => {
  // --- Element Selectors ---
  const elements = {
    dropArea: document.getElementById("dropArea"),
    fileInput: document.getElementById("fileInput"),
    fileListContainer: document.getElementById("fileListContainer"),
    submitBtn: document.getElementById("submitBtn"),
    languageSelector: document.getElementById("languageSelector"),
    placeholder: document.getElementById("placeholder"),
    processing: document.getElementById("processing-state"),
    results: document.getElementById("results-display"),
    originalTextContent: document.getElementById("original-text-content"),
    sanitizedTextContent: document.getElementById("sanitized-text-content"),
    statusMessage: document.getElementById("statusMessage"),
  };

  // Critical check for elements
  for (const key in elements) {
    if (!elements[key]) {
      console.error(
        `Initialization Failed: HTML element with id="${key}" was not found.`
      );
      return;
    }
  }

  let uploadedFile = null;

  // --- Main Interaction Logic ---
  async function submitDocument() {
    if (!uploadedFile) {
      alert("Please select a file first.");
      return;
    }

    elements.submitBtn.disabled = true;
    updateUIState("processing");
    document.getElementById("processing-status-text").innerText =
      "Analyzing Document...";

    // --- SIMULATED PIPELINE ---
    // This function simulates the backend processing delay
    // and then shows the pre-generated results.

    setTimeout(() => {
      // 1. Define the pre-generated medical report data
      const pregeneratedPii = {
        Names:
          "ANURAG KERBHAU SANDBHOR MANISHA S.C.E.SOC'S INDIRA COLLEGE OF ENGINEERING & MGT.",
        "Any characters": "F190520013 72245713J",
        "Phone Numbers": " ",
        ID: "22 - 1399157 R23052622835",
        "Insurance Policy": " ",
        "Numbers ": "1550000",
        "Credit Card Details": " ",
        "Account Number": " ",
        "IP address": " ",
      };

      // 2. Define the sanitized (dummy) version of the data
      const sanitizedPii = {
        Names: "Rohan Verma", // Names often remain for context
        "Any characters ": "F190520013 72245713J",
        "Phone Numbers": " ",
        ID: "22 - 1399157 R23052622835",
        "Insurance Policy": " ",
        "Treatment Bill": " ",
        "Credit Card Details": " ",
        "Account Number": " ",
        "IP address": " ",
      };

      // 3. Call the function to display these results
      displayResults(pregeneratedPii, sanitizedPii);

      // 4. Re-enable the submit button
      elements.submitBtn.disabled = false;
    }, 2500); // Simulate a 2.5 second analysis time
  }

  // --- Display and Helper Functions ---
  function displayResults(originalPii, sanitizedPii) {
    // Helper function to format the data objects into readable text
    const formatDataToString = (dataObject) => {
      let text = "--- PII Analysis ---\n\n";
      for (const [key, value] of Object.entries(dataObject)) {
        text += `${key.padEnd(20)}: ${value}\n`;
      }
      return text;
    };

    // Populate the text containers with the formatted strings
    elements.originalTextContent.textContent = formatDataToString(originalPii);
    elements.sanitizedTextContent.textContent =
      formatDataToString(sanitizedPii);

    const piiCount = Object.keys(originalPii).length;
    elements.statusMessage.className = "status-message status-success";
    elements.statusMessage.textContent = `Success! ${piiCount} PII items were found and sanitized.`;

    updateUIState("results");
  }

  function displayError(message) {
    elements.originalTextContent.textContent = "";
    elements.sanitizedTextContent.textContent = "";
    elements.statusMessage.className = "status-message status-error";
    elements.statusMessage.textContent = `Error: ${message}`;
    updateUIState("results");
  }

  function updateUIState(state) {
    const states = ["placeholder", "processing", "results"];
    states.forEach((s) => {
      const el = elements[s];
      if (el) el.classList.remove("active");
    });
    if (elements[state]) {
      elements[state].classList.add("active");
    }
  }

  // --- File Handling Functions (for UI interaction) ---
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function handleFiles(files) {
    if (files.length > 0) {
      uploadedFile = files[0];
      renderFileList();
    }
  }

  function renderFileList() {
    if (!uploadedFile) {
      elements.fileListContainer.innerHTML = "";
      return;
    }
    const fileSize = (uploadedFile.size / 1024).toFixed(1);
    elements.fileListContainer.innerHTML = `
        <div class="file-item">
            <div class="file-details">
                <span class="file-name">${uploadedFile.name}</span>
                <span class="file-size">${fileSize} KB</span>
            </div>
            <button class="remove-btn" id="removeFileBtn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
        </div>
    `;
    document
      .getElementById("removeFileBtn")
      .addEventListener("click", removeFile);
  }

  function removeFile() {
    uploadedFile = null;
    elements.fileInput.value = "";
    renderFileList();
    updateUIState("placeholder");
  }

  // --- Initial Event Listeners Setup ---
  elements.dropArea.addEventListener("click", () => elements.fileInput.click());
  elements.fileInput.addEventListener("change", () =>
    handleFiles(elements.fileInput.files)
  );

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) =>
    elements.dropArea.addEventListener(eventName, preventDefaults, false)
  );
  ["dragenter", "dragover"].forEach((eventName) =>
    elements.dropArea.addEventListener(
      eventName,
      () => elements.dropArea.classList.add("dragover"),
      false
    )
  );
  ["dragleave", "drop"].forEach((eventName) =>
    elements.dropArea.addEventListener(
      eventName,
      () => elements.dropArea.classList.remove("dragover"),
      false
    )
  );

  elements.dropArea.addEventListener(
    "drop",
    (e) => handleFiles(e.dataTransfer.files),
    false
  );
  elements.submitBtn.addEventListener("click", submitDocument);

  // Initial page setup
  updateUIState("placeholder");
});
