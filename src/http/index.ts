import { customHistory, route, getCurrentUrl } from "react-import";
import qs from "qs";
let baseUrl = "";

if (process.env.platform === "cordova" && process.env.NODE_ENV !== "production") {
    baseUrl = location.origin;
}
if (process.env.platform === "cordova" && process.env.NODE_ENV === "production") {
    baseUrl = localStorage.getItem("baseUrl");
    if (!baseUrl || baseUrl === "") {
        baseUrl = prompt("填写服务器地址", "http://192.168.2.103:8080");
        localStorage.setItem("baseUrl", baseUrl);
    }
}
interface ITokenInfo {
    token?: string;
    exp?: number;
    refresh_token?: string;
    refresh_exp?: number;
}
const AUTH_HEADER = "Authorization";
const TokenArr = [
    "token",
    "exp",
    "refresh_token",
    "refresh_exp",
];
function getToken(): ITokenInfo {
    const info: ITokenInfo = {};
    for (const name of TokenArr) {
        let value: any = localStorage.getItem(name);
        if (value && value !== "") {
            if (name === "exp" || name === "refresh_exp") {
                value = +value;
            }
            info[name] = value;
        } else {
            break;
        }
    }
    return info;
}
function clearToken() {
    for (const name of TokenArr) {
        localStorage.removeItem(name);
    }
}
const json = (res: Response) => res.json();
const text = (res: Response) => res.text();

function raw_fetch(url, options?: RequestInit): Promise<Response> {
    if (baseUrl && baseUrl !== "") {
        url = baseUrl + url;
    }
    return fetch(url, options);
}
function verifyToken(): Promise<string> {
    const tokenInfo = getToken();
    const timeNow = new Date().getTime();
    if (tokenInfo.exp && tokenInfo.exp - timeNow >= 2000) {
        if (tokenInfo.refresh_exp && tokenInfo.refresh_exp - timeNow >= 2000) {
            return Promise.reject("token已过期!");
        } else {
            return raw_fetch("/api/refresh_token", {
                headers: {
                    [AUTH_HEADER]: tokenInfo.refresh_token,
                },
            }).then(json).then((res: any) => {
                if (res.status === 200) {
                    const token: string = res.data.token;
                    const exp: number = res.data.exp;
                    tokenInfo.token = token;
                    tokenInfo.exp = exp;
                    localStorage.setItem("token", token);
                    localStorage.setItem("exp", String(exp));
                    return Promise.resolve(token);
                } else {
                    return Promise.reject(res.message);
                }
            });
        }
    } else if (tokenInfo.token && tokenInfo.token !== "") {
        return Promise.resolve(tokenInfo.token);
    } else {
        return Promise.reject("token不存在!");
    }
}

const WhiteList = {
    "/api/login": true,
    "/api/register": true,
    "/api/forgotpwd": true,
};

function baseFetch(url: string, options?: RequestInit): Promise<Response | void> {
    if (url in WhiteList) {
        return raw_fetch(url, options);
    }
    const catchToken = (reason) => {
        clearToken();
        const customLocation = (customHistory && customHistory.location) || location;
        route("/?href=" +  encodeURIComponent(getCurrentUrl()) + "&error=" + encodeURIComponent(String(reason)));
    };
    return verifyToken().then((token: string) => {
        if (options && options.headers) {
            options.headers[AUTH_HEADER] = token;
        } else if (options) {
            options.headers = {
                [AUTH_HEADER]: token,
            };
        } else {
            options = {
                headers: {
                    [AUTH_HEADER]: token,
                },
            };
        }
        return raw_fetch(url, options);
    }).catch(catchToken);
}
(window as any).baseFetch = baseFetch;

export function get_json(url: string) {
    return raw_fetch(url).then(json);
}

function createObject() {
    if (Object.create) {
        return Object.create(null);
    } else {
        return {};
    }
}

