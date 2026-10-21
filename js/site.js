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

  // Waitlist and contact forms (class "js-form"): check the required fields, then show the thank-you.
  // Not connected to a form service yet, so nothing is sent or saved (step 7: set the form's action).
  document.querySelectorAll("form.js-form").forEach(function (form) {
    var error = form.querySelector("[data-error]");
    var thanks = form.querySelector("[data-thanks]");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll("[required]").forEach(function (el) {
        var good;
        if (el.type === "radio") good = !!form.querySelector('input[name="' + el.name + '"]:checked');
        else if (el.type === "email") good = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim());
        else good = el.value.trim() !== "";
        if (el.type !== "radio") el.setAttribute("aria-invalid", good ? "false" : "true");
        if (!good) ok = false;
      });
      if (error) error.hidden = ok;
      if (!ok) return;
      form.querySelectorAll(".field, button, .form-note").forEach(function (el) { el.hidden = true; });
      if (thanks) { thanks.hidden = false; thanks.focus(); }
    });
  });
})();
