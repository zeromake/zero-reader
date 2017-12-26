import styl from "@/css/top-bar.styl";
import { h } from "react-import";
import SvgIcon from "./svg-icon";
import { propsDiffComponent } from "@/utils";

const TopBar = propsDiffComponent((props) => {
    return <div className={`${styl.top_bar} animated`} onClick={(event: MouseEvent) => event.stopPropagation()}>
        <div className={styl.left_content}>
            <SvgIcon className={styl.icon} name="icon-back"/>
        </div>
        <div className={styl.middle_content}>
            <h2>{`《${props.title}》`}</h2>
        </div>
        <div className={styl.right_content}>
            <SvgIcon className={styl.icon} name="icon-more"/>
        </div>
    </div>;
});

export default TopBar;
