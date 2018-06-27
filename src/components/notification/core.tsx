import { h, Component, render, unmountComponentAtNode, findDOMNode } from "module-react";
import Animate from "preact-animate";
import { prefix, NAME_SPACE } from "./utils";
import Notice from "./notice";

interface IProps {
    className?: string;
    classPrefix?: string;
    style?: any;
    ref?: (c: Notification) => void;
}

interface IProperties extends IProps {
    duration?: number;
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
    constructor(props: IProps, context: any) {
        super(props, context);
        this.state = {
            animated: false,
            notices: [],
        };
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
        notice.animated = true;
        if (!(notices.filter((n: any) => n.key === key).length)) {
            this.setState({
                notices: notices.concat(notice),
            });
        }
    }

    public remove = (key: string) => {
        this.setState((prevState: IState) => {
            return {
                notices: prevState.notices.filter((notice: any) => notice.key !== key),
            };
        });
        // this.actualRemove(key);
        // const { notices } = this.state;
        // const nextNotices = notices.map((n: any) => {
        //     if (n.key === key) {
        //         n.animated = false;
        //     }
        //     return n;
        // });
        // this.setState(
        //     {
        //         notices: nextNotices,
        //     },
        //     () => {
        //         setTimeout(() => {
        //             this.actualRemove(key);
        //         }, 1000);
        //     },
        // );
    }

    // public actualRemove(key: string) {
    //     this.setState((prevState: IState) => {
    //         return {
    //             notices: prevState.notices.filter((notice: any) => notice.key !== key),
    //         };
    //     });
    // }

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
                showProp="animated"
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
