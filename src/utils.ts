export function addLinkCss(href, id) {
    const link = document.getElementById(id);
    if (link) {
        return;
    }
    const newlink = document.createElement("link");
    newlink.setAttribute("href", href);
    newlink.setAttribute("rel", "stylesheet");
    newlink.id = id;
    document.head.appendChild(newlink);
}

export function removeLinkCss(id) {
    const link = document.getElementById(id);
    if (link) {
        document.head.removeChild(link);
    }
}
