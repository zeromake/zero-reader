import { h, render, Component, cloneElement } from "preact";

function findDOMNode(componentOrVdom: any): Element {
    return componentOrVdom && componentOrVdom.base;
}
const arrayMap = Array.prototype.map;
const arrayForEach = Array.prototype.forEach;
const arraySlice = Array.prototype.slice;

type Child = any[];

const Children = {
    map(children: Child, callback: any, ctx?: any) {
        if (children == null) {
            return null;
        }
        if (ctx && ctx !== children) {
            callback = callback.bind(ctx);
        }
        return arrayMap.call(children, callback);
    },
    forEach(children: Child, callback: any, ctx?: any) {
        if (children == null) {
            return null;
        }
        if (ctx && ctx !== children) {
            callback = callback.bind(ctx);
        }
        return arrayForEach.call(children, callback);
    },
    count(children: Child) {
        return children && children.length || 0;
    },
    only(children: Child) {
        if (!children || children.length !== 1) {
            throw new TypeError("Children.only() expects only one child.");
        }
        return children[0];
    },
    toArray(children: Child) {
        if (children == null) {
            return [];
        }
        return arraySlice.call(children);
    },
};
export {
    h,
    Component,
    findDOMNode,
    render,
    cloneElement,
    Children,
};