import { h, render, Component } from "preact";
import Router, { Route, Link, route } from "../assets/router/index";

function findDOMNode(componentOrVdom: any): Element {
    return componentOrVdom && componentOrVdom.base;
}

export {
    h,
    Component,
    findDOMNode,
    render,
    Router,
    Route,
    route,
    Link,
};
