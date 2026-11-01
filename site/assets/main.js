"use strict";

const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#navigation");
menuButton.hidden = false;
function closeMenu() {
  menuButton.setAttribute("aria-expanded", "false");
  navigation.classList.remove("is-open");
}
menuButton.addEventListener("click", () => {
  const isOpen = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!isOpen));
  navigation.classList.toggle("is-open", !isOpen);
});
navigation.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menuButton.getAttribute("aria-expanded") === "true") {
    closeMenu();
    menuButton.focus();
  }
});
document.addEventListener("click", (event) => {
  if (!event.target.closest(".header-inner")) closeMenu();
});
window.matchMedia("(min-width: 901px)").addEventListener("change", closeMenu);

const projectCards = [...document.querySelectorAll(".project-card")];
const filterButtons = [...document.querySelectorAll("[data-filter]")];
document.querySelector(".project-controls").hidden = false;
function filterProjects(filter) {
  let count = 0;
  for (const card of projectCards) {
    card.hidden = filter !== "all" && card.dataset.category !== filter;
    if (!card.hidden) count += 1;
  }
  for (const button of filterButtons) {
    button.setAttribute("aria-pressed", String(button.dataset.filter === filter));
  }
  document.querySelector("#project-count").textContent = `顯示 ${count} 件作品`;
}
filterButtons.forEach((button) => button.addEventListener("click", () => filterProjects(button.dataset.filter)));
// A direct project link must remain reachable even after a category was filtered out.
function revealHashProject() {
  const target = projectCards.find((card) => `#${card.id}` === window.location.hash);
  if (target?.hidden) {
    filterProjects("all");
    target.scrollIntoView();
  }
}
window.addEventListener("hashchange", revealHashProject);
revealHashProject();

const copyButton = document.querySelector("#copy-email");
const copyStatus = document.querySelector("#copy-status");
if (navigator.clipboard?.writeText) {
  copyButton.hidden = false;
  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText("leezr34@gmail.com");
      copyStatus.textContent = "Email 已複製，可以貼上使用。";
    } catch {
      copyStatus.textContent = "無法自動複製，請選取上方 Email 複製，或點擊開啟郵件。";
    }
  });
}
document.querySelector("#year").textContent = new Date().getFullYear();
