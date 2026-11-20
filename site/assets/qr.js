// Keeps the screen on while the QR code is shown (Screen Wake Lock API).
// Browsers without support simply ignore this.
(function () {
  if (!("wakeLock" in navigator)) return;

  function acquire() {
    if (document.visibilityState !== "visible") return;
    navigator.wakeLock.request("screen").catch(function () {});
  }

  // The lock is released when the tab is hidden; take it again on return.
  document.addEventListener("visibilitychange", acquire);
  acquire();
})();
