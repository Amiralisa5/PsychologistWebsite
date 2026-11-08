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

  window.openAppointmentModal = function(id, name, email, phone, service, format, date, time, notes, status, therapistNotes, meetLink, googleCalLink, dateShamsi) {
    if (!apptModal) return;

    document.getElementById("modalApptId").value = id;
    document.getElementById("modalClientName").textContent = name;
    document.getElementById("modalClientEmail").textContent = email;
    document.getElementById("modalClientPhone").textContent = phone;
    document.getElementById("modalService").textContent = service;
    document.getElementById("modalFormat").textContent = format;
    
    // Display both Shamsi & Gregorian
    const dateDisplay = dateShamsi ? `${dateShamsi} (${date || 'Flexible'})` : (date || 'Flexible');
    document.getElementById("modalDateTime").textContent = `${dateDisplay} · ${time || 'Anytime'}`;
    document.getElementById("modalClientNotes").textContent = notes || "None provided";
    document.getElementById("modalApptStatus").value = status;
    document.getElementById("modalTherapistNotes").value = therapistNotes || "";

    const meetInput = document.getElementById("modalMeetLink");
    const directMeetBtn = document.getElementById("modalDirectMeetBtn");
    const directCalBtn = document.getElementById("modalDirectCalBtn");

    const effectiveMeet = meetLink || "https://meet.google.com/das-ein-meet";
    if (meetInput) meetInput.value = effectiveMeet;
    if (directMeetBtn) directMeetBtn.href = effectiveMeet;
    if (directCalBtn && googleCalLink) directCalBtn.href = googleCalLink;

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
      const meetLink = document.getElementById("modalMeetLink")?.value || "";

      try {
        const response = await fetch(`/api/admin/appointments/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            status: status,
            therapist_notes: therapistNotes,
            meet_link: meetLink
          })
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

  // 5. Admin Notification Bell & Popover
  const notifBell = document.getElementById("adminNotifBell");
  const notifDropdown = document.getElementById("adminNotifDropdown");
  const notifBadgePill = document.getElementById("notifBadgePill");
  const notifPendingHeader = document.getElementById("notifPendingHeader");
  const notifListContainer = document.getElementById("notifListContainer");

  async function loadAdminNotifications() {
    if (!notifBell || !notifListContainer) return;
    try {
      const res = await fetch("/api/admin/notifications");
      if (!res.ok) return;
      const data = await res.json();

      const count = data.pending_count || 0;
      if (notifBadgePill) {
        if (count > 0) {
          notifBadgePill.textContent = count;
          notifBadgePill.style.display = "flex";
        } else {
          notifBadgePill.style.display = "none";
        }
      }

      if (notifPendingHeader) {
        notifPendingHeader.textContent = count > 0 ? `${count} Pending` : "All Clear";
      }

      let html = "";
      if (data.pending_items && data.pending_items.length > 0) {
        data.pending_items.forEach(item => {
          const isOnline = item.session_format === "Online";
          html += `
            <div class="notif-item">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.25rem;">
                <strong style="color:#0f172a;">${item.client_name}</strong>
                <span style="font-size:0.75rem; background:#fee2e2; color:#b91c1c; padding:1px 6px; border-radius:4px;">Pending</span>
              </div>
              <div style="font-size:0.8rem; color:#475569; margin-bottom:0.35rem;">
                <span>${item.service_type}</span> · 
                <span style="color:#0284c7; font-weight:600;">${isOnline ? 'Online (Meet)' : 'In-Person'}</span>
              </div>
              <div style="font-size:0.78rem; color:#64748b; margin-bottom:0.5rem;">
                🗓️ <strong>${item.date_shamsi || ''}</strong> (${item.date || 'Flexible'})
              </div>
              <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
                ${isOnline ? `<a href="${item.meet_link || 'https://meet.google.com/das-ein-meet'}" target="_blank" class="btn btn-meet btn-sm" style="padding:0.2rem 0.5rem; font-size:0.72rem;">📹 Meet</a>` : ''}
                <a href="${item.google_calendar_url}" target="_blank" class="btn btn-calendar btn-sm" style="padding:0.2rem 0.5rem; font-size:0.72rem;">📅 Calendar</a>
                <a href="/admin/appointments" class="btn btn-outline btn-sm" style="padding:0.2rem 0.5rem; font-size:0.72rem;">Review</a>
              </div>
            </div>
          `;
        });
      } else {
        html = '<div style="padding:1.5rem; text-align:center; color:#94a3b8; font-size:0.85rem;">🎉 No pending consultation requests.</div>';
      }

      // Add upcoming webinar/event if present
      if (data.events && data.events.length > 0) {
        html += '<div style="background:#f8fafc; padding:0.4rem 1rem; font-size:0.75rem; font-weight:700; color:#475569; border-top:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">Upcoming Clinical Events</div>';
        data.events.forEach(evt => {
          html += `
            <div class="notif-item" style="background:#f0fdf4;">
              <div style="font-weight:600; color:#166534; font-size:0.82rem; margin-bottom:0.2rem;">${evt.title_fa || evt.title_en}</div>
              <div style="font-size:0.78rem; color:#15803d; margin-bottom:0.4rem;">🗓️ ${evt.date_shamsi} · Google Meet</div>
              <div style="display:flex; gap:0.4rem;">
                <a href="${evt.meet_link}" target="_blank" class="btn btn-meet btn-sm" style="padding:0.15rem 0.45rem; font-size:0.72rem;">📹 Join Room</a>
                <a href="${evt.google_calendar_url}" target="_blank" class="btn btn-calendar btn-sm" style="padding:0.15rem 0.45rem; font-size:0.72rem;">📅 Cal</a>
              </div>
            </div>
          `;
        });
      }

      notifListContainer.innerHTML = html;
    } catch (e) {
      console.warn("Failed to load notifications:", e);
    }
  }

  if (notifBell && notifDropdown) {
    notifBell.addEventListener("click", (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle("active");
    });

    document.addEventListener("click", (e) => {
      if (!notifDropdown.contains(e.target) && e.target !== notifBell) {
        notifDropdown.classList.remove("active");
      }
    });

    loadAdminNotifications();
  }
});
