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
    }

    _listenToTriggerElementClick() {
        this.triggerElement.addEventListener("click", function () {
            this.show();
        }.bind(this));
    }

    _listenToOutsideClicks() {
        $(document).click(function (event) {
            if (this.isShown && this.wrapperElement.contains(event.target) === false && event.target !== this._triggerElement) {
                this.show();
            }
        }.bind(this))
    }

    /**
     * Show/Hide the popover (toggle)
     */
    show() {
        this.wrapperElement.classList.toggle("active");
        // $(this.wrapperElement).toggleClass("active", !this.isShown, 400, "fold");
        
        this.isShown = !this.isShown;
    }
}