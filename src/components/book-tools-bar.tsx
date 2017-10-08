import { h, Component } from "zreact";
import styl from "@/css/book-tools-bar.styl";



export default class BookToolsBar extends Component<any, any>{
    render(props: any) {
        const options = props.options;
        return <div class={styl.container_bar}>
            <div class={styl.toolbarLeft}>
                <button class={styl.toolbarButton} title="目录" onClick={options.showToc}>
                </button>
            </div>
            <div class={styl.toolbarRight}>

            </div>
            <div class={styl.toolbarMiddle}>

            </div>
        </div>
    };
}