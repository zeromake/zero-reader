import styl from "@/css/top-bar.styl";
import { h } from "react-import";
import SvgIcon from "./svg-icon";
import { propsDiffComponent } from "@/utils";

function onClick() {
    console.log("---------");
}

const TopBar = propsDiffComponent((props) => {
    return <div className={`${styl.top_bar} animated`} onClick={(event: MouseEvent) => event.stopPropagation()}>
        <div className={styl.middle_content}>
            <div className={styl.middle_wrap}>
                <h2>{`《${props.title}》`}</h2>
            </div>
        </div>
        <div className={styl.left_content}>
            { h(SvgIcon, {className: styl.icon, name: "icon-back", onClick}) }
        </div>
        <div className={styl.right_content}>
            { h(SvgIcon, {className: styl.icon, name: "icon-more", onClick}) }
        </div>
    </div>;
});

export default TopBar;
