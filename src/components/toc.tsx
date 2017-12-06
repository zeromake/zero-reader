import { h, Component } from "react-import";
import styl from "@/css/toc.styl";
import TocItem from "@/components/toc-item";

const Toc = (props: any, content: any) => {
    const theme = props.theme;
    return (
        <div className={styl.tocView + (theme ? " " + styl[theme] : "")}>
            {
                props.tocs.map((toc) => {
                    return <TocItem key={toc.text} onclick={props.onclick} toc={toc}/>;
                })
            }
        </div>
    );
};
export default Toc;
