'use-strict';

let activeModal = null;
let bottomHeightThreshold, sections;
let hamburgerToggle;
let mobileSearch;
let sidebar;
let toTop;

class Modal {
  constructor(element) {
    this.element = element;
  }

  close() {
    activeModal = null;
    this.element.style.display = 'none'
  }

  open() {
    if (activeModal) {
      activeModal.close();
    }
    activeModal = this;
    this.element.style.display = 'flex'
  }
}

class SearchBar {

  constructor() {
    this.box = document.querySelector('nav.mobile-only');
    this.bar = document.querySelector('nav.mobile-only input[type="search"]');
    this.openButton = document.getElementById('open-search');
    this.closeButton = document.getElementById('close-search');
  }

  open() {
    this.openButton.hidden = true;
    this.closeButton.hidden = false;
    this.box.style.top = "100%";
    this.bar.focus();
  }

  close() {
    this.openButton.hidden = false;
    this.closeButton.hidden = true;
    this.box.style.top = "0";
  }

}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

let showHideSidebar;

document.addEventListener('DOMContentLoaded', () => {
  mobileSearch = new SearchBar();

  bottomHeightThreshold = document.documentElement.scrollHeight - 30;
  sections = document.querySelectorAll('section');
  hamburgerToggle = document.getElementById('hamburger-toggle');

  toTop = document.getElementById('to-top');
  toTop.hidden = !(window.scrollY > 0);

  showHideSidebar = (e) => {
    sidebar.element.parentElement.classList.toggle('sidebar-toggle');
    let button = hamburgerToggle.firstElementChild;
    button.parentElement.classList.toggle("opened");
    if (button.textContent == 'menu') {
      button.textContent = 'close';
    }
    else {
      button.textContent = 'menu';
    }
  };

  if (hamburgerToggle) {
    hamburgerToggle.addEventListener('click', showHideSidebar);
    // close panel when clicking a jump link
    const jump_links = document.querySelectorAll("aside a.reference");
    jump_links.forEach(element => {
      element.addEventListener('click', showHideSidebar);
    });
    const extension_links = document.querySelectorAll("aside a.extension-nav");
    extension_links.forEach(element => {
      element.addEventListener('click', showHideSidebar);
    });
  }

  const tables = document.querySelectorAll('.py-attribute-table[data-move-to-id]');
  tables.forEach(table => {
    let element = document.getElementById(table.getAttribute('data-move-to-id'));
    let parent = element.parentNode;
    // insert ourselves after the element
    parent.insertBefore(table, element.nextSibling);
  });

  window.addEventListener('scroll', () => {
    toTop.hidden = !(window.scrollY > 0);
  });
});

document.addEventListener('keydown', (event) => {
  if (event.code == "Escape" && activeModal) {
    activeModal.close();
  }
});

$(document).ready(function () {
  $('a.external').attr('target', '_blank');
});

var url = new URL(window.location.href);

if (url.searchParams.has('q')) {
  query = url.searchParams.get('q')
  if (query.toLowerCase().includes('color')) {
    url.searchParams.set('q', query.replace('color', 'colour').replace('Color', 'Colour'));
    window.history.replaceState({}, document.title, url.toString());
  }
}
