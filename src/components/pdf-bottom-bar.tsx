import { h } from "react-import";
import styl from "../css/bottom-bar.styl";
import SvgIcon from "./svg-icon";
import Animate from "preact-animate";
import { propsDiffComponent } from "../utils";

// const bottomMenu = [
//     {icon: "fa-list-ul", title: "目录", id: 1},
//     {icon: "fa-desktop", title: "浏览方式", id: 2},
//     {icon: "fa-exclamation-circle", title: "文档属性", id: 3},
//     {icon: "fa-gear", title: "设置", id: 4},
// ];
const bottomMenu = [
    {icon: "icon-sort", title: "目录", id: 1},
    {icon: "icon-read", title: "浏览方式", id: 2},
    {icon: "icon-info", title: "文档属性", id: 3},
    {icon: "icon-settings", title: "设置", id: 4},
];

const BottomBar = propsDiffComponent((props) => {
        return <div {...Animate.filterProps(props, {className: `${styl.bottom_bar} animated`})}>
            <ul className={styl.menus}>
            {
                bottomMenu.map((menu) => {
                    const click = (event) => props.click(menu.id, event);
                    return <li className={styl.menu} key={String(menu.id)}>
                        { h(SvgIcon, {className: styl.icon, name: menu.icon, onClick: click, title: menu.title}) }
                    </li>;
                })
            }
            </ul>
        </div>;
});
export default BottomBar;
