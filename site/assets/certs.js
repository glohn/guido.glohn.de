// Turns "Expires <date>" into "Expired <date>" once the date is reached,
// so the page never shows an expired certification as valid.
// Without JavaScript the static text from the HTML is shown.
(function () {
  var today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  var entries = document.querySelectorAll(".certs .valid");

  for (var i = 0; i < entries.length; i++) {
    var time = entries[i].querySelector("time[datetime]");
    if (!time || time.getAttribute("datetime") > today) continue;

    entries[i].firstChild.nodeValue = "Expired ";
    entries[i].classList.remove("valid");
  }
})();
