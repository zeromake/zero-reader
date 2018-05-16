import styl from "../css/top-bar.styl";
import { h } from "react-import";
import SvgIcon from "./svg-icon";
import { propsDiffComponent } from "../utils";
import Animate from "preact-animate";

const TopBar = propsDiffComponent((props) => {
    const newProps = Animate.filterProps(props, {className: `${styl.top_bar} animated`});
    console.log(newProps);
    return <div {...newProps}>
        <div className={styl.middle_content}>
            <div className={styl.middle_wrap}>
                <h2>{`《${props.title}》`}</h2>
            </div>
        </div>
        <div className={styl.left_content}>
            { h(SvgIcon, {className: styl.icon, name: "icon-back", onClick: props.onBack}) }
        </div>
        <div className={styl.right_content}>
            { h(SvgIcon, {className: styl.icon, name: "icon-more", onClick: props.onMore}) }
        </div>
    </div>;
});

export default TopBar;
