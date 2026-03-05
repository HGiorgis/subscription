// Modern JavaScript with animations and enhanced UX

// Wait for DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

function initializeApp() {
  // Initialize all components
  initializeAlerts();
  initializePasswordStrength();
  initializeLogoutConfirmation();
  initializeProfilePicturePreview();
  initializeScrollAnimations();
  initializeTooltips();
  initializeFormAnimations();
  initializeCountdowns();
  initializeThemeToggle();
  initializeMobileMenu();
}

// Enhanced Alert System with animations
function initializeAlerts() {
  const alerts = document.querySelectorAll(".alert");

  alerts.forEach((alert, index) => {
    // Add entrance animation with delay based on index
    alert.style.animation = `slideIn 0.5s ease-out ${index * 0.1}s both`;

    // Auto-dismiss after 5 seconds
    setTimeout(
      () => {
        if (alert && alert.parentNode) {
          alert.style.transition = "all 0.5s ease";
          alert.style.opacity = "0";
          alert.style.transform = "translateX(100%)";

          setTimeout(() => {
            if (alert.parentNode) {
              alert.remove();
            }
          }, 500);
        }
      },
      5000 + index * 100,
    );

    // Add close button functionality
    const closeBtn = alert.querySelector(".btn-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.style.transition = "all 0.3s ease";
        alert.style.opacity = "0";
        alert.style.transform = "translateX(100%)";
        setTimeout(() => alert.remove(), 300);
      });
    }
  });
}

// Enhanced Password Strength Indicator
function initializePasswordStrength() {
  const passwordInput = document.getElementById("id_password1");
  if (!passwordInput) return;

  // Create modern strength indicator
  const container = document.createElement("div");
  container.className = "password-strength-container mt-3";
  container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="small fw-semibold text-muted">Password Strength</span>
            <span class="strength-label small fw-bold">Weak</span>
        </div>
        <div class="progress" style="height: 8px;">
            <div class="progress-bar strength-bar" role="progressbar" style="width: 0%"></div>
        </div>
        <div class="strength-requirements mt-2 small text-muted">
            <div class="requirement" data-req="length">✓ At least 8 characters</div>
            <div class="requirement" data-req="lowercase">✓ Contains lowercase letter</div>
            <div class="requirement" data-req="uppercase">✓ Contains uppercase letter</div>
            <div class="requirement" data-req="number">✓ Contains number</div>
            <div class="requirement" data-req="special">✓ Contains special character</div>
        </div>
    `;

  passwordInput.parentNode.appendChild(container);

  const strengthBar = container.querySelector(".strength-bar");
  const strengthLabel = container.querySelector(".strength-label");
  const requirements = container.querySelectorAll(".requirement");

  // Style requirements
  requirements.forEach((req) => {
    req.style.transition = "all 0.3s ease";
    req.style.opacity = "0.5";
  });

  passwordInput.addEventListener("input", function () {
    const password = this.value;
    const strength = calculatePasswordStrength(password);
    const percentage = (strength.score / 5) * 100;

    // Update progress bar
    strengthBar.style.width = percentage + "%";
    strengthBar.style.transition = "width 0.3s ease";

    // Update colors and label
    if (strength.score <= 2) {
      strengthBar.className = "progress-bar bg-danger";
      strengthLabel.textContent = "Weak";
      strengthLabel.style.color = "#ef4444";
    } else if (strength.score <= 4) {
      strengthBar.className = "progress-bar bg-warning";
      strengthLabel.textContent = "Medium";
      strengthLabel.style.color = "#f59e0b";
    } else {
      strengthBar.className = "progress-bar bg-success";
      strengthLabel.textContent = "Strong";
      strengthLabel.style.color = "#10b981";
    }

    // Update requirements
    updateRequirement(requirements[0], strength.hasLength);
    updateRequirement(requirements[1], strength.hasLowercase);
    updateRequirement(requirements[2], strength.hasUppercase);
    updateRequirement(requirements[3], strength.hasNumber);
    updateRequirement(requirements[4], strength.hasSpecial);
  });
}

function calculatePasswordStrength(password) {
  return {
    hasLength: password.length >= 8,
    hasLowercase: /[a-z]/.test(password),
    hasUppercase: /[A-Z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSpecial: /[$@#&!]/.test(password),
    score: [
      password.length >= 8,
      /[a-z]/.test(password),
      /[A-Z]/.test(password),
      /[0-9]/.test(password),
      /[$@#&!]/.test(password),
    ].filter(Boolean).length,
  };
}

function updateRequirement(element, condition) {
  if (condition) {
    element.style.opacity = "1";
    element.style.color = "#10b981";
  } else {
    element.style.opacity = "0.5";
    element.style.color = "#64748b";
  }
}

// Enhanced Logout Confirmation with modal
function initializeLogoutConfirmation() {
  const logoutLinks = document.querySelectorAll('a[href*="logout"]');

  logoutLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      // Create modern modal
      const modal = document.createElement("div");
      modal.className = "modal fade show";
      modal.style.display = "block";
      modal.style.backgroundColor = "rgba(0,0,0,0.5)";
      modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-sign-out-alt text-warning me-2"></i>
                                Confirm Logout
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Are you sure you want to logout?</p>
                            <p class="small text-muted">You'll need to login again to access your account.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i>Cancel
                            </button>
                            <a href="${link.href}" class="btn btn-danger" id="confirmLogout">
                                <i class="fas fa-sign-out-alt me-1"></i>Logout
                            </a>
                        </div>
                    </div>
                </div>
            `;

      document.body.appendChild(modal);

      // Add backdrop
      const backdrop = document.createElement("div");
      backdrop.className = "modal-backdrop fade show";
      document.body.appendChild(backdrop);

      // Handle close
      const closeModal = () => {
        modal.remove();
        backdrop.remove();
      };

      modal.querySelectorAll('[data-bs-dismiss="modal"]').forEach((btn) => {
        btn.addEventListener("click", closeModal);
      });

      // Handle logout confirmation
      document
        .getElementById("confirmLogout")
        .addEventListener("click", function (e) {
          e.preventDefault();
          window.location.href = link.href;
        });
    });
  });
}

