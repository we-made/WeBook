class Dialog {
    constructor({
        managerName,
        dialogId,
        discriminator,
        postInit,
        methods={},
        data={},
    } = {}) {
        this._methods = methods;

        this.managerName = managerName;
        this.dialogId = dialogId;
        this.discriminator = discriminator;

        this.data = data;

        this.$interior = null;
        this.interior = null;

        this.$dialogElement = this._getDialogElement();
        this.dialogElement = this.$dialogElement[0];

        this._spawnMutationObserver();
        this._discover();
        this._assimilateMethods();
        this._refreshListens();
        
        postInit(this);
    }

    /**
     * Spawn mutation observers and handlers guaranteeing that every time the dialog changes
     * that the attribute listeners will be refreshed and re-attached.
     */
    _spawnMutationObserver() {
        this.observer = new MutationObserver((mutations, observer) => {
            console.log(`${this.managerName}.${this.dialogId} refresh`);
            this._refreshListens();
        });
        this.observer.observe(this.$dialogElement[0], {
            subtree: true, 
            attributes: true,
        });
    }

    /**
     * Remove all existing listeners and attach new ones
     */
    _refreshListens() {
        this.$dialogElement.find('*[d-trigger]').off("click"); // remove old event handlers
        this._listenToDTriggerAttribute();
    }

    /**
     * Takes a string and converts it to camel case formatting, where an underscore denotes that the following character
     * is to be uppercased.
     * For example: entity_pk will be converted to entityPk, since there is an underscore before p (_p), p will be made
     * uppercase.
     * @param {*} str 
     * @returns str camelCased
     */
    _camelCaseFix(str) {
        for (let i = 0; i < str.length; i++) {
            if (str.charAt(i) === "_") {
                let nextChar = str.charAt(i+1);
                str = str.substring(0, i) + nextChar.toUpperCase() + str.substring(i+2, str.length);
            }
        }

        return str;
    }

    /**
     * Set up listeners listening to elements with the d-trigger attribute defined being clicked.
     * The d-triggr is a special attribute, and its value *should* refer to a method named in .methods.
     * On trigger we will try to run this method, while also getting all the d-arg (argument attributes)
     * defined on this element and feed them to the method as well. 
     */
    _listenToDTriggerAttribute () {
        this.$dialogElement.find('*[d-trigger]').click((event) => {
            let clickedElement = event.currentTarget;
            let nameOfMethodToTrigger = clickedElement.getAttribute("d-trigger");

            let argsObj = {};

            clickedElement.attributes.forEach((attr) => {
                if (attr.name.startsWith("d-arg-")) {
                    let argName = attr.name.split("-")[2];
                    argsObj[this._camelCaseFix(argName)] = attr.value;
                }
            });

            this[nameOfMethodToTrigger]( argsObj, event.currentTarget );
        });
    }


    getInteriorAsFormData() {
        let formData = new FormData();

        for ( let prop in this.interior ) {
            let element = this.interior[prop];
            if (element instanceof Node) {
                console.log(prop, element)
                formData.append(element.getAttribute("name"), element.value);
            }
        }

        return formData;
    }


    /**
     * Shorthand function for triggering a dialog managers "trigger" event, which makes it open/render
     * a dialog. The dialog managers are setting up listeners on $managerName.$dialogId.trigger when it is
     * initialized.
     * @param {*} managerName 
     * @param {*} dialogId 
     * @param {*} details 
     */
    raiseTriggerEvent(managerName, dialogId, details) {
        document.dispatchEvent(
            new CustomEvent(`${managerName}.${dialogId}.trigger`, { "detail": details })
        );
    }

    /**
     * Shorthand function for triggering a dialogs submit event. These are special events in the upstream
     * dialog manager. It is good practice to rely on the dialog manager, as opposed to doing the submit logic
     * in the dialog template. This allows for re-using dialogs, while writing independent implementations of submit 
     * logic for different managers.
     * @param {*} payload 
     */
    raiseSubmitEvent(payload) {
        if (!("dialog" in payload)) {
            payload.dialog = this.dialogId;
        }

        document.dispatchEvent(
            new CustomEvent(`${this.managerName}.submit`, {
                "detail": payload
            })
        );
    }

    /**
     * Gets the dialog element
     * @returns dialog element
     */
    _getDialogElement() {
        return $(`.${this.discriminator}`);
    }

    /**
     * Close this dialog (will close all dialogs on the owning manager)
     */
    closeMe() {
        document.dispatchEvent(new Event(`${this.managerName}.close`));
    }


    $(selector) {
        return this.$dialogElement.find(selector);
    }

    querySelector (selector) {
        return this.dialogElement.querySelector(selector);
    }

    querySelectorAll(selector) {
        return this.dialogElement.querySelectorAll(selector);
    }

    getElementById(id) {
        return this.dialogElement.querySelector("#" + id);
    }

    /**
     * Safely get an element within the dialog, same as $safeGet
     * @param {*} selector 
     * @returns 
     */
    safeGet(selector) {
        return this.$safeGet(selector)[0];
    }

    /**
     * Safely get an element within the dialog. safeGet guarantees giving you the unique and correct
     * element, that belongs to the dialog you are working with, so as to avoid collisions with identical
     * dialogs, or identically named elements.
     * @param {*} selector 
     */
    $safeGet(selector) {
        return this.$dialogElement.find(`${selector}`);
    }

    /**
     * Assimilate the consumers supplied methods into the dialog. We need to proxy them, so as 
     * to provide "this" to each dialog.
     */
    _assimilateMethods() {  
        for (const method in this._methods) {
            this.constructor.prototype[method] = 
                function () { 
                    return this._methods[method](this, ...arguments); 
                };
        }
    }

    /**
     * Goes through all inputs, selects, textareas, and maps them out so that they can be accessed
     * through the interior prop.
     */
    _discover() {
        let interior = {};
        
        this.$interior = this.$dialogElement.find("input, select, textarea");
        this.$interior.each((index, element) => {
                interior[element.id] = element;
            });

        this.interior = interior;
    }
}


