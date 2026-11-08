/**
 * Public Client-side JavaScript
 * Language Toggle, Consultation Request AJAX, Mobile Navigation
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById("mobileToggle");
  const navLinks = document.getElementById("navLinks");
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener("click", () => {
      navLinks.classList.toggle("active");
    });
  }

  // 2. Language Switcher
  const langSwitchBtns = document.querySelectorAll(".lang-switch-action");
  langSwitchBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const targetLang = btn.dataset.lang;
      // Set cookie for 1 year
      document.cookie = `site_lang=${targetLang};path=/;max-age=31536000;SameSite=Lax`;
      
      // Also update URL query if present, otherwise reload
      const url = new URL(window.location.href);
      url.searchParams.set("lang", targetLang);
      window.location.href = url.toString();
    });
  });

  // 3. Consultation Booking AJAX Form
  const bookingForm = document.getElementById("consultationForm");
  const formAlert = document.getElementById("formAlert");
  const submitBtn = document.getElementById("submitBookingBtn");

  if (bookingForm) {
    bookingForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const originalBtnText = submitBtn ? submitBtn.innerText : "Submit";
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = submitBtn.dataset.submittingText || "Submitting...";
      }

      const formData = new FormData(bookingForm);
      const payload = {
        client_name: formData.get("client_name"),
        email: formData.get("email"),
        phone: formData.get("phone"),
        service_type: formData.get("service_type"),
        session_format: formData.get("session_format"),
        preferred_date: formData.get("preferred_date") || "",
        preferred_time: formData.get("preferred_time") || "",
        notes: formData.get("notes") || "",
        language_used: document.documentElement.lang || "en"
      };

      try {
        const response = await fetch("/api/appointments/book", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok && result.success) {
          if (formAlert) {
            formAlert.className = "form-alert success";
            formAlert.innerHTML = `<strong>${result.title || "Success"}</strong>: ${result.message}`;
            formAlert.style.display = "block";
          }
          bookingForm.reset();
        } else {
          throw new Error(result.detail || "Unable to submit your request. Please check required fields.");
        }
      } catch (err) {
        if (formAlert) {
          formAlert.className = "form-alert error";
          formAlert.innerHTML = `<strong>Error</strong>: ${err.message}`;
          formAlert.style.display = "block";
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerText = originalBtnText;
        }
        if (formAlert) {
          formAlert.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }
    });
  }

  // 4. Set current year in footer
  const currentYearSpan = document.getElementById("currentYear");
  if (currentYearSpan) {
    currentYearSpan.textContent = new Date().getFullYear();
  }
});
