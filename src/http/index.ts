
const json = (res: Response) => res.json();
const text = (res: Response) => res.text();
/**
 * 获取json对象
 * @param url
 */
export function get_json(url: string) {
    return fetch(url).then(json);
}
/**
 * 获取文本
 * @param url
 */
export function get_text(url: string) {
    return fetch(url).then(text);
}

export function libraryData(sha: string) {
    return {
        get(url: string) {
            return fetch(url);
        },
        json(url: string) {
            return this.get(`/library/${sha}/${url}`).then(json);
        },
        text(url: string) {
            return this.get(`/library/${sha}/${url}`).then(text);
        },
        css(url: string) {
            return `/library/${sha}/${url}`;
        },
        image(url: string) {
            return this.css(url);
        },
    };
}
