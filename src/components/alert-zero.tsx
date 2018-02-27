import { h, findDOMNode, Component } from "react-import";
import styl from "@/css/alert-zero.styl";
import Animate from "preact-animate";
import SvgIcon from "./svg-icon";
// import { shallowDiffers } from "../utils";

function shallowDiffers(a: any, b: any): boolean {
    for (const i in a) {
        if (!(i in b)) {
            return true;
        }
    }
    for (const i in b) {
        if (a[i] !== b[i]) {
            return true;
        }
    }
    return false;
}
enum Level {
    INFO = 0,
    ERROR = 1,
}

interface IAlertZeroProps {
    defaultShow?: boolean;
    position?: "left-down" | "right-down" | "left-up" | "right-up";
    timeout?: number;
    message?: string | null;
    level?: Level;
    ref?: (c: AlertZero) => any;
}

const LevelColor = {
    0: "#000",
    1: "red",
};

export default class AlertZero extends Component<IAlertZeroProps, any> {
    private time: any;
    constructor(props: IAlertZeroProps, c: any) {
        super(props, c);
        this.state = {
            show: props.defaultShow,
        };
        this.time = null;
        const timeout: number = props.timeout;
        this.toggler = this.toggler.bind(this);
        // if (props.defaultShow && timeout > 0) {
        //     this.time = setTimeout(() => {
        //         this.toggler();
        //     }, timeout);
        // }
    }
    public shouldComponentUpdate(props: any, state: any): boolean {
        // props只要一个不同就返回true
        const flag = shallowDiffers(this.props, props) || shallowDiffers(this.state, state);
        return flag;
    }
    public static defaultProps = {
        defaultShow: false,
        position: "right-up",
        timeout: 2000,
        level: Level.INFO,
    };
    public isShow() {
        return this.state.show;
    }
    public toggler() {
        return new Promise((resolve) => {
            const show = !this.state.show;
            if (this.time) {
                clearTimeout(this.time);
                this.time = null;
            }
            this.setState({
                show,
            }, () => {
                    const timeout: number = this.props.timeout;
                    if (show && timeout > 0) {
                        this.time = setTimeout(() => {
                            this.toggler();
                        }, timeout);
                    }
                    return resolve();
                });
            });
    }
    public render() {
        const props = this.props;
        return (
            <Animate
                component={null}
                transitionName={{ enter: "fadeInRight", leave: "fadeOutRight" }}
                transitionEnter={true}
                transitionLeave={true}
                showProp="data-show"
            >
                <div className={styl.content + " animated"} data-show={this.state.show && this.props.message}>
                    <div className={styl.close}>
                        {h(SvgIcon, { name: "icon-close_light", className: styl.close_icon, onClick: this.toggler })}
                    </div>
                    <div className={styl.body}>
                        <span style={{color: LevelColor[props.level]}}>{this.props.message}</span>
                    </div>
                </div>
            </Animate>
        );
    }
}
