import { h, Component } from "module-react";
import Animate from "preact-animate";
import { prefix } from "./utils";

interface IProps {
    duration: number;
    content: any;
    onClose?: () => void;
    closable?: boolean;
    classPrefix: string;
    className?: string;
    style?: any;
    type?: string;
}
export default class Notice extends Component<IProps, any> {
    public props: IProps;
    public state: any;
    public context: any;
    public refs: any;
    private closeTimer?: number;
    public componentDidMount() {
        const { duration } = this.props;
        if (duration) {
            this.closeTimer = setTimeout(this.close, duration);
        }
    }
    public componentWillUnmount() {
        this.clearCloseTimer();
    }
    public clearCloseTimer() {
        if (this.closeTimer) {
            clearTimeout(this.closeTimer);
            this.closeTimer = null;
        }
    }
    public close = () => {
        const { onClose } = this.props;
        this.clearCloseTimer();
        onClose!();
    }
    public addPrefix(name: string) {
        return prefix(this.props.classPrefix)(name);
    }
    public render() {
        const {
            classPrefix,
            closable,
            className,
            content,
            style,
            type = "",
        } = this.props;
        const noticeClass = this.addPrefix("notice");
        const newProps = Animate.filterProps(this.props, {className: `${noticeClass}-wrapper`});
        const arr: string[] = [noticeClass];
        if (closable) {
            arr.push(this.addPrefix("notice-closable"));
        }
        if (!!type) {
            arr.push(`${classPrefix}-${type}`);
        }
        const classes = arr.join(" ");
        return (
            <div {...newProps}>
                <div className={classes} style={style}>
                <div className={`${noticeClass}-content`}>{content}</div>
                {closable && (
                    <div
                        role="button"
                        tabIndex={-1}
                        onClick={this.close}
                        className={`${noticeClass}-close`}
                    >
                        <span className={`${noticeClass}-close-x`} />
                    </div>
                )}
                </div>
            </div>
        );
    }
}
