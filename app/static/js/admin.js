/**
 * Admin Portal JavaScript
 * Manages Appointments, Notes, Articles, and Therapist Profile
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Appointment Filter & Search
  const filterTabs = document.querySelectorAll(".filter-tab");
  const appointmentRows = document.querySelectorAll(".appointment-row");
  const searchInput = document.getElementById("searchAppointments");

  function filterAppointments() {
    const activeTab = document.querySelector(".filter-tab.active");
    const statusFilter = activeTab ? activeTab.dataset.status : "all";
    const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

    appointmentRows.forEach(row => {
      const rowStatus = row.dataset.status.toLowerCase();
      const rowText = row.innerText.toLowerCase();

      const matchesStatus = (statusFilter === "all" || rowStatus === statusFilter);
      const matchesQuery = (!query || rowText.includes(query));

      row.style.display = (matchesStatus && matchesQuery) ? "" : "none";
    });
  }

  filterTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      filterTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      filterAppointments();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", filterAppointments);
  }

  // 2. Appointment Details & Note Modal
  const apptModal = document.getElementById("appointmentModal");
  const closeApptModal = document.getElementById("closeApptModal");
  const apptNotesForm = document.getElementById("apptNotesForm");

  window.openAppointmentModal = function(id, name, email, phone, service, format, date, time, notes, status, therapistNotes) {
    if (!apptModal) return;

    document.getElementById("modalApptId").value = id;
    document.getElementById("modalClientName").textContent = name;
    document.getElementById("modalClientEmail").textContent = email;
    document.getElementById("modalClientPhone").textContent = phone;
    document.getElementById("modalService").textContent = service;
    document.getElementById("modalFormat").textContent = format;
    document.getElementById("modalDateTime").textContent = `${date || 'Flexible'} · ${time || 'Anytime'}`;
    document.getElementById("modalClientNotes").textContent = notes || "None provided";
    document.getElementById("modalApptStatus").value = status;
    document.getElementById("modalTherapistNotes").value = therapistNotes || "";

    apptModal.classList.add("active");
  };

  if (closeApptModal) {
    closeApptModal.addEventListener("click", () => {
      apptModal.classList.remove("active");
    });
  }

  if (apptModal) {
    apptModal.addEventListener("click", (e) => {
      if (e.target === apptModal) {
        apptModal.classList.remove("active");
      }
    });
  }

  if (apptNotesForm) {
    apptNotesForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const id = document.getElementById("modalApptId").value;
      const status = document.getElementById("modalApptStatus").value;
      const therapistNotes = document.getElementById("modalTherapistNotes").value;

      try {
        const response = await fetch(`/api/admin/appointments/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: status, therapist_notes: therapistNotes })
        });
        const res = await response.json();
        if (response.ok && res.success) {
          window.location.reload();
        } else {
          alert(res.detail || "Error updating appointment");
        }
      } catch (err) {
        alert("Failed to update: " + err.message);
      }
    });
  }

  // 3. Quick Status Change from Dropdown
  document.querySelectorAll(".quick-status-select").forEach(select => {
    select.addEventListener("change", async (e) => {
      const apptId = select.dataset.id;
      const newStatus = select.value;

      try {
        const response = await fetch(`/api/admin/appointments/${apptId}/status`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: newStatus })
        });
        const res = await response.json();
        if (response.ok && res.success) {
          // Update status pill styling
          window.location.reload();
        } else {
          alert(res.detail || "Could not update status");
        }
      } catch (err) {
        alert("Network error: " + err.message);
      }
    });
  });

  // 4. Delete Article
  window.deleteArticle = async function(id, title) {
    if (!confirm(`Are you sure you want to delete article: "${title}"?`)) {
      return;
    }
    try {
      const response = await fetch(`/api/admin/articles/${id}`, {
        method: "DELETE"
      });
      const res = await response.json();
      if (response.ok && res.success) {
        window.location.reload();
      } else {
        alert(res.detail || "Error deleting article");
      }
    } catch (err) {
      alert("Network error: " + err.message);
    }
  };
});
