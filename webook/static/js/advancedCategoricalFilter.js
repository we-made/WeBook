/**
 * advancedCategoricalFilter.js
 * 
 * Implementation of an advanced categorical filter functioning as a dropdown / popover like
 * utility. Based on a category->children[] relationship, one can toggle/hide categories and children, search categories,
 * and retrieve the state (currently selected entities).
 */

import { Popover } from "./popover.js";

const BUTTON_CLASSES = [
    "btn", "btn-sm", "btn-white", "shadow-0",
]

const ITEM_CLASSES = [
    "badge", "border-body", "text-dark", "acf__item",
    "rounded-pill", "clickable-badge", "p-3", "m-1",
]

const CATEGORY_SEARCH_INPUT_CLASSES = [
    "form-control", "mb-1", "mt-1",
]

const X_OF_Y_CLASSES = [
    "small", "text-align-end", "d-block", "mt-1",
]


export class AdvancedCategoricalFilter extends Popover {
    constructor ( { 
        triggerMode,
        triggerElement, 
        wrapperElement, 
        data,
        selectionPresets,
        onSelectionUpdate,
        onSubmit,
        } = {} ) {

        super({
            triggerElement: triggerElement,
            wrapperElement: wrapperElement,
        });

        this._instanceDiscriminator = crypto.randomUUID();

        this._triggerMode = triggerMode;
        this._selectionPresets = selectionPresets;
        this._data = data;
        this._onSubmit = onSubmit;
        
        this.isRendered = false;

        // Map the items in the supplied data into a more easily accessible map, 
        // where the key is the supplied key for the item.
        this._itemsMap = this._mapItems(this._data);
        
        this.onSelectionUpdate = onSelectionUpdate;

        this._selectedMap = new Map();
        this._categorySearchMap = new Map();

        this._render();
    }

    _mapItems(data) {
        let itemsMap = new Map();
        data.forEach(function (category) {
            category.items.forEach( function (item) {
                item.categoryKey = category.key;
                itemsMap.set(item.key, item)
            });
        });

        return itemsMap;
    }

    static TRIGGERMODE_BUTTON = Symbol("TriggerModeButton")
    static TRIGGERMODE_ONUPDATE = Symbol("TriggerModeOnUpdate")

    _debounce (func, timeout = 300) {
        let timer;
        return (...args) => {
          clearTimeout(timer);
          timer = setTimeout(() => { func.apply(this, args); }, timeout);
        };
    }

    /**
     * Construct the html of the popover, using the supplied data.
     */
    _render() {
        this.wrapperElement.innerHTML = "";
        if (!this.wrapperElement.classList.contains("popover_wrapper")) {
            this.wrapperElement.classList.add("popover_wrapper");
        }

        let popoverContentEl = document.createElement("div");
        popoverContentEl.classList.add("popover_content", this._instanceDiscriminator);

        this.wrapperElement.appendChild(popoverContentEl);

        this._selectionPresets.forEach(function (selectionPreset) {
            let presetChipElement = document.createElement("div");
            presetChipElement.classList.add(...ITEM_CLASSES);
            presetChipElement.innerText = selectionPreset.title;
            presetChipElement.setAttribute("key", selectionPreset.key);
            presetChipElement.onclick = function (event) { 
                event.target.classList.toggle("active");
                selectionPreset.activates.forEach(function (key) {
                    this._toggleItemActiveState(key);
                }.bind(this));
            }.bind(this);
            popoverContentEl.appendChild(presetChipElement);
        }.bind(this))

        this._data.forEach(function (category) {
            let categoryWrapperElement = document.createElement("div");
            categoryWrapperElement.classList.add("__acf_categoryWrapper");
            categoryWrapperElement.setAttribute("id", category.key);

            let categoryTitleElement = document.createElement("h3")
            categoryTitleElement.innerText = category.category;
            categoryTitleElement.classList.add("mb-0");
            categoryWrapperElement.appendChild(categoryTitleElement);

            let categoryActivateAllButtonElement = document.createElement("button");
            categoryActivateAllButtonElement.classList.add(...BUTTON_CLASSES);
            categoryActivateAllButtonElement.innerHTML = "<i class='fas fa-check text-success'></i>&nbsp; Activate All";
            categoryActivateAllButtonElement.onclick = function (event) {
                this._setStateForAllItemsInCategory(category.key, true);
            }.bind(this);

            let categoryDeactivateAllButtonElement = document.createElement("button");
            categoryDeactivateAllButtonElement.classList.add(...BUTTON_CLASSES, "ms-2");
            categoryDeactivateAllButtonElement.innerHTML = "<i class='fas fa-times text-danger'></i>&nbsp; Deactivate All"
            categoryDeactivateAllButtonElement.onclick = function (event) {
                this._setStateForAllItemsInCategory(category.key, false);
            }.bind(this);

            categoryWrapperElement.appendChild(categoryActivateAllButtonElement);
            categoryWrapperElement.appendChild(categoryDeactivateAllButtonElement);

            let categorySearchInputElement = document.createElement("input");
            categorySearchInputElement.classList.add(
                ...CATEGORY_SEARCH_INPUT_CLASSES,
                "__acf_categorySearch",
            )
            categorySearchInputElement.setAttribute("placeholder", `Search through ${category.category}...`);
            
            if (this._categorySearchMap.has(category.key)) {
                categorySearchInputElement.value = this._categorySearchMap.get(category.key);
            }

            categorySearchInputElement.addEventListener("input", function (event) {
                let searchText = event.target.value;

                this._categorySearchMap.set(category.key, searchText);
                this._refocusSelector = `div.${this._instanceDiscriminator} div.__acf_categoryWrapper#${category.key} input.__acf_categorySearch`;
        
                /* this._categorySearchMap will be heeded and we will run ._searchItems() when rendering,
                and the new filtered version will be shown */
                this._debounce( this._render(), 300 );
            }.bind(this));

            categoryWrapperElement.appendChild(categorySearchInputElement);
            
            let items = this._searchItems(category.items, this._categorySearchMap.get(category.key));

            items.forEach(function (item) {
                let itemElement = document.createElement("div");
                itemElement.classList.add(
                    ...ITEM_CLASSES,
                    item.active || this._selectedMap.has(item.key) ? "active" : undefined,
                );
                itemElement.innerText = item.text;
                itemElement.setAttribute("id", item.key);
                itemElement.onclick = function (event) {
                    this._toggleItemActiveState(item.key);
                }.bind(this);
                categoryWrapperElement.appendChild(itemElement);
            }.bind(this));

            let countOfHiddenSelectedItems = this._selectedMap.size - items.filter( (x) => x.active ).length;

            let xOutOfYElement = document.createElement("em");
            xOutOfYElement.innerText = `${category.items.length} out of ${category.items.length} elements shown (${countOfHiddenSelectedItems} are hidden, but selected)`;
            xOutOfYElement.classList.add(...X_OF_Y_CLASSES);
            categoryWrapperElement.appendChild(xOutOfYElement);

            popoverContentEl.appendChild(categoryWrapperElement);
        }.bind(this));

        if (this._refocusSelector !== undefined) {
            $(this._refocusSelector).focus();
            this._refocusSelector = undefined;
        }

        this.isRendered = true;
    }

