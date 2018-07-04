import { h, Component, render, unmountComponentAtNode, findDOMNode } from "module-react";
import Animate from "preact-animate";
import { prefix, NAME_SPACE } from "./utils";
import Notice from "./notice";

interface IProps {
    duration?: number;
    className?: string;
    classPrefix?: string;
    style?: any;
    ref?: (c: Notification) => void;
}

interface IProperties extends IProps {
    getContainer?: () => Element;
}

interface IState {
    animated: boolean;
    notices: any[];
}

let id = 0;
const getUid = () => {
  id += 1;
  return `${NAME_SPACE}-notification-${Date.now()}-${id}`;
};

interface INotificationInstance {
    notice(p: IProps): void;
    remove(key: string): void;
    destroy(): void;
}

export default class Notification extends Component<IProps, IState> {
    public static defaultProps = {
        classPrefix: `${NAME_SPACE}-notification`,
        style: {
            top: "5px",
        },
    };

    public static newInstance(properties?: IProperties): {} {
        const { getContainer, ...props } = properties || {} as IProperties;
        let div: Element;
        if (getContainer) {
            div = getContainer();
        } else {
            div = document.createElement("div");
            document.body!.appendChild(div);
        }
        let notificationComponent: Notification | undefined | null;
        props.ref = function ref(c: Notification | null) {
            notificationComponent = c;
        };
        render(<Notification {...props} />, div);
        return {
            notice(noticeProps: IProps) {
                if (notificationComponent) {
                    notificationComponent.add(noticeProps);
                }
            },
            remove(key: string) {
                if (notificationComponent) {
                    notificationComponent.remove(key);
                }
            },
            destroy() {
                if (notificationComponent) {
                    unmountComponentAtNode(findDOMNode(notificationComponent));
                    document.body.removeChild(div);
                    div = null;
                }
            },
            component() {
                return notificationComponent;
            },
        };
    }
    public props: IProps;
    public state: IState;
    public done: any;
    constructor(props: IProps, context: any) {
        super(props, context);
        this.done = null;
        this.state = {
            animated: false,
            notices: [],
        };
        this.onAfterLeave = this.onAfterLeave.bind(this);
    }

    public add(notice: any) {
        const { notices } = this.state;
        let key: string;
        if (notice.key == null) {
            key = getUid();
        } else {
            key = notice.key;
        }
        notice.key = key;
        let has = false;
        let data = null;
        if (notices.length) {
            for (const n of notices) {
                if (n.key === key) {
                    data = notices.filter((item) => item.key !== key);
                    has = true;
                    break;
                }
            }
            if (!has) {
                data = notices.concat(notice);
            }
        } else {
            data = [notice];
        }
        if (has) {
            this.done = notice;
        }
        this.setState({
            notices: data,
        });
    }

    public onAfterLeave(com: any) {
        if (this.done) {
            if (this.done.key === com.props.rawKey) {
                 this.setState({
                    notices: this.state.notices.concat(this.done),
                });
            }
            this.done = null;
        }
    }

    public remove = (key: string) => {
        this.setState((prevState: IState) => {
            return {
                notices: prevState.notices.filter((notice: any) => notice.key !== key),
            };
        });
    }

    public addPrefix(name: string | string[]) {
        return prefix(this.props.classPrefix)(name);
    }

    public render() {
        const { notices } = this.state;
        const { className, style, classPrefix } = this.props;
        const notieNodes = notices.map((notice: any) => {
            return (
                <Notice
                    classPrefix={classPrefix}
                    {...notice}
                    onClose={() => {
                        this.remove(notice.key);
                        if (notice.onClose) {
                            notice.onClose();
                        }
                    }}
                >
                </Notice>
            );
        });
        const classes = [classPrefix, className].join(" ");
        return (
            <Animate
                component="div"
                componentProps={{className: classes, style}}
                transitionEnter={true}
                transitionLeave={true}
                onAfterLeave={this.onAfterLeave}
                // showProp="animated"
                transitionName={{
                    enter: "fadeInDown",
                    leave: "fadeOutUp",
                }}
                isRender={true}
            >
                {notieNodes}
            </Animate>
        );
    }
}
