import { h, Component } from "zreact";
import styl from "@/css/toc.styl";
import TocItem from "@/components/toc-item";

const Toc = (props: any, content: any) => {
    const theme = props.theme;
    return (
        <div class={styl.tocView + (theme ? " " + styl[theme] : "")}>
            {
                props.tocs.map((toc) => {
                    return <TocItem onclick={props.onclick} toc={toc}/>;
                })
            }
        </div>
    );
};
export default Toc;
