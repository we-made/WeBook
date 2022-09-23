class DialogPresetSelectManager extends DialogPluginBase {
    constructor(dialog, args) {
        super(dialog, args);
        
        this._setup();

        this.selectedItemsMap = new Map();
        this.activePresets = new Map();

        this.flatCheckboxToPresetMap = new Map();

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
                    this.selectedItemsMap.delete(e.target.value);
                    
                    if (Array.isArray(presetsIAmPartOf)) {
                        presetsIAmPartOf.forEach((presetKey) => this.softUntogglePreset(presetKey));
                    }
                }
            });
        });
    }

    softUntogglePreset(presetKey) {
        if (this.activePresets.has(presetKey)) {
            this.activePresets.delete(presetKey);
        }
    }

    activatePreset(presetKey) {
        const preset = this.presets.get(presetKey);
        preset.ids.forEach((id) => {
            let $checkboxElement = this.dialog.$('#' + id);
            $checkboxElement.attr("checked", true);
            this.selectedItemsMap.set($checkboxElement.attr("id"), $checkboxElement.siblings("label").text());
        });
        
        this.activePresets.set(presetKey, true);
    }

    uncheckAll() {
        this.checkboxes.forEach((checkboxElement) => {
            checkboxElement.removeAttr("checked").change();
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

        return results;
    }
}