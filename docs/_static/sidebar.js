// SPDX-License-Identifier: MIT

class Sidebar {
  constructor(element) {
    this.element = element;
    this.activeLink = null;

    this.element.addEventListener('click', (e) => {
      // If we click a navigation, close the hamburger menu
      if (e.target.tagName == 'A' && this.element.classList.contains('sidebar-toggle')) {
        this.element.classList.remove('sidebar-toggle');
        let button = hamburgerToggle.firstElementChild;
        button.textContent = 'menu';

        // Scroll a little up to actually see the header
        // Note: this is generally around ~55px
        // A proper solution is getComputedStyle but it can be slow
        // Instead let's just rely on this quirk and call it a day
        // This has to be done after the browser actually processes
        // the section movement
        setTimeout(() => window.scrollBy(0, -100), 75);
      }
    });
  }

  createCollapsableSections() {
    let toc = this.element.querySelector('ul');
    if (!toc) {
      return
    }
    let allReferences = toc.querySelectorAll('a.reference.internal:not([href="#"])');

    for (let ref of allReferences) {

      let next = ref.nextElementSibling;

      if (next && next.tagName === "UL") {
        let icon = document.createElement('span');
        icon.className = 'material-icons collapsible-arrow expanded';
        icon.innerText = 'expand_more';

        if (next.parentElement.tagName == "LI") {
          next.parentElement.classList.add('no-list-style')
        }

        icon.addEventListener('click', () => {
          if (icon.classList.contains('expanded')) {
            this.collapseSection(icon);
          } else {
            this.expandSection(icon);
          }
        })

        ref.classList.add('ref-internal-padding')
        ref.parentNode.insertBefore(icon, ref);

        // collapse all top-level toc entries, except the current page's
        // (i.e. all entries that don't contain a `#`)
        const refUrl = new URL(ref.href);
        if (!refUrl.hash) {
          // `false` to update immediately
          this.collapseSection(icon, false);
        }
      }
    }
  }

  collapseSection(icon, defer = true) {
    icon.classList.remove('expanded');
    icon.classList.add('collapsed');
    let children = icon.nextElementSibling.nextElementSibling;
    // <arrow><heading>
    // --> <square><children>
    const update = () => children.style.display = "none";
    if (defer) setTimeout(update, 75);
    else update();
  }

  expandSection(icon, defer = true) {
    icon.classList.remove('collapse');
    icon.classList.add('expanded');
    let children = icon.nextElementSibling.nextElementSibling;
    const update = () => children.style.display = "block";
    if (defer) setTimeout(update, 75);
    else update();
  }

  setActiveLink(section) {
    if (this.activeLink) {
      this.activeLink.parentElement.classList.remove('active');
    }
    if (section) {
      this.activeLink = document.querySelector(`#sidebar a[href="#${section.id}"]`);
      if (this.activeLink) {
        let headingChildren = this.activeLink.parentElement.parentElement;
        let heading = headingChildren.previousElementSibling.previousElementSibling;

        if (heading && headingChildren.style.display === 'none') {
          this.activeLink = heading;
        }
        this.activeLink.parentElement.classList.add('active');
      }
    }
  }

  scrollToCurrent() {
    const currentSection = this.element.querySelector("li.current");
    if (currentSection) {
      // setTimeout(..., 0) to avoid layout race condition
      setTimeout(() => currentSection.scrollIntoView({block: "center"}), 0);
    }
  }
}

function getCurrentSection() {
  let currentSection;
  if (window.scrollY + window.innerHeight > bottomHeightThreshold) {
    currentSection = sections[sections.length - 1];
  }
  else {
    if (sections) {
      const headerOffset = document.querySelector("main").offsetTop;  // height of header
      sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        // plus offset for more leniency
        // (section doesn't have to be scrolled all the way to the top to be considered active)
        if (rect.top < headerOffset + 50) {
          currentSection = section;
        }
      });
    }
  }
  return currentSection;
}

// create interactive sidebar
document.addEventListener('DOMContentLoaded', () => {
  sidebar = new Sidebar(document.getElementById('sidebar'));
  sidebar.createCollapsableSections();
  sidebar.scrollToCurrent();

  window.addEventListener('scroll', () => {
    sidebar.setActiveLink(getCurrentSection());
  });
});

function sidebarSearch() {
  const filter = document.getElementById('sidebar-search-box').value.toUpperCase();
  const items = document.querySelectorAll('#sidebar li')

  // Loop through all list items, and hide those who don't match the search query
  for (const item of items) {
    const a = item.querySelector("a");
    const itemText = a.textContent || a.innerText;
    if (itemText.toUpperCase().indexOf(filter) > -1) {
      // we need to convert all of the parents back into visible mode
      let el = item;
      while (el) {
        el.style.display = "";
        el = el.parentNode.closest("#sidebar li");
      }
    } else {
      item.style.display = "none";
    }
  }
}
