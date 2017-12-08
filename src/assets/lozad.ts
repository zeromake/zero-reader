const defaultConfig = {
    rootMargin: "0px",
    threshold: 0,
    target: document,
    load(element) {
        if (element.getAttribute("data-src")) {
            element.src = element.getAttribute("data-src");
        }
        if (element.getAttribute("data-srcset")) {
            element.srcset = element.getAttribute("data-srcset");
        }
        if (element.getAttribute("data-background-image")) {
            element.style.backgroundImage = "url(' + element.getAttribute(\"data-background-image\") + ')";
        }
    },
};

function markAsLoaded(element) {
    element.setAttribute("data-loaded", true);
}

const isLoaded = function isLoaded_(element) {
    return element.getAttribute("data-loaded") === "true";
};

const onIntersection = (load) => (entries, observer) => {
    entries.forEach((entry) => {
        if (entry.intersectionRatio > 0) {
            observer.unobserve(entry.target);

            if (!isLoaded(entry.target)) {
                load(entry.target);
                markAsLoaded(entry.target);
            }
        }
    });
};

export default function _(selector = ".lozad", options = {}) {
    const { rootMargin, threshold, load, target } = {...defaultConfig, ...options } as typeof defaultConfig;
    let observer;

    if ("IntersectionObserver" in window) {
        observer = new IntersectionObserver(onIntersection(load), {
            rootMargin,
            threshold,
        });
    }

    let elements: Node[] = Array.prototype.slice.apply(target.querySelectorAll(selector));
    return {
        observe() {
            for (const element of elements) {
                if (isLoaded(element)) {
                    continue;
                }
                if (observer) {
                    observer.observe(element);
                    continue;
                }
                load(element);
                markAsLoaded(element);
            }
        },
        triggerLoad(element) {
        if (isLoaded(element)) {
            return;
        }
        load(element);
        markAsLoaded(element);
        },
        unobserve() {
            for (const element of elements) {
                observer.unobserve(element);
            }
        },
        update() {
            elements = Array.prototype.slice.apply(target.querySelectorAll(selector));
            this.observe();
        },
    };
}
