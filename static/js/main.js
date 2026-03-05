/* =========================================
   PREMIUM JAVASCRIPT - ULTRA SMOOTH
   ========================================= */

class PremiumHub {
  constructor() {
    this.init();
  }

  init() {
    this.initNavbar();
    this.initAlerts();
    this.initPasswordStrength();
    this.initLogout();
    this.initProfilePicture();
    this.initTooltips();
    this.initDropdowns();
    this.initScrollEffects();
    this.initCountdowns();
    this.initFormValidation();
    this.initAnimations();
  }

  /* =========================================
       NAVBAR EFFECTS
       ========================================= */
  initNavbar() {
    const navbar = document.querySelector(".navbar");

    if (navbar) {
      window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
          navbar.classList.add("scrolled");
        } else {
          navbar.classList.remove("scrolled");
        }
      });
    }

    // Mobile menu close on click
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector(".navbar-collapse");

    if (navbarToggler && navbarCollapse) {
      document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", () => {
          if (window.innerWidth < 992) {
            navbarCollapse.classList.remove("show");
          }
        });
      });
    }
  }

  /* =========================================
       PREMIUM ALERTS WITH ANIMATIONS
       ========================================= */
  initAlerts() {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach((alert, index) => {
      // Stagger entrance animation
      alert.style.animation = `slideIn 0.4s ease-out ${index * 0.1}s both`;

      // Auto dismiss after 5 seconds
      setTimeout(
        () => {
          if (alert && alert.parentNode) {
            alert.style.transition = "all 0.3s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateX(20px)";

            setTimeout(() => {
              if (alert.parentNode) {
                alert.remove();
              }
            }, 300);
          }
        },
        5000 + index * 200,
      );
    });
  }

  /* =========================================
       ADVANCED PASSWORD STRENGTH
       ========================================= */
  initPasswordStrength() {
    const passwordInput = document.getElementById("id_password1");
    if (!passwordInput) return;

    // Create premium password strength indicator
    const container = document.createElement("div");
    container.className = "password-strength mt-3";
    container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="strength-text">Password Strength</span>
                <span class="strength-label fw-bold"></span>
            </div>
            <div class="strength-bar">
                <div class="strength-bar-fill"></div>
            </div>
            <div class="password-requirements mt-3">
                <div class="requirement" data-requirement="length">
                    <i class="far fa-circle"></i>
                    <span>At least 8 characters</span>
                </div>
                <div class="requirement" data-requirement="lowercase">
                    <i class="far fa-circle"></i>
                    <span>Contains lowercase letter</span>
                </div>
                <div class="requirement" data-requirement="uppercase">
                    <i class="far fa-circle"></i>
                    <span>Contains uppercase letter</span>
                </div>
                <div class="requirement" data-requirement="number">
                    <i class="far fa-circle"></i>
                    <span>Contains number</span>
                </div>
                <div class="requirement" data-requirement="special">
                    <i class="far fa-circle"></i>
                    <span>Contains special character</span>
                </div>
            </div>
        `;

    passwordInput.parentNode.appendChild(container);

    const strengthFill = container.querySelector(".strength-bar-fill");
    const strengthLabel = container.querySelector(".strength-label");
    const requirements = {
      length: container.querySelector('[data-requirement="length"]'),
      lowercase: container.querySelector('[data-requirement="lowercase"]'),
      uppercase: container.querySelector('[data-requirement="uppercase"]'),
      number: container.querySelector('[data-requirement="number"]'),
      special: container.querySelector('[data-requirement="special"]'),
    };

    // Add real-time validation
    passwordInput.addEventListener("input", () => {
      const password = passwordInput.value;
      const result = this.calculatePasswordStrength(password);

      // Update strength bar
      strengthFill.className = "strength-bar-fill " + result.class;

      // Update label
      strengthLabel.textContent = result.label;
      strengthLabel.style.color = result.color;

      // Update requirements
      this.updateRequirement(requirements.length, result.details.length);
      this.updateRequirement(requirements.lowercase, result.details.lowercase);
      this.updateRequirement(requirements.uppercase, result.details.uppercase);
      this.updateRequirement(requirements.number, result.details.number);
      this.updateRequirement(requirements.special, result.details.special);
    });
  }

  calculatePasswordStrength(password) {
    const details = {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };

    const score = Object.values(details).filter(Boolean).length;

    if (score <= 2) {
      return {
        class: "weak",
        label: "Weak",
        color: "#dc2626",
        details: details,
      };
    } else if (score <= 4) {
      return {
        class: "medium",
        label: "Medium",
        color: "#d97706",
        details: details,
      };
    } else {
      return {
        class: "strong",
        label: "Strong",
        color: "#059669",
        details: details,
      };
    }
  }

  updateRequirement(element, met) {
    if (!element) return;

    if (met) {
      element.classList.add("met");
      element.querySelector("i").className = "fas fa-check-circle";
    } else {
      element.classList.remove("met");
      element.querySelector("i").className = "far fa-circle";
    }
  }

  /* =========================================
       CONFIRM PASSWORD FIELD RENAMING
       ========================================= */
  renamePasswordFields() {
    // Rename password1 to "Password"
    const password1Field = document.querySelector('label[for="id_password1"]');
    if (password1Field) {
      password1Field.textContent = "Password";
    }

    // Rename password2 to "Confirm Password"
    const password2Field = document.querySelector('label[for="id_password2"]');
    if (password2Field) {
      password2Field.textContent = "Confirm Password";
    }

    // Add password visibility toggle
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach((input) => {
      const wrapper = document.createElement("div");
      wrapper.className = "position-relative";
      input.parentNode.insertBefore(wrapper, input);
      wrapper.appendChild(input);

      const toggleBtn = document.createElement("button");
      toggleBtn.type = "button";
      toggleBtn.className =
        "btn position-absolute end-0 top-50 translate-middle-y border-0 bg-transparent";
      toggleBtn.innerHTML = '<i class="far fa-eye"></i>';
      toggleBtn.style.zIndex = "10";

      toggleBtn.addEventListener("click", () => {
        const type = input.type === "password" ? "text" : "password";
        input.type = type;
        toggleBtn.innerHTML =
          type === "password"
            ? '<i class="far fa-eye"></i>'
            : '<i class="far fa-eye-slash"></i>';
      });

      wrapper.appendChild(toggleBtn);
    });
  }

  /* =========================================
       PREMIUM LOGOUT CONFIRMATION
       ========================================= */
  initLogout() {
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');

    logoutLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        this.showLogoutModal(link.href);
      });
    });
  }

  showLogoutModal(logoutUrl) {
    // Create modal
    const modal = document.createElement("div");
    modal.className = "modal fade show";
    modal.style.display = "block";
    modal.style.backgroundColor = "rgba(0,0,0,0.3)";
    modal.style.backdropFilter = "blur(4px)";

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
                        <p>Are you sure you want to sign out?</p>
                        <p class="small text-muted">You'll need to sign in again to access your account.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-light" data-bs-dismiss="modal">
                            Cancel
                        </button>
                        <a href="${logoutUrl}" class="btn btn-danger" id="confirmLogout">
                            <i class="fas fa-sign-out-alt me-2"></i>Sign Out
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

    // Handle logout
    document.getElementById("confirmLogout").addEventListener("click", (e) => {
      e.preventDefault();
      window.location.href = logoutUrl;
    });
  }

  /* =========================================
       PROFILE PICTURE PREVIEW
       ========================================= */
  initProfilePicture() {
    const fileInput = document.getElementById("id_profile_picture");
    if (!fileInput) return;

    // Style file input
    fileInput.style.display = "none";

    const preview = document.querySelector(
      "img.rounded-circle, .profile-avatar",
    );
    const container = fileInput.parentNode;

    // Add custom upload button
    const uploadBtn = document.createElement("label");
    uploadBtn.className = "btn btn-outline-primary btn-sm mt-2";
    uploadBtn.innerHTML = '<i class="fas fa-camera me-2"></i>Change Photo';
    uploadBtn.htmlFor = fileInput.id;

    container.appendChild(uploadBtn);

    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        const reader = new FileReader();

        reader.onload = (e) => {
          if (preview) {
            preview.style.transition = "transform 0.3s ease";
            preview.style.transform = "scale(0.9)";

            setTimeout(() => {
              preview.src = e.target.result;
              preview.style.transform = "scale(1)";
            }, 150);
          }

          this.showToast("Profile picture updated!", "success");
        };

        reader.readAsDataURL(e.target.files[0]);
      }
    });
  }

  /* =========================================
       TOOLTIPS
       ========================================= */
  initTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach((element) => {
      new bootstrap.Tooltip(element);
    });
  }

  /* =========================================
       DROPDOWN ANIMATIONS
       ========================================= */
  initDropdowns() {
    const dropdowns = document.querySelectorAll(".dropdown-toggle");

    dropdowns.forEach((dropdown) => {
      dropdown.addEventListener("show.bs.dropdown", () => {
        const menu = dropdown.nextElementSibling;
        if (menu) {
          menu.style.animation = "scaleIn 0.2s ease-out";
        }
      });
    });
  }

  /* =========================================
       SCROLL EFFECTS
       ========================================= */
  initScrollEffects() {
    // Reveal elements on scroll
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

  /* =========================================
       COUNTDOWN TIMERS
       ========================================= */
  initCountdowns() {
    const timers = document.querySelectorAll("[data-countdown]");

    timers.forEach((timer) => {
      const endDate = new Date(timer.dataset.countdown).getTime();

      const updateTimer = () => {
        const now = new Date().getTime();
        const distance = endDate - now;

        if (distance < 0) {
          timer.textContent = "Expired";
          return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor(
          (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
        );
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        timer.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
      };

      updateTimer();
      setInterval(updateTimer, 1000);
    });
  }

  /* =========================================
       FORM VALIDATION
       ========================================= */
  initFormValidation() {
    const forms = document.querySelectorAll("form");

    forms.forEach((form) => {
      form.addEventListener("submit", (e) => {
        if (!this.validateForm(form)) {
          e.preventDefault();
        }
      });
    });
  }

  validateForm(form) {
    const inputs = form.querySelectorAll("input[required]");
    let isValid = true;

    inputs.forEach((input) => {
      if (!input.value.trim()) {
        isValid = false;
        input.classList.add("is-invalid");

        // Remove error on input
        input.addEventListener(
          "input",
          () => {
            input.classList.remove("is-invalid");
          },
          { once: true },
        );
      }
    });

    return isValid;
  }

  /* =========================================
       TOAST NOTIFICATIONS
       ========================================= */
  showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${this.getToastIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
        `;

    // Style toast
    toast.style.position = "fixed";
    toast.style.top = "20px";
    toast.style.right = "20px";
    toast.style.zIndex = "9999";
    toast.style.minWidth = "300px";
    toast.style.padding = "1rem 1.5rem";
    toast.style.borderRadius = "var(--radius-xl)";
    toast.style.boxShadow = "var(--shadow-xl)";
    toast.style.animation = "slideIn 0.3s ease";
    toast.style.background =
      type === "success"
        ? "var(--success-light)"
        : type === "error"
          ? "var(--danger-light)"
          : type === "warning"
            ? "var(--warning-light)"
            : "var(--info-light)";
    toast.style.color =
      type === "success"
        ? "var(--success)"
        : type === "error"
          ? "var(--danger)"
          : type === "warning"
            ? "var(--warning)"
            : "var(--info)";
    toast.style.borderLeft = `4px solid ${
      type === "success"
        ? "var(--success)"
        : type === "error"
          ? "var(--danger)"
          : type === "warning"
            ? "var(--warning)"
            : "var(--info)"
    }`;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = "slideOut 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  getToastIcon(type) {
    return type === "success"
      ? "fa-check-circle"
      : type === "error"
        ? "fa-exclamation-circle"
        : type === "warning"
          ? "fa-exclamation-triangle"
          : "fa-info-circle";
  }

  /* =========================================
       ANIMATIONS
       ========================================= */
  initAnimations() {
    // Add slideOut animation
    const style = document.createElement("style");
    style.textContent = `
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
    document.head.appendChild(style);

    // Rename password fields
    this.renamePasswordFields();
  }
}

// Initialize PremiumHub when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.premiumHub = new PremiumHub();
});

// Export for use in other modules
window.showToast = (message, type) =>
  window.premiumHub?.showToast(message, type);
