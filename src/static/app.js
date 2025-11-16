document.addEventListener("DOMContentLoaded", () => {
  loadActivities();

  const signupForm = document.getElementById("signup-form");
  signupForm.addEventListener("submit", handleSignup);
});

// Load activities from the server
async function loadActivities() {
  try {
    const response = await fetch("/activities");
    const activities = await response.json();

    displayActivities(activities);
    populateActivitySelect(activities);
  } catch (error) {
    console.error("Error loading activities:", error);
    document.getElementById("activities-list").innerHTML = "<p>Error loading activities</p>";
  }
}

// Display activities on the page
function displayActivities(activities) {
  const activitiesList = document.getElementById("activities-list");
  activitiesList.innerHTML = "";

  for (const [name, details] of Object.entries(activities)) {
    const activityCard = document.createElement("div");
    activityCard.className = "activity-card";

    const participantsList =
      details.participants.length > 0
        ? `<ul class="participants-list">${details.participants.map((email) => 
            `<li><span class="participant-email">${email}</span><button class="delete-btn" onclick="unregisterParticipant('${name}', '${email}')" title="Remove participant">✕</button></li>`
          ).join("")}</ul>`
        : '<p class="no-participants">No participants yet</p>';

    activityCard.innerHTML = `
            <h4>${name}</h4>
            <p><strong>Description:</strong> ${details.description}</p>
            <p><strong>Schedule:</strong> ${details.schedule}</p>
            <p><strong>Capacity:</strong> ${details.participants.length}/${details.max_participants}</p>
            <div class="participants-section">
                <h5>Participants:</h5>
                ${participantsList}
            </div>
        `;

    activitiesList.appendChild(activityCard);
  }
}

// Populate the activity select dropdown
function populateActivitySelect(activities) {
  const activitySelect = document.getElementById("activity");
  activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

  for (const activityName of Object.keys(activities)) {
    const option = document.createElement("option");
    option.value = activityName;
    option.textContent = activityName;
    activitySelect.appendChild(option);
  }
}

// Handle the signup form submission
async function handleSignup(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const activity = document.getElementById("activity").value;
  const messageDiv = document.getElementById("message");

  if (!email || !activity) {
    showMessage("Please fill in all fields", "error");
    return;
  }

  try {
    const response = await fetch(`/activities/${encodeURIComponent(activity)}/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `email=${encodeURIComponent(email)}`,
    });

    const data = await response.json();

    if (response.ok) {
      showMessage(data.message, "success");
      document.getElementById("signup-form").reset();
      loadActivities(); // Reload to show updated participant list
    } else {
      showMessage(data.detail, "error");
    }
  } catch (error) {
    console.error("Error signing up:", error);
    showMessage("An error occurred while signing up", "error");
  }
}

// Unregister a participant from an activity
async function unregisterParticipant(activityName, email) {
  if (!confirm(`Are you sure you want to unregister ${email} from ${activityName}?`)) {
    return;
  }

  try {
    const response = await fetch(`/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(email)}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (response.ok) {
      showMessage(data.message, "success");
      loadActivities(); // Reload to show updated participant list
    } else {
      showMessage(data.detail, "error");
    }
  } catch (error) {
    console.error("Error unregistering participant:", error);
    showMessage("An error occurred while unregistering participant", "error");
  }
}

// Show a message to the user
function showMessage(text, type) {
  const messageDiv = document.getElementById("message");
  messageDiv.textContent = text;
  messageDiv.className = `message ${type}`;
  messageDiv.classList.remove("hidden");

  setTimeout(() => {
    messageDiv.classList.add("hidden");
  }, 5000);
}
