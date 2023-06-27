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
            if (this.wrapperElement.style.display === "none") {
                this.wrapperElement.style.display = "block";
            }
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
        this.wrapperElement.classList.toggle("active");
        this.isShown = !this.isShown;
    }
}