const cache = (max: number = 10) => {
    let cacheMap: {[name: string]: any} = createObject();
    let hist = 0;
    let miss = 0;
    let length = 0;
    let keySet = createObject();
    let offset = 0;
    let promotionNum = 0;
    return {
        get(key: string) {
            const value = cacheMap[key];
            if (value) {
                hist += 1;
                this.promotion(key);
                return value.value;
            }
            miss += 1;
        },
        add(key: string, value: any) {
            let index: number;
            if (!(key in cacheMap)) {
                if (length === max) {
                    offset += 1;
                    let oldKey = keySet[offset];
                    while (!oldKey) {
                        offset += 1;
                        oldKey = keySet[offset];
                    }
                    delete keySet[offset];
                    delete cacheMap[oldKey];
                } else {
                    length += 1;
                }
                index = length + offset + promotionNum;
                keySet[index] = key;
                cacheMap[key] = {
                    value,
                    index,
                };
            } else {
                this.promotion(key);
                cacheMap[key].value = value;
            }
        },
        clear() {
            hist = 0;
            miss = 0;
            length = 0;
            offset = 0;
            keySet = createObject();
            cacheMap = createObject();
        },
        info() {
            return {hist, miss, length, offset, promotionNum, keySet};
        },
        promotion(key: string) {
            const oldValue = cacheMap[key];
            const oldIndex = oldValue.index;
            let newIndex = promotionNum + length + offset;
            if (newIndex === oldIndex) {
                return;
            }
            newIndex += 1;
            promotionNum += 1;
            delete keySet[oldIndex];
            keySet[newIndex] = key;
            cacheMap[key].index = newIndex;
        },
        remove(key: string) {
            const oldValue = cacheMap[key];
            const oldIndex = oldValue.index;
            delete keySet[oldIndex];
            delete cacheMap[key];
            length -= 1;
        },
        has(key: string) {
            return key in cacheMap;
        },
    };
};

const cacheData = cache(20);

export function libraryData(sha: string) {
    const libraryBaseUrl = baseUrl ? baseUrl + "/librarys" : "/librarys";
    return {
        get(url: string, callback) {
            if (libraryBaseUrl) {
                url = libraryBaseUrl + url;
            }
            const cacheValue = cacheData.get(url);
            if (cacheValue) {
                // console.log(cacheData.info());
                return Promise.resolve(cacheValue);
            } else {
                return fetch(url).then(callback).then((value: any) => {
                    cacheData.add(url, value);
                    // console.log(cacheData.info());
                    return Promise.resolve(value);
                });
            }
        },
        json(url: string) {
            return this.get(`/${sha}/${url}`, json);
        },
        text(url: string) {
            return this.get(`/${sha}/${url}`, text);
        },
        css(url: string) {
            return `${libraryBaseUrl}/${sha}/${url}`;
        },
        image(url: string) {
            return this.css(url);
        },
        has(url: string) {
            return cacheData.has(url);
        },
        syncGet(url: string) {
            return cacheData.get(url);
        },
    };
}
function $ajaxRaw(url: string, options?: RequestInit): Promise<void | Response> {
    if (baseUrl && baseUrl !== "") {
        url = baseUrl + url;
    }
    return baseFetch(url, options);
}
function $ajaxBody(url, method: string, params?: IFromData | null, init?: RequestInit): Promise<void | Response> {
    let options: RequestInit;
    if (init) {
        options = {
            method,
            ...init,
        };
    } else {
        options = {
            method,
        };
    }
    if (params) {
        options.body = JSON.stringify(params);
    }
    return $ajaxRaw(url, options);
}
interface IFromData {
    [name: string]: string | null | undefined | boolean | number;
}

export const $ajax = {
    raw: $ajaxRaw,
    get(url, params?: IFromData | null, init?: RequestInit): Promise<void | Response> {
        if (params) {
            url += "?" + qs.stringify(params);
        }
        return $ajaxRaw(url, init);
    },
    post(url, params?: IFromData | null, init?: RequestInit): Promise<void | Response> {
        return $ajaxBody(url, "POST", params, init);
    },
    delete(url, params?: IFromData | null, init?: RequestInit): Promise<void | Response> {
        return $ajaxBody(url, "DELETE", params, init);
    },
    put(url, params?: IFromData | null, init?: RequestInit): Promise<void | Response> {
        return $ajaxBody(url, "PUT", params, init);
    },
    patch(url, params?: IFromData | null, init?: RequestInit): Promise<void | Response> {
        return $ajaxBody(url, "PATCH", params, init);
    },
};
