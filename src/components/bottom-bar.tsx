import { h, Component } from "zreact";
import styl from "@/css/bottom-bar.styl";

const bottomMenu = [
    {icon: "fa-list-ul", title: "目录", id: 1},
    {icon: "fa-desktop", title: "浏览方式", id: 2},
    {icon: "fa-exclamation-circle", title: "文档属性", id: 3},
    {icon: "fa-gear", title: "设置", id: 4},
];

export default class BottomBar extends Component<any, any> {
    public test(id, event) {
        console.log("-------", id);
    }
    public render() {
        return <div class={styl.bottom_bar}>
            <ul class={styl.menus}>
            {
                bottomMenu.map((menu) => {
                    return <li class={styl.menu}>
                        <i class={"fa " + menu.icon + " " + styl.icon} onClick={this.test.bind(this, menu.id)} title={menu.title}></i>
                    </li>;
                })
            }
            </ul>
        </div>;
    }
}