class AbstractBaseStep {
    constructor (onStepIn, onStepOut, wrapperElement) {
        this.onStepIn = onStepIn;
        this.onStepOut = onStepOut;
        this.wrapperElement = wrapperElement;
    }
    
}

class DialogStepper {
    constructor({
        steps, 
        railWrapperElement="#rail", 
        allowRailBasedNavigation=false} = {}) {

        if ( !(Array.isArray(steps)) || steps.length == 0 ) {
            throw Error("Steps is not of a valid value, or length", steps)
        }

        this.steps = steps;
        this.currentStep = 0;
        this.railWrapperElement = railWrapperElement instanceof Node ? railWrapperElement : document.querySelector(railWrapperElement);
        this.allowRailBasedNavigation = false;

        this._setupSteps();
    }

    _render() {
      this.railWrapperElement.innerHTML = "";

      for (let i = 0; i < this.steps.length; i++) {
        let step = this.steps[i];

        let stepBtn = document.createElement('span');
        stepBtn.innerText = `${i+1}`;
        stepBtn.style.display = "inline";
        stepBtn.classList.add("stepper-stage-pill");
        if (this.currentStep == i) {
          stepBtn.setAttribute("disabled", "true")
          stepBtn.classList.add("active");
          stepBtn.innerText = `${i+1}. ${step.title}`;
        }
        stepBtn.onclick = () => this.stepTo(i);
        this.railWrapperElement.appendChild(stepBtn);
      }
    }

    _setupSteps() {
      this.steps.forEach(function (step) {
        if (!(step.element instanceof Node)) {
          step.element = document.querySelector(step.element);
        }
        step.element.style.display = 'none';
      });

      this.stepTo(this.currentStep);
    }

    next = () => this.stepTo(this.currentStep + 1)
    back = () => this.stepTo(this.currentStep - 1);

    _hideSteps = () => this.steps.forEach((step) => step.element.style.display = "none");

    /**
     * Step to indexToStepTo. If indexToStepTo is negative or greater than the amounts of steps then
     * false will be returned and the step will not be changed. The indexing is zero-based.
     * @param {*} indexToStepTo 
     */
    stepTo(indexToStepTo) {
        if (indexToStepTo >= this.steps.length || indexToStepTo < 0) {
            return false;
        }
        this._hideSteps();
        
        let hasMoved = this.currentStep !== indexToStepTo;
        let oldStep = this.steps[this.currentStep];
        let newStep = this.steps[indexToStepTo];

        newStep.element.style.display = 'block';
        if (typeof oldStep.stepOut !== "undefined" && hasMoved === true)
            oldStep.stepOut();
        if (typeof newStep.stepIn !== "undefined")
            newStep.stepIn();
        
        this.currentStep = indexToStepTo;

        this._render()
    }
  }