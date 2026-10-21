// Vyta website: header menus (dropdowns and the phone menu) and the waitlist form.
(function () {
  var header = document.getElementById("site-header");
  if (header) {
    var toggle = header.querySelector(".menu-toggle");
    var triggers = header.querySelectorAll(".nav-trigger");

    function closeMenus(except) {
      triggers.forEach(function (t) { if (t !== except) t.setAttribute("aria-expanded", "false"); });
    }

    triggers.forEach(function (t) {
      t.addEventListener("click", function () {
        var open = t.getAttribute("aria-expanded") === "true";
        closeMenus(t);
        t.setAttribute("aria-expanded", open ? "false" : "true");
      });
    });

    if (toggle) {
      toggle.addEventListener("click", function () {
        var open = header.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        document.body.classList.toggle("nav-open", open);
      });
    }

    // Close on Escape, on a click outside the header, and when a menu link is followed
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var openTrigger = header.querySelector('.nav-trigger[aria-expanded="true"]');
      closeMenus();
      if (openTrigger) openTrigger.focus();
    });
    document.addEventListener("click", function (e) {
      if (!header.contains(e.target)) closeMenus();
    });
    header.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        closeMenus();
        header.classList.remove("is-open");
        document.body.classList.remove("nav-open");
        if (toggle) toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Waitlist form: checks the fields and shows a thank-you. Not connected to a form service yet.
  var form = document.getElementById("waitlist-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = form.querySelector("#wl-name").value.trim();
      var email = form.querySelector("#wl-email").value.trim();
      var role = form.querySelector('input[name="role"]:checked');
      var ok = name && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) && role;
      document.getElementById("wl-error").hidden = !!ok;
      if (!ok) return;
      form.querySelectorAll(".field, button").forEach(function (el) { el.hidden = true; });
      document.getElementById("wl-thanks").hidden = false;
    });
  }
})();
