// import { Component, createElement as h } from "react";
// import { Link } from "react-router-dom";
import { Component, h, Link } from "react-import";
import styl from "@/css/library.styl";
import { get_json } from "@/http/index";

export default class Library extends Component<any, any> {
    constructor(p, c) {
        super(p, c);
        this.state = {
            library: [],
        };
    }
    public componentDidMount() {
        get_json("/db.json").then((data: any) => {
            this.setState({ library: data });
        });
    }
    public render() {
        const props = this.props;
        const state = this.state;
        return (
            <div className={styl.library + " animated"}>
                {
                    state.library.map((book) => {
                        const href = `/library/${book.sha}/`;
                        const title = book.title || book.file_name;
                        return (
                            <div key={book.sha} className={styl.center_book}>
                                <Link href={href} to={href} title={title}>
                                    <div className={styl.book_image}>
                                        <img src={book.cover ? `/library/${book.sha}/${book.cover}` : null} alt={title} title={title}/>
                                    </div>
                                </Link>
                                <span className={styl.book_title} title={title}>{title}</span>
                            </div>
                        );
                    })
                }
            </div>
        );
    }
}