// Enhanced Profile Picture Preview with animation
function initializeProfilePicturePreview() {
  const profilePicInput = document.getElementById("id_profile_picture");
  if (!profilePicInput) return;

  const preview = document.querySelector(
    "img.rounded-circle, .profile-pic-preview",
  );
  const container = profilePicInput.parentNode;

  // Add modern upload button
  const uploadBtn = document.createElement("div");
  uploadBtn.className = "profile-upload-btn mt-3";
  uploadBtn.innerHTML = `
        <label for="${profilePicInput.id}" class="btn btn-outline-primary w-100">
            <i class="fas fa-camera me-2"></i>Change Profile Picture
        </label>
    `;

  profilePicInput.style.display = "none";
  container.appendChild(uploadBtn);

  profilePicInput.addEventListener("change", function (e) {
    if (this.files && this.files[0]) {
      const reader = new FileReader();

      reader.onload = function (e) {
        if (preview) {
          // Add animation
          preview.style.transition = "all 0.3s ease";
          preview.style.transform = "scale(0.9)";

          setTimeout(() => {
            preview.src = e.target.result;
            preview.style.transform = "scale(1)";
          }, 150);
        }

        // Show success message
        showToast("Profile picture updated successfully!", "success");
      };

      reader.readAsDataURL(this.files[0]);
    }
  });
}

// Scroll Animations
function initializeScrollAnimations() {
  const elements = document.querySelectorAll(
    ".card, .stats-card, .animate-on-scroll",
  );

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
        }
      });
    },
    { threshold: 0.1 },
  );

  elements.forEach((element) => {
    element.style.opacity = "0";
    element.style.transform = "translateY(20px)";
    element.style.transition = "all 0.6s ease";
    observer.observe(element);
  });
}

// Tooltips
function initializeTooltips() {
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach((element) => {
    new bootstrap.Tooltip(element);
  });
}

