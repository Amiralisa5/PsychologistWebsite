/**
 * Dasein Journal — Persian (Jalali) Calendar & Google Integration Helper
 * Provides bidirectional Shamsi <-> Gregorian conversion, interactive date picker,
 * and Google Calendar / Google Meet notification modal handling.
 */

const PERSIAN_MONTH_NAMES = [
  "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
  "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
];

const PERSIAN_DIGITS = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];

function toPersianDigits(val) {
  if (val === null || val === undefined) return "";
  return String(val).replace(/\d/g, d => PERSIAN_DIGITS[d]);
}

function toEnglishDigits(val) {
  if (!val) return "";
  const pDigits = "۰۱۲۳۴۵۶۷۸۹";
  const aDigits = "٠١٢٣٤٥٦٧٨٩";
  return String(val)
    .replace(/[۰-۹]/g, ch => pDigits.indexOf(ch))
    .replace(/[٠-٩]/g, ch => aDigits.indexOf(ch));
}

function gregorianToJalali(gy, gm, gd) {
  const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
  const gy2 = (gm > 2) ? (gy + 1) : gy;
  let days = 355666 + (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) + gd + g_d_m[gm - 1];
  let jy = -1595 + (33 * Math.floor(days / 12053));
  days %= 12053;
  jy += 4 * Math.floor(days / 1461);
  days %= 1461;
  if (days > 365) {
    jy += Math.floor((days - 1) / 365);
    days = (days - 1) % 365;
  }
  const jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
  const jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
  return [jy, jm, jd];
}

