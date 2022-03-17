import { FullCalendarEvent, FullCalendarResource, FullCalendarBased, LocationStore } from "./commonLib.js";


export class LocationCalendar extends FullCalendarBased {

    constructor ( {calendarElement } = {} ) {
        super();

        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        
        this._LOCATIONS_STORE = new LocationStore(this);

        this.init()
    }

    refresh() {
        console.info("HIT REFRESH")
        this.init()
    }

    _bindPopover() {

    }

    init() {
        let _this = this;
        this._fcCalendar = new FullCalendar.Calendar(_this._calendarElement, {
            initialView: 'timeGridWeek',
            resources: async (start, end) => {
                return await _this._LOCATIONS_STORE._refreshStore(start,end)
                    .then(a => _this._LOCATIONS_STORE.getAll());
            }
        });

        this._fcCalendar.render();
    }
}