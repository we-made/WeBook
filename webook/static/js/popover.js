export class Popover {
    constructor({
        triggerElement,
        wrapperElement,
    } = {}) {
        this.triggerElement = triggerElement;
        this.wrapperElement = wrapperElement;
        
        this.isShown = false;

        if (this.triggerElement) {
            this._listenToTriggerElementClick();
        }

        this._listenToOutsideClicks();
    }

    _listenToTriggerElementClick() {
        this.triggerElement.addEventListener("click", function () {
            this.show();
        }.bind(this));
    }

    _listenToOutsideClicks() {
        console.log(">> _listenToOutsideClicks()!")
        $(document).click(function (event) {
            if (this.isShown && this.wrapperElement.contains(event.target) === false && event.target !== this.triggerElement && this.triggerElement.contains(event.target) === false) {
                this.show();
            }
        }.bind(this))
    }

    /**
     * Show/Hide the popover (toggle)
     */
    show() {
        console.log(">> Show!")
        this.wrapperElement.classList.toggle("active");
        this.isShown = !this.isShown;
        console.log(">>" + this.isShown)
    }
}