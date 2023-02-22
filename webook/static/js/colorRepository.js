const _COLORS = [
    { background: "#d0fffd", border: "#18FFF9", text: "black" },
    { background: "#e8cfeb", border: "#8F139F", text: "black" },
    { background: "#cce6ee", border: "#0086AD", text: "black" },
    { background: "#ccf6e5", border: "#00D27F", text: "black" },
    { background: "#fbdbe9", border: "#EF4F91", text: "black" },
    { background: "#dbd1e4", border: "#4D1B7B", text: "black" },
    { background: "#fffccc", border: "#fff000", text: "black" },

]

export class ColorRepository {
    constructor() {
        this.step = 0;
        this._colors = _COLORS
    }

    getColor() {
        const color = this._colors[this.step]
        this.step++;
        return color;
    }

    reset() {
        this.step = 0;
    }
}