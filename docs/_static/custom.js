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


  const search_box = document.querySelector(".search input[type='search']");
  const updateSearchPlaceholder = function() {
    if (window.matchMedia && window.matchMedia('(max-width: 600px)').matches) {
      if (!search_box.classList.contains("mobile-search")) {
        search_box.classList.add("mobile-search");
        search_box.placeholder = search_box.getAttribute("placeholder-mobile");
      }
    } else {
      if (search_box.classList.contains("mobile-search")) {
        search_box.classList.remove("mobile-search");
        search_box.placeholder = search_box.getAttribute("placeholder-desktop");
      }
    }
  }
  // Alter search box text for small screen sizes to reduce clipping
  window.addEventListener("resize", updateSearchPlaceholder);
  updateSearchPlaceholder();


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
    const extension_links = document.querySelectorAll("aside a.extension-nav[href='#']");
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


  // dark mode toggle

  var dark_mode_rule;
  for (const sheet of document.styleSheets) {
    if (sheet.href && !sheet.href.endsWith("style.css")) {
      continue;
    }
    for (const rule of sheet.cssRules) {
      if (rule.type == CSSRule.MEDIA_RULE) {
        if (rule.media.mediaText.includes("prefers-color-scheme: dark")) {
           dark_mode_rule = rule;
        }
      }
    }
  }

  function toggleDarkMode(on) {
    // set data-theme to control code blocks
    if (on) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
    }

    localStorage.setItem("dark-mode", on);

    // edit media query to manually override prefers-color-scheme
    if (on) {
      dark_mode_rule.media.mediaText = "screen";
    } else {
      dark_mode_rule.media.mediaText = "screen and disabled";
    }
  }

  function switchToggle(event) {
    let switchToggle = document.querySelector("#dark-mode-switch");
    let knob = document.querySelector("#dark-mode-switch .knob");

    if (knob.classList.contains("dark")) {
      knob.classList.remove("dark");
      knob.classList.add("light");

      toggleDarkMode(false);

      // After 100ms, switch the icons
      setTimeout(function() {
        switchToggle.classList.remove("dark");
        switchToggle.classList.add("light");
      }, 100);
    } else {
      knob.classList.remove("light");
      knob.classList.add("dark");

      toggleDarkMode(true);

      // After 100ms, switch the icons
      setTimeout(function() {
        switchToggle.classList.remove("light");
        switchToggle.classList.add("dark");
      }, 100);
    }
  }

  document.getElementById("dark-mode-switch").addEventListener('click', switchToggle);

  // Set toggle state and default color scheme according to local storage and user preferences
  let toggle_set = JSON.parse(localStorage.getItem("dark-mode"));
  var color_scheme = "light";
  console.log("Loading dark mode setting:", toggle_set);
  if (toggle_set === null) {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      color_scheme = "dark";
    } else {
      color_scheme = "light";
    }
    document.documentElement.setAttribute('data-theme', color_scheme);
  } else {
    if (toggle_set) {
      color_scheme = "dark";
      toggleDarkMode(true);
    } else {
      color_scheme = "light";
      toggleDarkMode(false);
    }
  }
  document.getElementById("dark-mode-switch").classList.add(color_scheme);
  document.querySelector("#dark-mode-switch .knob").classList.add(color_scheme);
});


function focusSearch() {
  $('input[name=q]').first().focus();
}


function unfocusSearch() {
  $('input[name=q]').first().blur();
}


$(document).keydown((event) => {
  if (event.altKey || event.metaKey)
    return;

  const focusedElement = document.activeElement;
  if (["TEXTAREA", "INPUT", "SELECT", "BUTTON"].includes(focusedElement.tagName)) {
    // handle `escape` in search field
    if (!event.ctrlKey && !event.shiftKey && event.key === "Escape" && $('input[name=q]').first().is(focusedElement)) {
      unfocusSearch();
      return false;
    }
    // otherwise, ignore all key presses in inputs
    return;
  }

  if (!event.ctrlKey) {
    // close modal using `escape`, if modal exists
    if (!event.shiftKey && event.key === "Escape" && activeModal) {
      activeModal.close();
      return false;
    }

    // focus search using `/` or `s`
    // (not checking `shiftKey` for `/` since some keyboards need it)
    if (event.key === "/" || (!event.shiftKey && event.key === "s")) {
      focusSearch();
      return false;
    }
  }

  // focus search using `ctrl+k`
  if (!event.shiftKey && event.ctrlKey && event.key == "k") {
    focusSearch();
    return false;
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
