import { prefix, NOTICE_TYPES, NAME_SPACE } from "../utils";
import Notification from "../core";
let alertInstance: {notice(p: any): void};
let defaultDuration = 2000;
let defaultTop = 5;
let defaultClassPrefix = `${NAME_SPACE}-notification`;
let getContainer;
const addPrefix = (name) => prefix(defaultClassPrefix)(name);
function getInstance(instance) {
  return (
    instance ||
    Notification.newInstance({
      style: { top: defaultTop },
      duration: defaultDuration,
      className: addPrefix("alert"),
      classPrefix: defaultClassPrefix,
      getContainer,
    })
  );
}
function notice(content: any, duration: number = defaultDuration, onClose: () => void, type: string) {
    alertInstance = getInstance(alertInstance);
    if (typeof content === "function") {
        content = content();
    }
    alertInstance.notice({
        content,
        duration,
        onClose,
        type,
        closable: true,
    });
}
export default {
    success(content: any, duration?: number, onClose?: () => void) {
        notice(content, duration, onClose, NOTICE_TYPES.SUCCESS);
    },
    error(content: any, duration?: number, onClose?: () => void) {
        notice(content, duration, onClose, NOTICE_TYPES.ERROR);
    },
    info(content: any, duration?: number, onClose?: () => void) {
        notice(content, duration, onClose, NOTICE_TYPES.INFO);
    },
    warning(content: any, duration?: number, onClose?: () => void) {
        notice(content, duration, onClose, NOTICE_TYPES.WARNING);
    },
    config(options) {
        if (options.top !== undefined) {
            defaultTop = options.top;
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
