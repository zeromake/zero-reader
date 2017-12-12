import "es6-promise/auto";
import "unfetch/polyfill";
import { h, render } from "react-import";
// import "./assets/lazyload.js";
// import { createElement as h } from "react";
// import { render } from "react-dom";
import "intersection-observer";
import MainRouter from "./router";
// import BookLayout from "./book-layout";
import "animate.css";
import "./css/main.styl";
import "./css/base.css";
import "font-awesome/css/font-awesome.min.css";
// import "linearicons";

declare const process: any;
declare const require: (modul: string) => any;

render(<MainRouter/>, document.getElementById("app"));
if (process.env.NODE_ENV !== "production") {
    const { initDevTools } = require("zreact/devtools");
    initDevTools();
}
