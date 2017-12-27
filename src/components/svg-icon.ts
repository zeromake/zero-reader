import { h } from "react-import";
import { propsDiffComponent } from "@/utils";

const SvgIcon = propsDiffComponent((props) => {
    const name = props.name;
    const newProps = {...props};
    delete newProps.name;
    delete newProps.children;
    newProps.className = newProps.className ? `svg_icon ${newProps.className}` : "svg_icon";
    return h("svg", newProps, h("use", {xlinkHref: `#${name}`}));
});

export default SvgIcon;
