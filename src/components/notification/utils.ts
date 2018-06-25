
export const NAME_SPACE = "zr";
export const NOTICE_TYPES = {
    SUCCESS: "success",
    ERROR: "error",
    INFO: "info",
    WARNING: "warning",
};

export function prefix(fix: string) {
    return function _(className: string | string[]): string {
        if (!fix || !className) {
            return "";
        }
        if (typeof className === "object" && className.filter) {
            return (className as string[]).filter((name: any) => !!name).map((name: any) => `${fix}-${name}`).join(" ");
        }
        return `${fix}-${className}`;
    };
}
