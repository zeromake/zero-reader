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

export function removeHead(id) {
    const link = document.getElementById(id);
    if (link) {
        document.head.removeChild(link);
    }
}

export function addStyle(id: string, css: string) {
    const style = document.getElementById(id);
    if (style) {
        style.innerHTML = css;
        return;
    }
    const newstyle = document.createElement("style");
    newstyle.setAttribute("type", "text/css");
    newstyle.id = id;
    newstyle.innerHTML = css;
    document.head.appendChild(newstyle);
}
