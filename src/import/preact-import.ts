import { h, render, Component } from "preact";
import Router, { Route, Link } from "preact-router";

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
    Link,
};
