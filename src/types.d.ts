declare module "*.styl" {
    const style: {
        [name: string]: string;
    };
    export default style;
}

declare module "*.json" {
    const json: {
        [name: string]: any;
    }
    export default json;
}

declare module "zreact-router" {
    export const Router: any;
    export const Link: any;
    export const Route: any;
    export const route: (url: string, replace?: boolean) => boolean;
    export const getCurrentUrl: () => string;
    export const customHistory: any;
    export const Match: any;
    export const AsyncRoute: any;
    export default Router;
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
    import { h, render, Component, findDOMNode, cloneElement, Children, unmountComponentAtNode } from "zreact";
    export {
        h,
        Component,
        findDOMNode,
        cloneElement,
        Children,
        render,
        unmountComponentAtNode,
    };
}

declare module "react-import" {
    import { h, render, Component, findDOMNode, cloneElement, Children } from "zreact";
    import Router, { Route, Link, route, getCurrentUrl, customHistory, AsyncRoute } from "zreact-router";
    // const customHistory: any;
    // const AsyncRoute: any;

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
        AsyncRoute,
        getCurrentUrl,
        customHistory,
    };
}

declare module "better-scroll" {
    import BScroll from "better-scroll/index";
    export default BScroll;
}

declare module "rsuite-notification" {
    const alert: any;
    export const Alert: any;
    export default alert;
}

declare module "hotkeys-js" {
    const hotkeys: any;
    export default hotkeys;
}

declare module "history/createHashHistory" {
    const History: any;
    export default History;
}

declare module "material-ui/Button" {
    const Button: any;
    export default Button;
}

declare const process: any;

declare const require: (name: string) => { default: any };

declare module "sweetalert2" {
    const swal: any;
    export default swal;
}

declare module "qs" {
    const qs: any;
    export default qs;
}
