// Clean JavaScript for better UX

document.addEventListener("DOMContentLoaded", function () {
  initializeAlerts();
  initializePasswordStrength();
  initializeLogoutConfirmation();
  initializeProfilePicturePreview();
  initializeTooltips();
});

// Simple alert dismissal with animation
function initializeAlerts() {
  const alerts = document.querySelectorAll(".alert");

  alerts.forEach((alert, index) => {
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      if (alert && alert.parentNode) {
        alert.style.transition = "opacity 0.3s ease";
        alert.style.opacity = "0";

        setTimeout(() => {
          if (alert.parentNode) {
            alert.remove();
          }
        }, 300);
      }
    }, 5000);
  });
}

// Simple password strength indicator
function initializePasswordStrength() {
  const passwordInput = document.getElementById("id_password1");
  if (!passwordInput) return;

  // Create simple strength indicator
  const container = document.createElement("div");
  container.className = "mt-2";
  container.innerHTML = `
        <div class="progress" style="height: 4px;">
            <div class="progress-bar" role="progressbar" style="width: 0%"></div>
        </div>
        <small class="text-muted mt-1 d-block">Use at least 8 characters with letters and numbers</small>
    `;

  passwordInput.parentNode.appendChild(container);

  const strengthBar = container.querySelector(".progress-bar");

  passwordInput.addEventListener("input", function () {
    const password = this.value;
    const strength = calculateStrength(password);

    strengthBar.style.width = strength.percentage + "%";

    if (strength.score <= 2) {
      strengthBar.className = "progress-bar bg-danger";
    } else if (strength.score <= 4) {
      strengthBar.className = "progress-bar bg-warning";
    } else {
      strengthBar.className = "progress-bar bg-success";
    }
  });
}

function calculateStrength(password) {
  let score = 0;
  if (password.length >= 8) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[$@#&!]/.test(password)) score++;

  return {
    score: score,
    percentage: (score / 5) * 100,
  };
}

// Simple logout confirmation
function initializeLogoutConfirmation() {
  const logoutLinks = document.querySelectorAll('a[href*="logout"]');

  logoutLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      if (!confirm("Are you sure you want to logout?")) {
        e.preventDefault();
      }
    });
  });
}

// Simple profile picture preview
function initializeProfilePicturePreview() {
  const profilePicInput = document.getElementById("id_profile_picture");
  if (!profilePicInput) return;

  profilePicInput.addEventListener("change", function (e) {
    if (this.files && this.files[0]) {
      const reader = new FileReader();

      reader.onload = function (e) {
        const preview = document.querySelector(
          "img.rounded-circle, .profile-avatar",
        );
        if (preview) {
          preview.src = e.target.result;
        }
      };

      reader.readAsDataURL(this.files[0]);
    }
  });
}

// Simple tooltips
function initializeTooltips() {
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach((element) => {
    new bootstrap.Tooltip(element);
  });
}
