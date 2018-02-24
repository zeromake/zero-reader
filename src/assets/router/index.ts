import { cloneElement, h, Component, Children } from "module-react";
import {
    exec,
    assign,
    pathRankSort,
    findProps,
    rankChild,
    findChildren,
    isRoute,
    findChildRoute,
} from "./utils";

let customHistory = null;

const ROUTERS = [];

const subscribers = [];

let beforeEach: ((to: string, form: string, next: () => void) => void) | null = null;

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
function _route(url, replace) {
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
function route(url, replace = false) {
    return new Promise<boolean>(function _(resolve) {
        const next = (newUrl?: string, newReplace?: boolean) => {
            let temp: boolean;
            if (newUrl) {
                temp = _route(newUrl, newReplace);
            } else {
                temp = _route(url, replace);
            }
            resolve(temp);
            return temp;
        };
        if (beforeEach) {
            beforeEach(url, getCurrentUrl(), next);
        }
    });
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

async function delegateLinkHandler(e) {
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
            const temp: boolean = await routeFromLink(t);
            if (temp) {
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
    private initRoute: boolean;

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
        this.initRoute = true;
        this.state = {
            url: props.url || getCurrentUrl(),
        };

        initEventListeners();
        if (props.beforeEach) {
            beforeEach = props.beforeEach;
        }
        this._componentWillMount();
    }
    public shouldComponentUpdate(props) {
        if (props.static !== true) {
            return true;
        }
        return props.url !== this.props.url || props.onChange !== this.props.onChange;
    }

    /** Check if the given URL can be matched against any children */
    private canRoute(url) {
        return this.handleChildren(
            Children.toArray(this.props.children),
            url,
            false,
        ).length > 0;
    }

    /** Re-render children with a new URL to match against. */
    public routeTo(url) {
        this._didRoute = false;
        if (this.initRoute) {
            this.state.url = url;
        } else {
            this.setState({ url });
        }

        // if we"re in the middle of an update, don"t synchronously re-route.
        if (this.updating) {
            return this.canRoute(url);
        }
        if (!this.initRoute) {
            this.forceUpdate();
        }
        return this._didRoute;
    }

    public _componentWillMount() {
        ROUTERS.push(this);
        this.updating = true;
        if (this.props.beforeEach) {
            this.props.beforeEach(this.state.url, this.state.url, (newUrl: string) => {
                if (newUrl) {
                    _route(newUrl, false);
                }
            });
        }
    }

    public componentDidMount() {
        if (customHistory) {
            this.unlisten = customHistory.listen((location) => {
                const url: string = `${location.pathname || ""}${location.search || ""}`;
                this.routeTo(url);
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

    public handleChildren(children: any[], url: string, invoke: boolean, parentPath?: string): any[] {
        let newChildren: any[] = [];
        let isNoRank = false;
        if (children == null) {
            return newChildren;
        }
        for (let vnode of children) {
            if (isRoute(vnode)) {
                newChildren = this.getMatchingChildren(children, url, invoke, isNoRank, parentPath);
                break;
            } else {
                isNoRank = true;
                const vnodeChildren = findChildren(vnode);
                if (vnodeChildren && vnodeChildren.length > 0) {
                    if (!invoke) {
                        newChildren = newChildren.concat(this.handleChildren(vnodeChildren, url, invoke));
                    } else {
                        vnode = cloneElement(
                            vnode,
                            {},
                            this.handleChildren(vnodeChildren, url, invoke),
                        );
                    }
                }
                if (vnode && invoke) {
                    newChildren.push(vnode);
                }
            }
        }
        return newChildren;
    }

    public getMatchingChildren(children: any[], url: string, invoke: boolean, isNoRank: boolean = false, parentPath?: string): any[] {
        const rankArr = [];
        // let isNoRank = false;
        if (!isNoRank) {
            let index = 0;
            for (const vnode of children) {
                if (isRoute(vnode)) {
                    const props = findProps(vnode);
                    if (props) {
                        let newVnode = vnode;
                        const deepChildren = Children.toArray(findChildren(vnode));
                        if (deepChildren && deepChildren.length > 0) {
                            newVnode = cloneElement(
                                vnode,
                                {},
                                this.handleChildren(deepChildren, url, invoke, props.path),
                            );
                        }
                        rankArr.push({ index, rank: rankChild(newVnode), vnode: newVnode });
                    }
                } else {
                    isNoRank = true;
                    break;
                }
                index += 1;
            }
        }
        const rankChildren = [];
        const execRoute = (vnode) => {
            const props = findProps(vnode);
            let path = props.path;
            if (parentPath && !path.startsWith(parentPath)) {
                path = parentPath + (parentPath.endsWith("/") || path.startsWith("/")) ? "" : "/" + path;
            }
            const deepChildren = Children.toArray(findChildren(vnode));
            const childRoute = findChildRoute(deepChildren[0]);
            if (childRoute) {
                const matches = childRoute.matches;
                if (invoke !== false) {
                    const newProps = { url, matches, history: customHistory };
                    assign(newProps, matches);
                    delete (newProps as any).ref;
                    delete (newProps as any).key;
                    rankChildren.push(cloneElement(vnode, newProps));
                } else {
                    rankChildren.push(vnode);
                }
            } else {
                const matches = exec(url, path, props);
                if (matches) {
                    if (invoke !== false) {
                        const newProps = { url, matches, history: customHistory };
                        assign(newProps, matches);
                        delete (newProps as any).ref;
                        delete (newProps as any).key;
                        rankChildren.push(cloneElement(vnode, newProps));
                    } else {
                        rankChildren.push(vnode);
                    }
                }
            }
        };
        if (isNoRank) {
            for (const vnode of children) {
                if (isRoute(vnode)) {
                    execRoute(vnode);
                } else if (vnode && invoke) {
                    rankChildren.push(vnode);
                }
                }
        } else {
            rankArr.sort(pathRankSort).forEach(({ vnode }) => execRoute(vnode));
        }
        return rankChildren;
        // children.forEach((vnode, index) => {
        //     const props = findProps(vnode);
        //     if (props) {
        //         rankArr.push({ index, rank: rankChild(vnode), vnode });
        //     }
        // });
    }

    public render() {
        const { url } = this.state;
        const { children, onChange } = this.props;
        const active = this.handleChildren(Children.toArray(children), url, true);

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

// function getCustomHistory() {
//     return customHistory;
// }

export { subscribers, getCurrentUrl, route, Router, Route, Link, customHistory };
export default Router;
