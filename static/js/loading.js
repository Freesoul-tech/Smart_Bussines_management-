(function () {
  const screen = document.getElementById("loading-screen");
  const message = document.getElementById("loading-message");
  const retryButton = document.getElementById("loading-retry");

  if (!screen || !message || !retryButton) {
    return;
  }

  function hideLoading() {
    screen.classList.add("is-hidden");
  }

  function showOfflineState() {
    screen.classList.remove("is-hidden");
    message.textContent =
      "We cannot reach the server right now. Check your connection and try again.";
    retryButton.hidden = false;
  }

  function showReadyState() {
    message.textContent = "Preparing your workspace...";
    retryButton.hidden = true;
    hideLoading();
  }

  window.addEventListener("load", function () {
    if (navigator.onLine === false) {
      showOfflineState();
      return;
    }
    showReadyState();
  });

  window.addEventListener("offline", showOfflineState);
  window.addEventListener("online", showReadyState);
  retryButton.addEventListener("click", function () {
    window.location.reload();
  });
})();
