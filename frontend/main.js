// src/main.js
const API_URL = "http://localhost:8000";

const loginForm = document.getElementById("login-form");
const loadDocumentsButton = document.getElementById("load-documents");
const documentsDiv = document.getElementById("documents");

async function login() {
  const formData = new FormData(loginForm);
  // formData.append("grant_type", "password");
  // const urlSearchParams = new URLSearchParams(formData);
  // console.log(urlSearchParams);
  try {
    const response = await fetch(`${API_URL}/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(formData),
    });
    const data = await response.json();
    document.cookie = `access_token=${data.access_token}`;
    window.alert("Login successful");
  } catch (error) {
    window.alert("Error: " + error);
  }
}

// Add event listeners once DOM is loaded
document.addEventListener("DOMContentLoaded", async () => {
  // Add click handler for login form submission
  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    login();
  });
  loadDocumentsButton.addEventListener("click", async () => {
    try {
      const response = await fetch(`${API_URL}/documents/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${document.cookie.split("=")[1]}`,
        },
      });
      const data = await response.json();
      documentsDiv.innerHTML = "";
      data.forEach((doc) => {
        const div = document.createElement("div");
        div.innerHTML = `<h3>${doc.title}</h3><p>${doc.content}</p>`;
        documentsDiv.appendChild(div);
      });
    } catch (error) {
      window.alert("Error: " + error);
    }
  });
});
