import { h, Component } from "react-import";
import styl from "@/css/bottom-bar.styl";

const bottomMenu = [
    {icon: "fa-list-ul", title: "目录", id: 1},
    {icon: "fa-desktop", title: "浏览方式", id: 2},
    {icon: "fa-exclamation-circle", title: "文档属性", id: 3},
    {icon: "fa-gear", title: "设置", id: 4},
];
// const bottomMenu = [
//     {icon: "lnr-menu", title: "目录", id: 1},
//     {icon: "lnr-screen", title: "浏览方式", id: 2},
//     {icon: "lnr-question-circle", title: "文档属性", id: 3},
//     {icon: "lnr-cog", title: "设置", id: 4},
// ];

export default class BottomBar extends Component<any, any> {
    public test(id, event) {
        event.stopPropagation();
        console.log("-------", id);
    }
    public render() {
        return h("div", {className: `${styl.bottom_bar} ${styl.animated}`, style: this.props.style},
            <ul className={styl.menus}>
            {
                bottomMenu.map((menu) => {
                    return <li className={styl.menu}>
                        <i className={"fa " + menu.icon + " " + styl.icon} onClick={this.test.bind(this, menu.id)} title={menu.title}></i>
                    </li>;
                })
            }
            </ul>,
        );
    }
}
