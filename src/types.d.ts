declare module "*.styl" {
    const style: {
        [name: string]: string;
    };
    export default style;
}
declare module "preact-router" {
    const style: any;
    export const Link: any;
    export const Route: any;
    export const route: (url: string, replace?: boolean) => boolean;
    export const getCurrentUrl: () => string;
    export default style;
}
declare module "preact-animate" {
    const Animate: any;
    export default Animate;
}
declare module "lodash.throttle" {
    import { throttle } from "lodash";
    export default throttle;
}

declare module "screenfull" {
    const screenfull: any;
    export default screenfull;
}

declare module "preact" {
    import * as zreact from "zreact";
    export = zreact;
}

declare module "module-react" {
    import { h, render, Component, findDOMNode, cloneElement, Children } from "zreact";
    export {
        h,
        Component,
        findDOMNode,
        cloneElement,
        Children,
        render,
    };
}

declare module "react-import" {
    // import { createElement as h, Component } from "react";
    // import { render, findDOMNode } from "react-dom";
    // import { BrowserRouter as Router, Route, Link } from "react-router-dom";
    
    // export {
    //     h,
    //     Component,
    //     findDOMNode,
    //     render,
    //     Router,
    //     Route,
    //     Link,
    // };
    import { h, render, Component, findDOMNode, cloneElement, Children } from "zreact";
    import Router, { Route, Link, route, getCurrentUrl } from "preact-router";
    export {
        h,
        Component,
        findDOMNode,
        cloneElement,
        Children,
        render,
        Router,
        Route,
        route,
        Link,
        getCurrentUrl,
    };
}

declare module "better-scroll" {
    import BScroll from "better-scroll/index";
    export default BScroll;
}

declare module "hotkeys-js" {
    const hotkeys: any;
    export default hotkeys;
}

declare const process: any;

declare const require: (name: string) => { default: any };
