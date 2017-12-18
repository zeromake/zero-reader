import AbcLayout from "./abc-layout";
import { findDOMNode, h } from "react-import";
import styl from "@/css/layout.styl";
import BookToolsBar from "./book-tools-bar";
import BottomBar from "./bottom-bar";

export default class EpubLayout extends AbcLayout<any, any> {
    protected isBlock;

    protected tocClick(toc) {

    }
    protected  renderHeader() {
        const state = this.state;
        // const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        return <BookToolsBar options={ { showToc: () => {this.setState({ toc_open: !state.toc_open }); } } }/>;
    }
    protected  renderFooter() {
        return <BottomBar/>;
    }
    protected  renderContent() {
        const state = this.state;
        return <div className={styl.pageHtml}>
                <div className={styl.view + " w0 h0"} dangerouslySetInnerHTML={{__html: state.pageHtml}}>
                </div>
            </div>;
    }
}
