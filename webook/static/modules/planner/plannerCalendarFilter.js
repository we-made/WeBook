import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";


class LocationFilterSet {
    constructor( slug, name, rooms, isVisible ) {
        this.slug = slug;
        this.name = name;
        this.rooms = rooms;

        this.isVisible = isVisible;
    }

    getInTransferForm() {
        // target is already selected/active rooms. Source is non-active rooms.
        let target = []
        let source = []

        this.rooms.forEach(element => {
            if (element.isVisible) {
                target.push(element.name);
            }    
        });
    }
}

class RoomFilterSet {
    constructor ( slug, name, isVisible ) {
        this.slug = slug;
        this.name = name;
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
        
        this._listenToFilterRoomOnLocations();
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
}