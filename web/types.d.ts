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
    export const DRouter: any;
    export const Link: any;
    export const Route: any;
    // export const navigate: (to, opt?: {state?: any; replace?: boolean; }) => void;
    export const Redirect: any;
    export const LocationProvider:any;
    export const Location: any;
    export const globalHistory: any;
}

declare module "hash-source" {
    const createHashSource: () => any;
    export default createHashSource;
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
    import { DRouter, Route, Link, Redirect, LocationProvider, Location } from "zreact-router";
    // const customHistory: any;
    // const AsyncRoute: any;

    export {
        h,
        Component,
        findDOMNode,
        cloneElement,
        Children,
        render,
        DRouter as Router,
        Route,
        Link,
        Redirect,
        LocationProvider,
        Location,
    };
}

declare module "better-scroll" {
    import * as BScroll from "better-scroll";
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

declare module "router-history" {
    export const history: any;
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

declare module "fscreen" {
    const fscreen : {
        fullscreenEnabled: boolean,
        fullscreenElement?: Element,
        requestFullscreen: (e: Element) => void;
        exitFullscreen: () => void;
    };
    export default fscreen;
}
declare module "@zeromake/zreact" {
    export const createElement: any;
    export const Component: any;
    export const findDOMNode: any;
    export const render: any;
    export const cloneElement: any;
    export const Children: any;
    export const unmountComponentAtNode: any;
}
