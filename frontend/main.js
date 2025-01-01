// src/main.js
const API_URL = "http://localhost:8000";
const containerDiv = document.getElementById("container");
const loginForm = document.getElementById("login-form");
const logoutForm = document.getElementById("logout-form");
const promptForm = document.getElementById("prompt-form");
const welcomeMessage = document.getElementById("welcome-message");
const promptResponse = document.getElementById("prompt-response");

function update_vertical_centering() {
  containerDiv.style.top = `${
    (window.innerHeight - containerDiv.clientHeight) / 2
  }px`;
}

async function is_authenticated() {
  try {
    const response = await fetch(`${API_URL}/users/me/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${document.cookie.split("=")[1]}`,
      },
    });
    const data = await response.json();
    if (data.id && data.username) {
      return data;
    } else {
      return false;
    }
  } catch (error) {
    window.alert("Authentication Error: " + error);
  }
}

async function refresh_is_authenticated() {
  // Check if user is authenticated
  promptResponse.innerText = "";
  const user_info = await is_authenticated();
  if (user_info) {
    welcomeMessage.innerHTML = `Hey, ${user_info.username}`;
    loginForm.style.display = "none";
    promptForm.style.display = "block";
    promptForm.reset();
    logoutForm.style.display = "block";
  } else {
    welcomeMessage.innerHTML = "Who are you?";
    loginForm.style.display = "block";
    loginForm.reset();
    promptForm.style.display = "none";
    logoutForm.style.display = "none";
  }
  update_vertical_centering();
}

function logout() {
  document.cookie = "access_token=logged_out";
  refresh_is_authenticated();
}

async function login() {
  const formData = new FormData(loginForm);
  try {
    const response = await fetch(`${API_URL}/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(formData),
    });
    const data = await response.json();
    if (data.access_token) {
      console.log("Login Success!")
    } else {
      loginForm.reset();
      window.alert("Incorrect username or password");
      console.log("Login Failed!");
    }
    document.cookie = `access_token=${data.access_token}`;
  } catch (error) {
    window.alert("Error Logging In: " + error);
  }
  refresh_is_authenticated();
}

async function submitPrompt() {
  const formData = new FormData(promptForm);
  try {
    const response = await fetch(`${API_URL}/prompt`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${document.cookie.split("=")[1]}`,
      },
      body: JSON.stringify({
        prompt: formData.get("prompt"),
      }),
    });
    const data = await response.json();
    promptResponse.innerText = data.response;
  } catch (error) {
    window.alert("Error: " + error);
  }
  update_vertical_centering();
}

// Add event listeners once DOM is loaded
document.addEventListener("DOMContentLoaded", async () => {
  refresh_is_authenticated();
  // Add click handler for login form submission
  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    login();
  });
  logoutForm.addEventListener("submit", (event) => {
    event.preventDefault();
    logout();
  });
  promptForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitPrompt();
  });
});