function jalaliToGregorian(jy, jm, jd) {
  jy += 1595;
  let days = -355668 + (365 * jy) + (Math.floor(jy / 33) * 8) + Math.floor(((jy % 33) + 3) / 4) + jd + ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
  let gy = 400 * Math.floor(days / 146097);
  days %= 146097;
  if (days > 36524) {
    days -= 1;
    gy += 100 * Math.floor(days / 36524);
    days %= 36524;
    if (days >= 365) days += 1;
  }
  gy += 4 * Math.floor(days / 1461);
  days %= 1461;
  if (days > 365) {
    gy += Math.floor((days - 1) / 365);
    days = (days - 1) % 365;
  }
  let gd = days + 1;
  const isLeap = ((gy % 4 === 0 && gy % 100 !== 0) || gy % 400 === 0);
  const sal_a = [0, 31, isLeap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  let gm = 0;
  while (gm < 13 && gd > sal_a[gm]) {
    gd -= sal_a[gm];
    gm += 1;
  }
  return [gy, gm, gd];
}

function padZero(num) {
  return num < 10 ? "0" + num : String(num);
}

/**
 * Initializes the Persian Calendar interactive widget on forms
 */
function initPersianDatePicker() {
  const container = document.getElementById("shamsiPickerWrap");
  const rawDateInput = document.getElementById("preferred_date");
  const shamsiDateInput = document.getElementById("preferred_date_shamsi");
  const badge = document.getElementById("shamsiDatePreview");

  if (!container || !rawDateInput) return;

  const daySelect = document.getElementById("shamsiDay");
  const monthSelect = document.getElementById("shamsiMonth");
  const yearSelect = document.getElementById("shamsiYear");

  if (!daySelect || !monthSelect || !yearSelect) return;

  function syncFromShamsi() {
    const jy = parseInt(yearSelect.value, 10);
    const jm = parseInt(monthSelect.value, 10);
    const jd = parseInt(daySelect.value, 10);

    const [gy, gm, gd] = jalaliToGregorian(jy, jm, jd);
    const gregIso = `${gy}-${padZero(gm)}-${padZero(gd)}`;
    const shamsiStr = `${jy}/${padZero(jm)}/${padZero(jd)}`;

    rawDateInput.value = gregIso;
    if (shamsiDateInput) shamsiDateInput.value = shamsiStr;

    if (badge) {
      const monthName = PERSIAN_MONTH_NAMES[jm - 1] || "";
      badge.innerHTML = `<strong>🗓️ تقویم خورشیدی:</strong> ${toPersianDigits(jd)} ${monthName} ${toPersianDigits(jy)} <span style="color:#64748b; font-size:0.8rem;">(${gregIso})</span>`;
    }
  }

  daySelect.addEventListener("change", syncFromShamsi);
  monthSelect.addEventListener("change", syncFromShamsi);
  yearSelect.addEventListener("change", syncFromShamsi);

  // Initialize with tomorrow's date
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const [currJy, currJm, currJd] = gregorianToJalali(
    tomorrow.getFullYear(),
    tomorrow.getMonth() + 1,
    tomorrow.getDate()
  );

  yearSelect.value = currJy;
  monthSelect.value = currJm;
  daySelect.value = currJd;
  syncFromShamsi();
}

/**
 * Shows the rich appointment notification pop-up modal
 */
function showAppointmentSuccessModal(data) {
  const modal = document.getElementById("appointmentSuccessModal");
  if (!modal) return;

  const isFa = document.documentElement.lang === "fa" || document.documentElement.dir === "rtl";

  // Elements
  const clientEl = document.getElementById("modalClientName");
  const serviceEl = document.getElementById("modalService");
  const formatEl = document.getElementById("modalFormat");
  const dateEl = document.getElementById("modalDate");
  const timeEl = document.getElementById("modalTime");
  const meetRow = document.getElementById("modalMeetRow");
  const meetBtn = document.getElementById("modalMeetBtn");
  const meetLinkText = document.getElementById("modalMeetLinkText");
  const calBtn = document.getElementById("modalCalendarBtn");

  if (clientEl) clientEl.innerText = data.client_name || "";
  if (serviceEl) serviceEl.innerText = data.service_type || "";
  if (formatEl) {
    formatEl.innerText = data.session_format === "Online"
      ? (isFa ? "جلسه آنلاین تصویری (Google Meet)" : "Online Video Session (Google Meet)")
      : (isFa ? "جلسه حضوری (کلینیک کارگر شمالی)" : "In-Person Clinic Session");
  }

  if (dateEl) {
    if (isFa) {
      dateEl.innerHTML = `${toPersianDigits(data.preferred_date_shamsi || "")} <span style="color:#64748b; font-size:0.82rem;">(${data.preferred_date || ""})</span>`;
    } else {
      dateEl.innerHTML = `${data.preferred_date || ""} <span style="color:#64748b; font-size:0.82rem;">(${toPersianDigits(data.preferred_date_shamsi || "")})</span>`;
    }
  }

  if (timeEl) timeEl.innerText = data.preferred_time || "";

  // Handle Google Meet link
  const meetUrl = data.meet_link || "https://meet.google.com/das-ein-meet";
  if (meetRow) {
    if (data.session_format === "Online") {
      meetRow.style.display = "flex";
      if (meetBtn) meetBtn.href = meetUrl;
      if (meetLinkText) meetLinkText.innerText = meetUrl;
    } else {
      meetRow.style.display = "none";
    }
  }

  // Handle Google Calendar button
  if (calBtn && data.google_calendar_url) {
    calBtn.href = data.google_calendar_url;
  }

  modal.classList.add("active");
}

function closeAppointmentSuccessModal() {
  const modal = document.getElementById("appointmentSuccessModal");
  if (modal) modal.classList.remove("active");
}

function copyMeetLink() {
  const linkText = document.getElementById("modalMeetLinkText")?.innerText || "https://meet.google.com/das-ein-meet";
  navigator.clipboard.writeText(linkText).then(() => {
    alert(document.documentElement.lang === "fa" ? "✅ لینک Google Meet کپی شد!" : "✅ Google Meet link copied to clipboard!");
  });
}

/**
 * Initializes the Upcoming Clinical Event notification popup
 */
function initEventNotificationPopup() {
  const popup = document.getElementById("eventNotificationPopup");
  if (!popup) return;

  const eventId = popup.dataset.eventId;
  const isDismissed = sessionStorage.getItem("dismissed_event_" + eventId);
  if (isDismissed) {
    popup.style.display = "none";
    return;
  }

  popup.style.display = "block";
}

function dismissEventPopup(eventId) {
  const popup = document.getElementById("eventNotificationPopup");
  if (popup) {
    popup.style.display = "none";
    sessionStorage.setItem("dismissed_event_" + eventId, "true");
  }
}

// Auto-run on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initPersianDatePicker();
  initEventNotificationPopup();

  // Close modal when clicking outside content
  const modal = document.getElementById("appointmentSuccessModal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        closeAppointmentSuccessModal();
      }
    });
  }
});
