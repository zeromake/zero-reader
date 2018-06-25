import { h, Component, render } from "module-react";
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
    duration: number;
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

export default class Notification extends Component<IProps, IState> {
    public static defaultProps = {
        classPrefix: `${NAME_SPACE}-notification`,
        style: {
            top: "5px",
        },
    };

    public static newInstance(properties?: IProperties): {notice(p: IProps): void} {
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
        const { notices } = this.state;
        const nextNotices = notices.map((n: any) => {
            if (n.key === key) {
                n.animated = false;
            }
            return n;
        });
        this.setState(
            {
                notices: nextNotices,
            },
            () => {
                setTimeout(() => {
                    this.actualRemove(key);
                }, 1000);
            },
        );
    }

    public actualRemove(key: string) {
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
                <Animate
                key={notice.key}
                component={null}
                transitionEnter={true}
                transitionLeave={true}
                transitionName={{
                    enter: this.addPrefix("enter"),
                    leave: this.addPrefix("exit"),
                }}
                isRender={false}
                >
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
                </Animate>
            );
        });
        const classes = [classPrefix, className].join(" ");
        return (
            <div className={classes} style={style}>
                {notieNodes}
            </div>
        );
    }
}
