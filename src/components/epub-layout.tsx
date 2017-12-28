import AbcLayout from "./abc-layout";
import { findDOMNode, h } from "react-import";
import styl from "../css/layout.styl";

export default class EpubLayout extends AbcLayout<any, any> {
    protected isBlock;

    protected tocClick(toc) {

    }
    protected  renderHeader() {
        const state = this.state;
        // const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        return "";
    }
    protected  renderFooter() {
        return "";
    }
    protected  renderContent() {
        const state = this.state;
        return <div className={styl.pageHtml}>
                <div className={styl.view + " w0 h0"} dangerouslySetInnerHTML={{__html: state.pageHtml}}>
                </div>
            </div>;
    }
}
