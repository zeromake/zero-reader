import { h, render, Component, cloneElement } from "preact";

function findDOMNode(componentOrVdom: any): Element {
    return componentOrVdom && componentOrVdom.base;
}
export {
    h,
    Component,
    findDOMNode,
    render,
    cloneElement,
};