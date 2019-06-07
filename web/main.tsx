import "es6-promise/auto";
import "unfetch/polyfill";
import { createElement as h } from "react";
import { render } from "react-dom";
import "intersection-observer";
import "animate.css";
import "./css/main.styl";
import "./css/base.css";
import "./components/notification/index.less";
import "./assets/icons/index";
import MainRouter from "./router";
import "preact/debug";
// function zero_render(vdom: JSX.Element, dom: Element) {
//     const root = dom.parentElement;
//     return render(vdom, root, dom);
// }

render(<MainRouter/>, document.getElementById("app"));

declare const process: any;
