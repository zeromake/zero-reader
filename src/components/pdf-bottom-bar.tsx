import { h } from "react-import";
import styl from "@/css/bottom-bar.styl";

const bottomMenu = [
    {icon: "fa-list-ul", title: "目录", id: 1},
    {icon: "fa-desktop", title: "浏览方式", id: 2},
    {icon: "fa-exclamation-circle", title: "文档属性", id: 3},
    {icon: "fa-gear", title: "设置", id: 4},
];
const BottomBar = function render(props) {
        return <div className={`${styl.bottom_bar} animated`} onClick={(event) => event.stopPropagation()}>
            <ul className={styl.menus}>
            {
                bottomMenu.map((menu) => {
                    const click = (event) => props.click(menu.id, event);
                    return <li className={styl.menu}>
                        <i className={"fa " + menu.icon + " " + styl.icon} onClick={click} title={menu.title}></i>
                    </li>;
                })
            }
            </ul>
        </div>;
};
export default BottomBar;
