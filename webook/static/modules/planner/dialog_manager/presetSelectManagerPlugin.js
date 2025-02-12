class DialogPresetSelectManager extends DialogPluginBase {
    constructor(dialog, args) {
        super(dialog, args);

        this._setup();

        this.selectedItemsMap = new Map();
        this.activePresets = new Map();

        this.flatCheckboxToPresetMap = new Map();

        /**
         * Whenever DataTables refreshes it removes the rows (and thus our checkboxes) from
         * the document. We keep an internal store of the state of the users selection, so that we
         * can persist these changes beyond the confines of DataTables and the evolving document.
         * The solution then in this case becomes to listen for draw events on all datatables, and
         * should one be found we try to toggle all the checkboxes we know are to be considered as checked. It works out well.
         * This should ideally be rewritten sooner or later, probably to the core --- the reliance on the document for state, even as small as it is now,
         * is not, I see in retrospect, a good or sane approach. There are without doubt better, and more succinct ways to implement this.
         */
        if (this.datatables) {
            this.datatables.forEach((datatableElement) => {
                dialog.$(datatableElement).on('draw.dt', () => { // table has been paginated
                    Array.from(this.selectedItemsMap.keys()).forEach((id) => { 
                        dialog.$('#' + id).attr("checked", true);
                    });
                });
            });
        }

        // generates a map that can be used to find all presets that a checkbox is part of
        this.checkboxPresetMap = this._generateCheckboxToPresetMap();
    }

    _generateCheckboxToPresetMap() {
        const checkboxPresetMap = new Map();
        Array.from(this.presets.values()).forEach((preset) => {
            preset.ids.forEach((id) => {
                checkboxPresetMap.has(id) ? checkboxPresetMap.get(id).push(id) : checkboxPresetMap.set(id, [ preset.key ]);
            });
        });

        return checkboxPresetMap;
    }

    _setup() {
        this.checkboxes.forEach((checkboxElement) => {
            checkboxElement.addEventListener("change", (e) => {
                const id = checkboxElement.id;
                const presetsIAmPartOf = this.checkboxPresetMap.get(id);

                if (e.target.checked) {
                    this.selectedItemsMap.set(e.target.id, $(e.target).siblings("label.form-check-label").text());
                }
                else {
                    this.selectedItemsMap.delete(e.target.id);
                    
                    if (Array.isArray(presetsIAmPartOf)) {
                        presetsIAmPartOf.forEach((presetKey) => this.softUntogglePreset(presetKey));
                    }
                }
            });
        });
    }

    setSelection(bundle) {
        if (!bundle) return;

        this.activePresets.forEach((presetKey) => this.softUntogglePreset(presetKey));
        this.selectedItemsMap.keys().forEach((id) => {
            this.dialog.$('#' + id).click();
        });

        if (bundle.selectedPresets) {
            bundle.selectedPresets.forEach((presetKey) => this.activatePreset(presetKey));
        }

        if (bundle.allSelectedEntityIds) {
            bundle.allSelectedEntityIds.forEach((entity) => {
                if (!entity) return;

                let $checkboxElement = this.dialog.$('#' + entity.id);
                
                if ($checkboxElement) {
                    $checkboxElement.click();
                }

                this.selectedItemsMap.set(
                    entity.id, 
                    entity.text,
                );
            });
        }
    }

    softUntogglePreset(presetKey) {
        if (this.activePresets.has(presetKey)) {
            if (typeof this.activePresets.get(presetKey) === "object")
                this.activePresets.get(presetKey).classList.remove("border", "border-success");
            this.activePresets.delete(presetKey);
        }
    }

    activatePreset(presetKey, triggerElement=undefined) {
        const preset = this.presets.get(presetKey);

        if (this.activePresets.has(presetKey)) {
            this.softUntogglePreset(presetKey);

            preset.ids.forEach((id) => {
                let $checkboxElement = this.dialog.$('#' + id);
                if ($checkboxElement) {
                    $checkboxElement.removeAttr("checked").change();
                }

                this.selectedItemsMap.delete(id);
            });
        }
        else {
            preset.ids.forEach((id) => {
                const roomName = this.rooms.get(parseInt(id))
                let $checkboxElement = this.dialog.$('#' + id);
                if ($checkboxElement) {
                    $checkboxElement.attr("checked", true);
                }
    
                this.selectedItemsMap.set(
                    id, 
                    roomName,
                );
            });
    
            if (!triggerElement)
                triggerElement = this.dialog.$('a[d-arg-preset_key="' + presetKey + '"]')[0];
    
            if (triggerElement !== undefined)
                triggerElement.classList.add("border", "border-success");
    
            this.activePresets.set(presetKey, triggerElement !== undefined ? triggerElement : true);
        }

        if ("onPresetActivated" in this) {
            this.onPresetActivated(this.dialog, this.getSelected());
        }
        else {
            console.log("No onPresetActivated method found in DialogPresetSelectManager");
        }
    }

    uncheckAll() {
        this.checkboxes.forEach((checkboxElement) => {
            $(checkboxElement).removeAttr("checked").change();
            this.selectedItemsMap.delete(checkboxElement.id);
        });
    }

    getSelected() {
        let viewables = [];

        let results = {
            allPresets: this.presets,
            selectedPresets: Array.from(this.activePresets.keys()),
            allSelectedEntityIds: Array.from(this.selectedItemsMap, ([name, value]) => ({id: name, text: value})),
        };


        let selectedItemsMapExcludingPresetSubjects = new Map(this.selectedItemsMap);
        Array.from(this.activePresets.keys()).forEach((presetKey) => {
            const preset = this.presets.get(presetKey);
            viewables.push({ id: "preset_" + preset.key, text: preset.name });
            preset.ids.forEach( (id) => selectedItemsMapExcludingPresetSubjects.delete(id) );
        });
        viewables = viewables.concat(Array.from(selectedItemsMapExcludingPresetSubjects, ([name, value]) => ({id: name, text: value})));

        results.viewables = viewables;
        
        if (Array.from(this.checkboxes).some((checkboxElement) => checkboxElement.getAttribute("type") === "radio")) {
            results.allSelectedEntityIds = results.allSelectedEntityIds.slice(-1);
            results.viewables = results.viewables.slice(-1);
        }

        return results;
    }
}