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
        get_json("/library/db.json").then((data: any) => {
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
                        return (
                            <div key={book.sha} className={styl.center_book}>

                                <Link href={href} to={href} title={book.title}>
                                    <div className={styl.book_image}>
                                        <img src={book.cover ? `/library/${book.sha}/${book.cover}` : null} alt={book.title} title={book.title}/>
                                    </div>
                                </Link>
                                <span className={styl.book_title} title={book.title}>{book.title}</span>
                            </div>
                        );
                    })
                }
            </div>
        );
    }
}
