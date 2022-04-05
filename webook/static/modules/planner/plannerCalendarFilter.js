import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";

const REFRESH_ON_CONTEXT_UPDATE = true

class LocationFilterSet {
    constructor( slug, name, rooms, isVisible ) {
        this.slug = slug;
        this.name = name;
        this.rooms = rooms;

        this.isVisible = isVisible;
    }
}


export class PlannerCalendarFilter {
    constructor () {
        this.dialogManager = new DialogManager({
            managerName: "calendarFilter",
            dialogs: [
                [
                "roomFilterDialog",
                new Dialog({
                    dialogElementId: "roomFilterDialog",
                    triggerElementId: undefined,
                    triggerByEvent: true,
                    htmlFabricator: async (context) => {
                        return await fetch("/arrangement/planner/dialogs/room_filter?slug=" + context.location.slug)
                            .then(response => response.text());
                    },
                    onRenderedCallback: () => { this.dialogManager._makeAware(); },
                    dialogOptions: { width: 800 },
                    onSubmit: async (context, details) => {
                    }
                })
            ]]
        });

        this.locationContext = new Map();
        
        this._listenToFilterRoomOnLocations();
        this._listenToRoomFilterUpdate();
        this._listenToLocationFilterUpdate();
    }

    getFilteredSlugs() {
        var slugs = [];

        for (var [key, value] of this.locationContext) {
            if (value.isVisible === "false") {
                slugs.push(value.slug);
            }
            slugs.push(...value.rooms);
        }

        return slugs;
    }

    openRoomFilterDialog(locationSlug){
        this.dialogManager.setContext({ location: { slug: locationSlug } });
        this.dialogManager.openDialog( "roomFilterDialog" );
    }
    
    _listenToFilterRoomOnLocations () {
        $('.filterLocationBtn').on('click', (e) => {
            this.openRoomFilterDialog(e.currentTarget.value);
        })
    }

    _listenToRoomFilterUpdate() {
        document.addEventListener('plannerCalendar.filter.updateRoomFilter',    (e) => {
            var [sampleLocationSlug, _sampleRoomSlug] = e.detail.slugs[0].split("|");
            if (this.locationContext.has(sampleLocationSlug) !== true) {
                this.locationContext.set(sampleLocationSlug, new LocationFilterSet(
                    sampleLocationSlug, "", [], true
                ));
            }

            var locationFilterSet = this.locationContext.get(sampleLocationSlug);
            locationFilterSet.rooms = e.detail.slugs.map( (slugStr) => {
                return slugStr.split("|")[1];
            });
            this.locationContext.set(sampleLocationSlug, locationFilterSet);

            if (REFRESH_ON_CONTEXT_UPDATE) {
                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
            }
        });
    }

    _listenToLocationFilterUpdate() {
        document.addEventListener('plannerCalendar.filter.updateLocationFilter', (e) => {
            e.detail.slugs.forEach((slug) => {
                var [setToVisible, slug] = slug.split("|");

                if (this.locationContext.has(slug) !== true) {
                    this.locationContext.set(slug, new LocationFilterSet(slug, "", [], setToVisible));
                }
                else {
                    var locationFilterSet = this.locationContext.get(slug);
                    locationFilterSet.isVisible = setToVisible;
                    this.locationContext.set(slug, locationFilterSet);
                }
            })

            if (REFRESH_ON_CONTEXT_UPDATE) {
                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
            }
        });
    }
}