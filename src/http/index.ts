
const json = (res: Response) => res.json();
const text = (res: Response) => res.text();

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

export function libraryData(sha: string) {
    const cacheData = cache(20);
    return {
        get(url: string, callback) {
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
            return this.get(`/library/${sha}/${url}`, json);
        },
        text(url: string) {
            return this.get(`/library/${sha}/${url}`, text);
        },
        css(url: string) {
            return `/library/${sha}/${url}`;
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