// Form Animations
function initializeFormAnimations() {
  const formControls = document.querySelectorAll(".form-control, .form-select");

  formControls.forEach((element) => {
    element.addEventListener("focus", () => {
      element.parentElement?.classList.add("focused");
    });

    element.addEventListener("blur", () => {
      element.parentElement?.classList.remove("focused");
    });
  });
}

// Countdown Timers
function initializeCountdowns() {
  const countdownElements = document.querySelectorAll("[data-countdown]");

  countdownElements.forEach((element) => {
    const endDate = new Date(element.dataset.countdown).getTime();

    const updateCountdown = () => {
      const now = new Date().getTime();
      const distance = endDate - now;

      if (distance < 0) {
        element.textContent = "Expired";
        return;
      }

      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      const hours = Math.floor(
        (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
      );
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);

      element.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    };

    updateCountdown();
    setInterval(updateCountdown, 1000);
  });
}

// Theme Toggle
function initializeThemeToggle() {
  const themeToggle = document.getElementById("theme-toggle");
  if (!themeToggle) return;

  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme");
    const isDark = document.body.classList.contains("dark-theme");
    localStorage.setItem("theme", isDark ? "dark" : "light");

    themeToggle.innerHTML = isDark
      ? '<i class="fas fa-sun"></i>'
      : '<i class="fas fa-moon"></i>';
  });

  // Load saved theme
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-theme");
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
  }
}

// Mobile Menu Enhancement
function initializeMobileMenu() {
  const navbarToggler = document.querySelector(".navbar-toggler");
  const navbarCollapse = document.querySelector(".navbar-collapse");

  if (navbarToggler && navbarCollapse) {
    navbarToggler.addEventListener("click", () => {
      navbarCollapse.classList.toggle("show");
      navbarToggler.classList.toggle("active");
    });

    // Close menu on link click
    navbarCollapse.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", () => {
        navbarCollapse.classList.remove("show");
        navbarToggler.classList.remove("active");
      });
    });
  }
}

// Toast Notification System
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast-notification toast-${type}`;
  toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${getToastIcon(type)} me-2"></i>
            <span>${message}</span>
        </div>
    `;

  // Style the toast
  toast.style.position = "fixed";
  toast.style.top = "20px";
  toast.style.right = "20px";
  toast.style.zIndex = "9999";
  toast.style.minWidth = "300px";
  toast.style.padding = "1rem";
  toast.style.borderRadius = "8px";
  toast.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
  toast.style.animation = "slideIn 0.3s ease";
  toast.style.backgroundColor =
    type === "success"
      ? "#10b981"
      : type === "error"
        ? "#ef4444"
        : type === "warning"
          ? "#f59e0b"
          : "#3b82f6";
  toast.style.color = "white";

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideOut 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function getToastIcon(type) {
  return type === "success"
    ? "fa-check-circle"
    : type === "error"
      ? "fa-exclamation-circle"
      : type === "warning"
        ? "fa-exclamation-triangle"
        : "fa-info-circle";
}

// Loading State
function showLoading(button) {
  button.disabled = true;
  const originalText = button.innerHTML;
  button.innerHTML = '<span class="loading me-2"></span>Loading...';
  button.dataset.originalText = originalText;
}

function hideLoading(button) {
  button.disabled = false;
  button.innerHTML = button.dataset.originalText || "Submit";
}

// Form Validation
function validateForm(form) {
  const inputs = form.querySelectorAll(
    "input[required], select[required], textarea[required]",
  );
  let isValid = true;

  inputs.forEach((input) => {
    if (!input.value.trim()) {
      isValid = false;
      input.classList.add("is-invalid");

      // Create error message if not exists
      if (!input.nextElementSibling?.classList.contains("invalid-feedback")) {
        const error = document.createElement("div");
        error.className = "invalid-feedback";
        error.textContent = "This field is required";
        input.parentNode.insertBefore(error, input.nextSibling);
      }
    } else {
      input.classList.remove("is-invalid");
    }
  });

  return isValid;
}

// Add slideOut animation
const style = document.createElement("style");
style.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Export functions for use in other modules
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.validateForm = validateForm;
