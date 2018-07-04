import "es6-promise/auto";
import "unfetch/polyfill";
import { h, render } from "react-import";
import "intersection-observer";
import "animate.css";
import "./css/main.styl";
import "./css/base.css";
import "./components/notification/index.less";
import "./assets/icons/index";
import { initDevTools } from "zreact/devtools";
import MainRouter from "./router";
function zero_render(vdom: JSX.Element, dom: Element) {
    const root = dom.parentElement;
    return render(vdom, root, dom);
}

zero_render(<MainRouter/>, document.getElementById("app"));

if (process.env.NODE_ENV !== "production" && initDevTools) {
    initDevTools();
}

declare const process: any;
