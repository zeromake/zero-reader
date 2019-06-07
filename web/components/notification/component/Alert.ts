import { prefix, NOTICE_TYPES, NAME_SPACE } from "../utils";
import Notification from "../core";
let alertInstance: {notice(p: any): void};
let defaultDuration = 2000;
let defaultTop = 5;
let defaultBottom;
let defaultClassPrefix = `${NAME_SPACE}-notification`;
let getContainer;
const addPrefix = (name) => prefix(defaultClassPrefix)(name);
function getInstance(instance) {
  const style = defaultTop ? { top: defaultTop } : { bottom: defaultBottom };
  return (
    instance ||
    Notification.newInstance({
      style,
      duration: defaultDuration,
      className: addPrefix("alert"),
      classPrefix: defaultClassPrefix,
      getContainer,
    })
  );
}

function getAlertConfig(config) {
    const cfg = {closable: true, ...config};
    if (cfg.duration == null) {
        cfg.duration = defaultDuration;
    }
    if (typeof cfg.content === "function") {
        cfg.content = cfg.content();
    }
    return cfg;
}

function notice(config) {
    alertInstance = getInstance(alertInstance);
    alertInstance.notice(getAlertConfig(config));
}

function levelAlert(type: string) {
    return function Alert_(content: any, duration?: number, onClose?: () => void, key?: string) {
        let config;
        if (typeof content === "object") {
            config = content;
            config.type = type;
        } else {
            config = {
                content,
                duration,
                onClose,
                type,
                key,
            };
        }
        return notice(config);
    };
}

export default {
    open: notice,
    success: levelAlert(NOTICE_TYPES.SUCCESS),
    error: levelAlert(NOTICE_TYPES.ERROR),
    info: levelAlert(NOTICE_TYPES.INFO),
    warning: levelAlert(NOTICE_TYPES.WARNING),
    config(options) {
        if (options.top !== undefined) {
            defaultTop = options.top;
            alertInstance = null;
        }
        if (options.bottom !== undefined) {
            defaultBottom = options.bottom;
            alertInstance = null;
        }
        if (options.duration !== undefined) {
            defaultDuration = options.duration;
        }
        if (options.classPrefix !== undefined) {
            defaultClassPrefix = options.classPrefix;
        }
        if (options.getContainer !== undefined) {
            getContainer = options.getContainer;
        }
    },
};
