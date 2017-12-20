import { cloneElement, h, Component } from "zreact";
import { exec, prepareVNodeForRanking, assign, pathRankSort } from "./utils";

let customHistory = null;

const ROUTERS = [];

const subscribers = [];

const EMPTY = {};

function isPreactElement(node) {
    return node.__preactattr_ != null || typeof Symbol !== "undefined" && node[Symbol.for("preactattr")] != null;
}

function setUrl(url, type = "push") {
    if (customHistory && customHistory[type]) {
        customHistory[type](url);
    } else if (typeof history !== "undefined" && history[type + "State"]) {
        history[type + "State"](null, null, url);
    }
}

function getCurrentUrl() {
    let url;
    if (customHistory && customHistory.location) {
        url = customHistory.location;
    } else if (customHistory && customHistory.getCurrentLocation) {
        url = customHistory.getCurrentLocation();
    } else {
        url = typeof location !== "undefined" ? location : EMPTY;
    }
    return `${url.pathname || ""}${url.search || ""}`;
}

function route(url, replace = false) {
    if (typeof url !== "string" && url.url) {
        replace = url.replace;
        url = url.url;
    }

    // only push URL into history if we can handle it
    if (canRoute(url)) {
        setUrl(url, replace ? "replace" : "push");
    }

    return routeTo(url);
}

/** Check if the given URL can be handled by any router instances. */
function canRoute(url) {
    for (let i = ROUTERS.length; i--; ) {
        if (ROUTERS[i].canRoute(url)) {
            return true;
        }
    }
    return false;
}

/** Tell all router instances to handle the given URL.  */
function routeTo(url) {
    let didRoute = false;
    for (const router of ROUTERS) {
        if (router.routeTo(url) === true) {
            didRoute = true;
        }
    }
    for (let i = subscribers.length; i--; ) {
        subscribers[i](url);
    }
    return didRoute;
}

function routeFromLink(node) {
    // only valid elements
    if (!node || !node.getAttribute) {
        return;
    }

    const href = node.getAttribute("href");
    const target = node.getAttribute("target");

    // ignore links with targets and non-path URLs
    if (!href || !href.match(/^\//g) || (target && !target.match(/^_?self$/i))) {
        return;
    }

    // attempt to route, if no match simply cede control to browser
    return route(href);
}

function handleLinkClick(e) {
    if (e.button === 0) {
        routeFromLink(e.currentTarget || e.target || this);
        return prevent(e);
    }
}

function prevent(e) {
    if (e) {
        if (e.stopImmediatePropagation) {
            e.stopImmediatePropagation();
        }
        if (e.stopPropagation) {
            e.stopPropagation();
        }
        e.preventDefault();
    }
    return false;
}

function delegateLinkHandler(e) {
    // ignore events the browser takes care of already:
    if (e.ctrlKey || e.metaKey || e.altKey || e.shiftKey || e.button !== 0) {
        return;
    }

    let t = e.target;
    do {
        if (String(t.nodeName).toUpperCase() === "A" && t.getAttribute("href") && isPreactElement(t)) {
            if (t.hasAttribute("native")) {
                return;
            }
            // if link is handled by the router, prevent browser defaults
            if (routeFromLink(t)) {
                return prevent(e);
            }
        }
        t = t.parentNode;
    } while (t);
}

let eventListenersInitialized = false;

function initEventListeners() {
    if (eventListenersInitialized) {
        return;
    }

    if (typeof addEventListener === "function") {
        if (!customHistory) {
            addEventListener("popstate", () => {
                routeTo(getCurrentUrl());
            });
        }
        addEventListener("click", delegateLinkHandler);
    }
    eventListenersInitialized = true;
}

const Link = (props) => (
    h("a", assign({ onClick: handleLinkClick }, props))
);

const Route = (props: any) => h(props.component, props);

class Router extends Component<any, any> {
    public updating: boolean;

    private _didRoute: boolean;
    private unlisten: any;
    private previousUrl: string;

    public static subscribers = subscribers;
    public static getCurrentUrl = getCurrentUrl;
    public static route = route;
    public static Router = Router;
    public static Route = Route;
    public static Link = Link;

    constructor(props) {
        super(props);
        if (props.history) {
            customHistory = props.history;
        }

        this.state = {
            url: props.url || getCurrentUrl(),
        };

        initEventListeners();
    }
    public shouldComponentUpdate(props) {
        if (props.static !== true) {
            return true;
        }
        return props.url !== this.props.url || props.onChange !== this.props.onChange;
    }

    /** Check if the given URL can be matched against any children */
    private canRoute(url) {
        return this.handleChildren(this.props.children, url, false).length > 0;
    }

    /** Re-render children with a new URL to match against. */
    public routeTo(url) {
        this._didRoute = false;
        this.setState({ url });

        // if we"re in the middle of an update, don"t synchronously re-route.
        if (this.updating) {
            return this.canRoute(url);
        }

        this.forceUpdate();
        return this._didRoute;
    }

    public componentWillMount() {
        ROUTERS.push(this);
        this.updating = true;
    }

    public componentDidMount() {
        if (customHistory) {
            this.unlisten = customHistory.listen((location) => {
                this.routeTo(`${location.pathname || ""}${location.search || ""}`);
            });
        }
        this.updating = false;
    }

    public componentWillUnmount() {
        if (typeof this.unlisten === "function") {
            this.unlisten();
        }
        ROUTERS.splice(ROUTERS.indexOf(this), 1);
    }

    public componentWillUpdate() {
        this.updating = true;
    }

    public componentDidUpdate() {
        this.updating = false;
    }

    public handleChildren(children, url, invoke) {
        const newChildren: any[] = [];
        if (children == null) {
            return newChildren;
        }
        for (let vnode of children) {
            if (vnode.nodeName === Route) {
                return this.getMatchingChildren(children, url, invoke);
            } else {
                if (vnode.children && vnode.children.length > 0) {
                    vnode = cloneElement(
                        vnode,
                        {},
                        this.handleChildren(vnode.children, url, invoke),
                    );
                }
                if (vnode) {
                    newChildren.push(vnode);
                }
            }
        }
        return newChildren;
    }

    public getMatchingChildren(children, url, invoke) {
        return children
            .filter(prepareVNodeForRanking)
            .sort(pathRankSort)
            .map((vnode) => {
                const matches = exec(url, vnode.attributes.path, vnode.attributes);
                if (matches) {
                    if (invoke !== false) {
                        const newProps = { url, matches };
                        assign(newProps, matches);
                        delete (newProps as any).ref;
                        delete (newProps as any).key;
                        return cloneElement(vnode, newProps);
                    }
                    return vnode;
                }
            }).filter(Boolean);
    }

    public render({ children, onChange }, { url }) {
        const active = this.handleChildren(children, url, true);

        const current = active[0] || null;
        this._didRoute = !!current;

        const previous = this.previousUrl;
        if (url !== previous) {
            this.previousUrl = url;
            if (typeof onChange === "function") {
                onChange({
                    router: this,
                    url,
                    previous,
                    active,
                    current,
                });
            }
        }

        return current;
    }
}

export { subscribers, getCurrentUrl, route, Router, Route, Link };
export default Router;
