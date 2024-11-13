let currentStep = 1;
const totalSteps = 4;

function changeStep(step) {
  if (step === 1 && !validateStep(currentStep)) {
    return;
  }
  const steps = document.querySelectorAll(".step");
  steps[currentStep - 1].classList.remove("active");
  currentStep += step;
  if (currentStep < 1) currentStep = 1;
  if (currentStep > totalSteps) currentStep = totalSteps;
  steps[currentStep - 1].classList.add("active");
  updateProgressBar();
  updateButtons();
  if (currentStep === 3) {
    populateReview();
  }
  if (currentStep === 4) {
    submitForm();
  }
}

function validateStep(step) {
  const currentStepFields = document.querySelector(`#step${step}`).querySelectorAll("input, select");
  let valid = true;
  currentStepFields.forEach(field => {
    if (!field.checkValidity()) {
      field.style.borderColor = "#e74c3c";
      valid = false;
    } else {
      field.style.borderColor = "#ccc";
    }
  });
  return valid;
}

function updateProgressBar() {
  for (let i = 1; i <= totalSteps; i++) {
    document.getElementById(`progress${i}`).classList.toggle("active", i <= currentStep);
  }
}

function updateButtons() {
  document.getElementById("prevBtn").style.display = currentStep === 1 ? "none" : "inline-block";
  document.getElementById("nextBtn").innerHTML = currentStep === totalSteps ? "Submit" : "Next";
  if (currentStep === totalSteps) {
    document.getElementById("nextBtn").onclick = () => submitForm();
  } else {
    document.getElementById("nextBtn").onclick = () => changeStep(1);
  }
}

function populateReview() {
  const reviewDiv = document.getElementById("review");
  const formData = new FormData(document.getElementById("multiStepForm"));
  reviewDiv.innerHTML = "";
  for (let [key, value] of formData.entries()) {
    reviewDiv.innerHTML += `<div class="review-item"><label>${key}:</label> <span>${value}</span></div>`;
  }
}

function selectForm(formType) {
  document.querySelector('.selection-container').style.display = 'none';
  document.getElementById('formContainer').style.display = 'block';
}

function toggleRAGFields() {
  const ragRequired = document.getElementById("ragRequired");
  const ragFields = document.getElementById("ragFields");
  ragFields.style.display = ragRequired.checked ? "block" : "none";
}

function showTooltip(element) {
  const tooltip = document.createElement("div");
  tooltip.className = "tooltip";
  tooltip.innerText = element.getAttribute("title");
  document.body.appendChild(tooltip);
  const rect = element.getBoundingClientRect();
  tooltip.style.left = `${rect.left + window.scrollX + 20}px`;
  tooltip.style.top = `${rect.top + window.scrollY - 10}px`;
  tooltip.style.display = "block";
  element.onmouseleave = () => {
    tooltip.remove();
  };
}

function submitForm() {
  const formData = new FormData(document.getElementById("multiStepForm"));
  fetch('/calculate-pricing', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(Object.fromEntries(formData))
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert('Error: ' + data.error);
    } else {
      displayResults(data);
    }
  })
  .catch(error => console.error('Error:', error));
}

function displayResults(data) {
  const resultsTable = document.getElementById("resultsTableBody");
  resultsTable.innerHTML = `
    <tr>
      <td>${data.model}</td>
      <td>${data.region}</td>
      <td>${data.total_tokens}</td>
      <td>${(data.cost / data.total_tokens * 1000).toFixed(2)} €</td>
      <td>${data.cost.toFixed(2)} €</td>
    </tr>
  `;
  document.getElementById("totalPrice").innerText = `${data.cost.toFixed(2)} €`;
}

function downloadExcel() {
  const table = document.querySelector('.results-table');
  let tableHTML = table.outerHTML.replace(/ /g, '%20');

  const a = document.createElement('a');
  a.href = 'data:application/vnd.ms-excel,' + tableHTML;
  a.download = 'pricing_results.xls';
  a.click();
}

updateButtons();
