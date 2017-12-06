import "es6-promise/auto";
import "unfetch/polyfill";
import { h, render } from "react-import";
// import { createElement as h } from "react";
// import { render } from "react-dom";
// import { initDevTools } from "zreact/dist/devtools";
import MainRouter from "./router";
// import BookLayout from "./book-layout";
import "animate.css";
import "./css/main.styl";
import "./css/base.css";
import "font-awesome/css/font-awesome.min.css";
// import "linearicons";

render(<MainRouter/>, document.getElementById("app"));
// initDevTools();