    _setStateForAllItemsInCategory(categoryKey, newState) {
        let $itemHtmlElements = this._$getItemHtmlElementsInCategory(categoryKey);
        let keys = [];
        $itemHtmlElements.each( (index, $item) => { 
            this._setItemActiveState($item.id, newState, false); 
            keys.push($item.id);
        });
        this._triggerSelectionUpdateEvent( keys );
    }

    _$getItemHtmlElementsInCategory(categoryKey) {
        return $(`div.${this._instanceDiscriminator} div.__acf_categoryWrapper#${categoryKey} div.acf__item`);
    }

    _getItemHtmlElementByKey(key) {
        return $(`div.${this._instanceDiscriminator} div.acf__item#${key}`)[0];
    }

    _setItemActiveState(key, newActiveState, triggerUpdateEvent=true) {
        let element = this._getItemHtmlElementByKey(key);
        newActiveState ? element.classList.add("active") : element.classList.remove("active");
        this._itemsMap.get(key).active = newActiveState;

        if (newActiveState) {
            this._selectedMap.set(key, true);
        }
        else {
            if (this._selectedMap.has(key)) {
                this._selectedMap.delete(key);
            }
        }

        if (triggerUpdateEvent) {
            this._triggerSelectionUpdateEvent(key);
        }
    }

    _toggleItemActiveState(key, triggerUpdateEvent=true) {
        let element = this._getItemHtmlElementByKey(key);
        element.classList.toggle("active");
        this._itemsMap.get(key).active = !this._itemsMap.get(key).active;

        if (this._selectedMap.has(key) === false) {
            this._selectedMap.set(key, true);
        }
        else {
            this._selectedMap.delete(key);
        }

        if (triggerUpdateEvent) {
            this._triggerSelectionUpdateEvent(key);
        }
    }

    _searchItems(items, searchText) {
        if (!searchText) {
            return items;
        }

        return items.filter( (item) => item.text.toUpperCase().includes(searchText.toUpperCase()) );
    }

    _triggerSelectionUpdateEvent(keyOrKeys) {
        if (this.onSelectionUpdate !== undefined && typeof this.onSelectionUpdate === "function") {
            this.onSelectionUpdate(keyOrKeys);
        }

        this._triggerOnSubmit();
        if (this._triggerMode === this.TRIGGERMODE_ONUPDATE) {
            this._triggerOnSubmit();
        }
    }

    _triggerOnSubmit() {
        let result = [];
        this._data.forEach(function (category) {
            result.push({
                "category": category.key,
                "items": category.items,
            })
        })

        this._debounce(this._onSubmit(result));
    }

    /**
     * Get the selected items of the popover
     * @returns array of item keys
     */
    getSelected() {
        return Array.from(this._selectedMap.values());
    }
}