import { h, Component, Link } from "react-import";
import styl from "@/css/book-tools-bar.styl";
import screenfull from "screenfull";

export default class BookToolsBar extends Component<any, any> {
    public fullScreen() {
        if (screenfull) {
            screenfull.toggle();
        }
    }
    public render(props?: any) {
        const options = props.options;
        return <div className={styl.container_bar}>
            <div className={styl.toolbarLeft}>
                <button className={styl.toolbarButton} title="目录" onClick={options.showToc}>
                </button>
                <Link href="/">主页</Link>
                <button onClick={this.fullScreen}>全屏</button>
            </div>
            <div className={styl.toolbarRight}>

            </div>
            <div className={styl.toolbarMiddle}>

            </div>
        </div>;
    }
}
