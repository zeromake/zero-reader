import { createElement as h } from "react";
import { prefix, NOTICE_TYPES, PLACEMENT_TYPES, NAME_SPACE } from "../utils";

import Notification from "../core";

const defaultPlacement = "topRight";
let defaultTop = 24;
let defaultBottom = 24;
let defaultDuration = 4500;
let notityInstance = {};
let defaultClassPrefix = `${NAME_SPACE}-notification`;
let getContainer;

const addPrefix = (name: string) => prefix(defaultClassPrefix)(name);

interface IConfig {
    placement?: string;
    top?: number;
    bottom?: number;
    description: any|(() => any);
    duration?: number;
    onClose?: () => void;
    key?: string;
    type?: string;
    title?: string;
    classPrefix?: string;
    getContainer?: () => Element;
}

function getPlacementStyle(config: IConfig) {
    let style = {};
    let className: string;
    const placement = config.placement || defaultPlacement;
    const top = config.top || defaultTop;
    const bottom = config.bottom || defaultBottom;

    switch (placement) {
    case PLACEMENT_TYPES.TOPLEFT:
        style = {
        top,
        left: 24,
        };
        className = addPrefix("top-left");
        break;
    case PLACEMENT_TYPES.TOPRIGHT:
        style = {
            top,
            right: 24,
        };
        className = addPrefix("top-right");
        break;
    case PLACEMENT_TYPES.BOTTOMLEFT:
        style = {
            bottom,
            left: 24,
        };
        className = addPrefix("bottom-left");
        break;
    case PLACEMENT_TYPES.BOTTOMRIGHT:
        style = {
            bottom,
            right: 24,
        };
        className = addPrefix("bottom-right");
        break;
    default:
        style = {
            top,
            left: 24,
        };
        break;
    }
    return { style, className };
}

function getInstance(config: IConfig) {
    const placement = config.placement || defaultPlacement;
    if (!notityInstance[placement]) {
        const temp = getPlacementStyle(config);
        const className = [addPrefix("notify"), temp.className].join(" ");
        notityInstance[placement] = Notification.newInstance({
            style: temp.style,
            className,
            classPrefix: defaultClassPrefix,
            getContainer,
        });
    }
    return notityInstance[placement];
}

/**
 *
 * @param {*} config: {} : title,description,style,duration,placement,top, bottom, onClose,type, key
 */
function notice(config: IConfig) {
    let duration;
    let description = config.description;
    if (typeof description === "function") {
        description = description();
    }
    if (config.duration == null) {
        duration = defaultDuration;
    } else {
        duration = config.duration;
    }

    const content = (
        <div className={addPrefix("content")}>
            <div className={addPrefix("title")}>{config.title}</div>
            <div className={addPrefix("description")}>{description}</div>
        </div>
    );
    const instance = getInstance(config);
    instance.notice({
        content,
        duration,
        closable: true,
        onClose: config.onClose,
        key: config.key,
        type: config.type,
        ...config,
    });
}

function wrapper(type: string) {
    return (config: IConfig) => {
        config.type = type;
        notice(config);
    };
}

export default {
    open: notice,
    success: wrapper(NOTICE_TYPES.SUCCESS),
    error: wrapper(NOTICE_TYPES.SUCCESS),
    info: wrapper(NOTICE_TYPES.SUCCESS),
    warning: wrapper(NOTICE_TYPES.SUCCESS),
    remove: wrapper(NOTICE_TYPES.SUCCESS),
    /**
     * 全局配置方法
     * @param {*} options{
     *  top,
     *  bottom,
     *  classPrefix,
     *  duration,
     *  getContainer
     * }
     */
    config(options: IConfig) {
        if (options.top != null) {
            defaultTop = options.top;
            // 如果存在实例，在设置新的top值后，需要将实例置空
            notityInstance = {};
        }
        if (options.bottom != null) {
            defaultBottom = options.bottom;
            notityInstance = {};
        }
        if (options.duration != null) {
            defaultDuration = options.duration;
        }
        if (options.classPrefix != null) {
            defaultClassPrefix = options.classPrefix;
        }
        if (options.getContainer != null) {
            getContainer = options.getContainer;
        }
    },
};
