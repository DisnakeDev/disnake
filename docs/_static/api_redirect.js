'use-strict';

window.onload = main;

function main() {
    const url = new URL("https://docs.disnake.dev/en/latest/api.html"); // (window.location.href)

    if (!url.pathname.endsWith('api.html')) return; // Ensure we're on legacy api.html page

    let redirect_to = '';

    if (url.pathname.endsWith('ext/commands/api.html')) {
        redirect_to = get_ext_commands_api_link(url);
    } else {
        redirect_to = get_api_link(url);
    }
}

function get_api_link(url) {
    console.log(require('./searchindex.js'.Search));
}

function get_ext_commands_api_link(url) {
    console.log(require('./searchindex.js'.Search));
}