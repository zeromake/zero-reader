import { h, Component } from "react-import";
import styl from "@/css/toc.styl";
import TocItem from "./toc-item";

const Toc = (props: any, content: any) => {
    const theme = props.theme;
    return (
        <div className={styl.tocView + (theme ? " " + styl[theme] : "")}>
            {
                props.tocs.map((toc, index: number) => {
                    return h(
                        TocItem,
                        {
                            key: `0_${index}_${toc.index}`,
                            onclick: props.onclick,
                            toc,
                            level: 1,
                        },
                    );
                })
            }
        </div>
    );
};
export default Toc;
